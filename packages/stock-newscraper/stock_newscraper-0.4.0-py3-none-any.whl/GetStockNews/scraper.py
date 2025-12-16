import csv
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Set, Tuple, Union
from urllib.parse import urlparse

import dateparser
try:
    import pandas as pd
except ImportError:
    pd = None
from datetime import date, datetime, timedelta

from pygooglenews import GoogleNews
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

NEWS_DIRECTORY_NAME = "news_scraper_results"
AD_MARKERS = ("ad", "advert", "promoted", "sponsored", "廣告", "贊助")
RESULT_COLUMNS = [
    "search_term",
    "symbol",
    "published",
    "resolved_link",
    "title",
    "content",
]
MAX_STEP_TIMEOUT_MS = 7_000
ADAPTIVE_SPLIT_THRESHOLD = 90
GOOGLE_RESULTS_PAGE_LIMIT = 85  # Google News search returns at most ~85 entries per page

Logger = Callable[[str], None]

class TargetSpec(NamedTuple):
    search_term: str
    symbol: Optional[str]
    label: str


def ensure_directory(target_path: str) -> None:
    directory = os.path.dirname(target_path)
    os.makedirs(directory, exist_ok=True)


def default_logger(message: str) -> None:
    print(message)


def create_file_logger(folder: str, filename: str = "news_scraper.log") -> Logger:
    normalized_folder = folder or os.getcwd()
    log_path = os.path.join(normalized_folder, filename)
    ensure_directory(log_path)
    lock = threading.Lock()

    def logger(message: str) -> None:
        timestamp = datetime.utcnow().isoformat()
        line = f"[{timestamp}] {message}"
        print(message)
        try:
            with lock:
                with open(log_path, "a", encoding="utf-8") as handle:
                    handle.write(line + "\n")
        except Exception:
            pass

    return logger


class OutputFormat(Enum):
    CSV = "csv"
    PARQUET = "parquet"


OUTPUT_EXTENSIONS = {
    OutputFormat.CSV: ".csv",
    OutputFormat.PARQUET: ".parquet",
}


def parse_output_format(value: Optional[Union[str, OutputFormat]]) -> OutputFormat:
    if isinstance(value, OutputFormat):
        return value
    if not value:
        return OutputFormat.PARQUET
    normalized = value.strip().lower()
    if normalized in (OutputFormat.PARQUET.value, "pq"):
        return OutputFormat.PARQUET
    if normalized == OutputFormat.CSV.value:
        return OutputFormat.CSV
    raise ValueError(f"不支援的輸出格式：{value}")


def normalize_date_input(value: str, fallback: str) -> str:
    if not value:
        return fallback
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        parsed = dateparser.parse(value)
        if parsed:
            return parsed.date().isoformat()
    return fallback


def build_query(keyword: str, start_date: date, end_date: date) -> str:
    after = start_date.isoformat()
    before = (end_date + timedelta(days=1)).isoformat()
    return f'"{keyword}" after:{after} before:{before}'


def _resolve_google_link(page, link: str, timeout_ms: int = MAX_STEP_TIMEOUT_MS) -> str:
    try:
        page.goto(link, wait_until="domcontentloaded", timeout=timeout_ms)
    except PlaywrightTimeoutError:
        return page.url

    try:
        page.wait_for_load_state("networkidle", timeout=timeout_ms)
    except PlaywrightTimeoutError:
        pass

    return page.url


def _truncate_text(text: str, max_length: int = 2000) -> str:
    trimmed = text.strip()
    if len(trimmed) <= max_length:
        return trimmed
    return trimmed[:max_length] + "..."


def _contains_keyword(text: str, keyword_lower: str, min_length: int) -> bool:
    cleaned = (text or "").strip()
    return len(cleaned) >= min_length and keyword_lower in cleaned.lower()


def _strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value or "").strip()


def _extract_keyword_content(
    page,
    keyword: str,
    summary_snippet: str = "",
    min_length: int = 100,
    final_url: Optional[str] = None,
) -> str:
    keyword_lower = keyword.lower()
    selectors = [
        "article.article-content",
        "article#mainarticle",
        "div.article_content",
        "div.article-body",
        "div.article-content__text",
        "div#article-body",
        "div.news-body",
        "div#news-body",
        "section.article-content__editor",
        "section.article-content__paragraph",
        "div.story-content",
        "div.article-body__content",
        "div.article-main",
        "div.main-content",
        "div.story-body",
        "div.text-body",
    ]

    for selector in selectors:
        block = page.query_selector(selector)
        if block:
            text = block.inner_text() or ""
            if _contains_keyword(text, keyword_lower, min_length):
                return _truncate_text(text)

    general_selectors = ["article", "main", "section", "div"]
    paragraph_texts: List[str] = [
        paragraph.inner_text() or "" for paragraph in page.query_selector_all("p")
    ]
    domain_candidate_selectors = [
        "[class*='article']",
        "[id*='article']",
        "[class*='content']",
        "[id*='content']",
    ]

    candidates: List[str] = []
    candidates.extend(paragraph_texts)
    for selector in general_selectors:
        candidates.extend(
            block.inner_text() or "" for block in page.query_selector_all(selector)
        )
    for selector in domain_candidate_selectors:
        candidates.extend(
            block.inner_text() or "" for block in page.query_selector_all(selector)
        )

    keyword_matches: List[str] = []
    fallback_matches: List[str] = []
    for text in candidates:
        cleaned = text.strip()
        if not cleaned:
            continue
        if _contains_keyword(cleaned, keyword_lower, min_length):
            keyword_matches.append(cleaned)
        elif len(cleaned) >= min_length:
            fallback_matches.append(cleaned)

    if keyword_matches:
        longest = max(keyword_matches, key=len)
        return _truncate_text(longest)
    if fallback_matches:
        longest = max(fallback_matches, key=len)
        return _truncate_text(longest)

    summary_text = _strip_html(summary_snippet)
    if summary_text and len(summary_text) >= min_length:
        return _truncate_text(summary_text)
    return ""


def _fetch_search_entries(
    query: str,
    limit: Optional[int],
    logger: Logger,
    delay_seconds: float = 0,
    fetch_all: bool = False,
    keyword_filter: Optional[str] = None,
) -> Tuple[List[dict], int]:
    if limit is not None and limit <= 0 and not fetch_all:
        logger("⚠️ limit 不得小於等於 0，已跳過搜尋。")
        return []

    if delay_seconds and delay_seconds > 0:
        time.sleep(delay_seconds)

    logger(f"🔍 查詢 Google News：{query}")
    try:
        gn = GoogleNews(country="TW", lang="zh-Hant")
        search_result = gn.search(query=query)
        entries = search_result.get("entries", [])
    except Exception as exc:
        logger(f"❌ Google News 查詢失敗：{exc}")
        return []

    if not entries:
        logger("⚠️ 查無符合條件的新聞條目。")
        return []

    filtered = [entry for entry in entries if _remove_ad_and_promo(entry)]
    if not filtered:
        logger("⚠️ 目前結果中只有廣告或贊助內容，已排除。")
        return [], 0
    if keyword_filter:
        key_lower = keyword_filter.lower()
        before_keyword = len(filtered)
        filtered = [entry for entry in filtered if key_lower in (entry.get("title") or "").lower()]
        logger(f"🧾 剩餘 {len(filtered)} 筆標題含 '{keyword_filter}' (原始 {before_keyword} 筆)。")
        if not filtered:
            logger("⚠️ 標題過濾後無符合的新聞條目。")
            return [], before_keyword
    else:
        before_keyword = len(filtered)

    logger(
        f"✅ 抓到 {len(filtered)} 筆候選文章，將依 limit={limit if limit is not None else 'default'} 處理。"
    )
    if fetch_all or limit is None:
        return filtered, before_keyword
    return filtered[:limit], before_keyword


def _adaptive_fetch_entries(
    keyword: str,
    start_date: date,
    end_date: date,
    logger: Logger,
    search_delay: float,
    fetch_all: bool,
    seen_links: Set[str],
    remaining_limit: Optional[int] = None,
) -> List[dict]:
    collected: List[dict] = []
    intervals: List[Tuple[date, date]] = [(start_date, end_date)]
    limit_remaining = remaining_limit

    while intervals:
        if limit_remaining == 0:
            break
        current_start, current_end = intervals.pop()
        if current_start > current_end:
            continue

        while True:
            span_days = (current_end - current_start).days
            available = limit_remaining if limit_remaining is not None else None
            needs_full_fetch = fetch_all or available is None or available > ADAPTIVE_SPLIT_THRESHOLD
            request_limit = None if needs_full_fetch else available

            entries, candidate_count = _fetch_search_entries(
                build_query(keyword, current_start, current_end),
                request_limit,
                logger,
                search_delay,
                fetch_all=needs_full_fetch,
                keyword_filter=keyword,
            )
            if not entries:
                break

            local_links: Set[str] = set()
            unique_entries: List[dict] = []
            for entry in entries:
                link = entry.get("link")
                if not link or link in seen_links or link in local_links:
                    continue
                local_links.add(link)
                unique_entries.append(entry)

            should_split = (
                span_days >= 1
                and candidate_count >= min(ADAPTIVE_SPLIT_THRESHOLD, GOOGLE_RESULTS_PAGE_LIMIT)
                and (fetch_all or available is None or available > ADAPTIVE_SPLIT_THRESHOLD)
            )
            if should_split:
                mid_offset = span_days // 2
                mid_date = current_start + timedelta(days=mid_offset)
                intervals.append((mid_date + timedelta(days=1), current_end))
                current_end = mid_date
                continue

            for entry in unique_entries:
                if limit_remaining == 0:
                    break
                collected.append(entry)
                link = entry.get("link")
                if link:
                    seen_links.add(link)
                if limit_remaining is not None:
                    limit_remaining -= 1
            break

        if limit_remaining == 0:
            break

    return collected


def _remove_ad_and_promo(entry: dict) -> bool:
    title = entry.get("title", "")
    return not any(marker in title.lower() for marker in AD_MARKERS)


def _process_entry(
    entry: dict,
    entry_id: int,
    keyword: str,
    logger: Logger,
    worker_delay: float,
    proxy: Optional[str],
) -> Optional[dict]:
    link = entry.get("link")
    if not link:
        logger(f"[entry-{entry_id}] 無效連結，跳過")
        return None

    worker_id = threading.get_ident()
    logger(f"[entry-{entry_id}] worker {worker_id} 啟動，目標 {link}")
    try:
        with sync_playwright() as playwright:
            with playwright.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--no-sandbox", "--disable-setuid-sandbox"],
            ) as browser:
                context = (
                    browser.new_context(proxy={"server": proxy})
                    if proxy
                    else browser.new_context()
                )
                try:
                    page = context.new_page()
                    page.set_default_navigation_timeout(MAX_STEP_TIMEOUT_MS)
                    page.set_default_timeout(MAX_STEP_TIMEOUT_MS)
                    if worker_delay and worker_delay > 0:
                        time.sleep(worker_delay)

                    final_url = _resolve_google_link(page, link)
                    title = entry.get("title", "無標題")
                    published = entry.get("published", "")
                    summary = entry.get("summary", "")
                    try:
                        content = _extract_keyword_content(
                            page,
                            keyword,
                            summary,
                            final_url=final_url,
                        )
                    except Exception as exc:
                        logger(
                            f"[entry-{entry_id}] ⚠️ 內容抽取失敗 ({exc})，再嘗試一次。"
                        )
                        time.sleep(0.5)
                        try:
                            page.wait_for_load_state("networkidle", timeout=MAX_STEP_TIMEOUT_MS)
                        except PlaywrightTimeoutError:
                            pass
                        content = _extract_keyword_content(
                            page,
                            keyword,
                            summary,
                            final_url=final_url,
                        )
                    target_host = urlparse(final_url).netloc or "unknown"

                    logger(f"[entry-{entry_id}] {published[:10]} | {title}")
                    logger(f"   ↪ {final_url} ({target_host})")

                    if not content:
                        logger("   ⚠️ 未找到符合條件的區塊，仍將紀錄。")
                        content = "未找到符合條件的區塊"
                    else:
                        preview = content[:120].replace("\n", " ")
                        logger(f"   ✔ 內容長度 {len(content)}，前綴：{preview}...")

                    return {
                        "published": published,
                        "resolved_link": final_url,
                        "title": title,
                        "content": content,
                    }
                finally:
                    context.close()
    except Exception as exc:
        logger(f"[entry-{entry_id}] ⛔️ Playwright 失敗：{exc}")
    return None


def _resolve_entries(
    entries: List[dict],
    keyword: str,
    logger: Logger,
    worker_delay: float = 0,
    proxy: Optional[str] = None,
    worker_count: Optional[int] = None,
) -> List[dict]:
    if not entries:
        return []

    available_workers = os.cpu_count() or 4
    desired_workers = available_workers * 2 if worker_count is None else worker_count
    max_workers = min(len(entries), desired_workers) or 1
    user_label = worker_count if worker_count is not None else "auto"
    logger(
        f"🧠 準備啟動最多 {max_workers} 個 worker（條目數：{len(entries)}，cpu：{available_workers}，user={user_label}）"
    )

    results: List[dict] = []
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for idx, entry in enumerate(entries, start=1):
            futures.append(
                executor.submit(
                    _process_entry,
                    entry,
                    idx,
                    keyword,
                    logger,
                    worker_delay,
                    proxy,
                )
            )
            if worker_delay and worker_delay > 0 and idx < len(entries):
                time.sleep(worker_delay)

        for future in as_completed(futures):
            try:
                row = future.result()
            except Exception as exc:
                logger(f"⛔️ worker 執行失敗：{exc}")
                continue
            if row:
                results.append(row)
    return results


def _parse_date_value(value: object) -> Optional[date]:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
        try:
            parsed = dateparser.parse(value)
        except Exception:
            return None
        if parsed:
            return parsed.date()
    return None


def _ensure_pandas() -> None:
    if pd is None:
        raise ImportError("pandas is required for parquet output; install pandas and pyarrow")


def get_stock_results_path(
    base_folder: str,
    label: str,
    output_format: OutputFormat = OutputFormat.PARQUET,
) -> str:
    normalized_folder = base_folder or os.getcwd()
    directory = os.path.join(normalized_folder, NEWS_DIRECTORY_NAME)
    extension = OUTPUT_EXTENSIONS[output_format]
    safe_label = _sanitize_label(label)
    filename = f"{safe_label}{extension}"
    return os.path.join(directory, filename)


def _sanitize_label(value: str) -> str:
    trimmed = value.strip()
    if not trimmed:
        return "target"
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", trimmed)
    return sanitized


def _read_latest_from_csv(path: str) -> Optional[date]:
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            dates = [_parse_date_value(row.get("published")) for row in reader]
    except Exception:
        return None
    values = [value for value in dates if value]
    return max(values) if values else None


def _read_latest_from_parquet(path: str) -> Optional[date]:
    _ensure_pandas()
    try:
        df = pd.read_parquet(path, columns=["published"])
    except Exception:
        return None
    if df.empty:
        return None
    values = df["published"].dropna().tolist()
    dates = [_parse_date_value(value) for value in values]
    filtered = [value for value in dates if value]
    return max(filtered) if filtered else None


def read_latest_published_date(
    results_path: str, output_format: OutputFormat = OutputFormat.PARQUET
) -> Optional[date]:
    if not os.path.isfile(results_path):
        return None
    if output_format == OutputFormat.CSV:
        return _read_latest_from_csv(results_path)
    return _read_latest_from_parquet(results_path)


def _write_results_to_csv(rows: List[dict], csv_path: str) -> None:
    ensure_directory(csv_path)
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=RESULT_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def _write_results_to_parquet(rows: List[dict], parquet_path: str) -> None:
    _ensure_pandas()
    ensure_directory(parquet_path)
    df = pd.DataFrame(rows)
    if os.path.isfile(parquet_path):
        try:
            existing = pd.read_parquet(parquet_path)
            df = pd.concat([existing, df], ignore_index=True)
        except Exception:
            pass
    df = _reorder_dataframe_columns(df)
    df.to_parquet(parquet_path, index=False)


def _write_rows(rows: List[dict], path: str, output_format: OutputFormat) -> None:
    if output_format == OutputFormat.CSV:
        _write_results_to_csv(rows, path)
        return
    _write_results_to_parquet(rows, path)


def _reorder_dataframe_columns(df):
    if df.empty:
        return df
    preferred = [col for col in RESULT_COLUMNS if col in df.columns]
    others = [col for col in df.columns if col not in preferred]
    if preferred + others == list(df.columns):
        return df
    return df[preferred + others]


def _collect_existing_links(path: str, output_format: OutputFormat) -> Set[str]:
    if not os.path.isfile(path):
        return set()
    links: Set[str] = set()
    try:
        if output_format == OutputFormat.CSV:
            with open(path, newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    resolved = row.get("resolved_link")
                    if resolved:
                        links.add(resolved)
        else:
            _ensure_pandas()
            df = pd.read_parquet(path, columns=["resolved_link"])
            if not df.empty:
                for value in df["resolved_link"].dropna().astype(str):
                    links.add(value)
    except Exception:
        pass
    return links


def fetch_stock_news(
    target: TargetSpec,
    base_folder: str,
    from_date: str,
    to_date: str,
    limit: Optional[int] = None,
    logger: Logger = default_logger,
    output_format: OutputFormat = OutputFormat.PARQUET,
    search_delay: float = 0,
    worker_delay: float = 0,
    worker_count: Optional[int] = None,
    proxy: Optional[str] = None,
    fetch_all: bool = False,
) -> Optional[str]:
    if not target.search_term:
        raise ValueError("search_term is required")

    from_date = normalize_date_input(from_date, from_date)
    to_date = normalize_date_input(to_date, to_date)
    from_date_obj = _parse_date_value(from_date)
    to_date_obj = _parse_date_value(to_date)
    if from_date_obj is None or to_date_obj is None:
        raise ValueError("from_date/to_date 需為可解析的日期")
    if from_date_obj > to_date_obj:
        raise ValueError("from_date cannot be later than to_date")

    symbol_label = target.symbol or "keyword"
    logger(
        f"=== {target.search_term} ({symbol_label}) {from_date_obj.isoformat()} ~ {to_date_obj.isoformat()} ==="
    )
    seen_links: Set[str] = set()
    entries = _adaptive_fetch_entries(
        target.search_term,
        from_date_obj,
        to_date_obj,
        logger,
        search_delay,
        fetch_all,
        seen_links,
        limit,
    )
    if not entries:
        return None

    resolved_rows = _resolve_entries(
        entries, target.search_term, logger, worker_delay, proxy, worker_count
    )
    if not resolved_rows:
        return None

    results_path = get_stock_results_path(base_folder, target.label, output_format)
    existing_links = _collect_existing_links(results_path, output_format)
    observed_links: Set[str] = set()
    filtered_rows: List[dict] = []
    search_lower = target.search_term.lower()
    for row in resolved_rows:
        resolved_link = row.get("resolved_link")
        if not resolved_link or resolved_link in existing_links or resolved_link in observed_links:
            continue
        observed_links.add(resolved_link)
        title = row.get("title", "")
        if search_lower and search_lower not in title.lower():
            logger(f"   ⚠️ 標題未包含 {target.search_term}，跳過。")
            continue
        row["search_term"] = target.search_term
        row["symbol"] = target.symbol or ""
        filtered_rows.append(row)

    if not filtered_rows:
        logger("⚠️ 無新的文章可寫入。")
        return results_path

    _write_rows(filtered_rows, results_path, output_format)
    logger(f"✅ 已寫入 {len(filtered_rows)} 筆至 {results_path}")
    return results_path


def fetch_batch_news(
    targets: List[TargetSpec],
    base_folder: str,
    from_date: str,
    to_date: str,
    limit: Optional[int] = None,
    logger: Logger = default_logger,
    output_format: OutputFormat = OutputFormat.PARQUET,
    search_delay: float = 0,
    worker_delay: float = 0,
    worker_count: Optional[int] = None,
    proxy: Optional[str] = None,
    fetch_all: bool = False,
) -> List[Tuple[TargetSpec, Optional[str]]]:
    if not targets:
        raise ValueError("至少需要一個目標規格")

    normalized_folder = base_folder or os.getcwd()
    results: List[Tuple[TargetSpec, Optional[str]]] = []
    for target in targets:
        try:
            results_path = fetch_stock_news(
                target,
                normalized_folder,
                from_date,
                to_date,
                limit,
                logger,
                output_format,
                search_delay=search_delay,
                worker_delay=worker_delay,
                worker_count=worker_count,
                proxy=proxy,
                fetch_all=fetch_all,
            )
        except Exception as exc:
            logger(f"❌ {target.search_term} ({target.symbol or 'keyword'}) 擷取失敗：{exc}")
            results_path = None
        results.append((target, results_path))
    return results
