import os
import re
from datetime import date, timedelta
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

from .scraper import (
    Logger,
    OutputFormat,
    TargetSpec,
    create_file_logger,
    fetch_batch_news,
    fetch_stock_news,
    get_stock_results_path,
    parse_output_format,
    read_latest_published_date,
)
from .symbols import fetch_symbol_mapping

DEFAULT_FROM_DATE = "2025-12-06"
DEFAULT_TO_DATE = "2025-12-07"
DEFAULT_LIMIT: Optional[int] = None
DEFAULT_TARGETS: Optional[List[Union[str, int]]] = ["2330"]


def _slug_keyword(value: str) -> str:
    cleaned = re.sub(r"[^\w]+", "_", value.strip())
    cleaned = cleaned.strip("_")
    return cleaned or "keyword"


def _resolve_targets(
    values: List[str], symbol_map: Dict[str, str]
) -> List[TargetSpec]:
    resolved: List[TargetSpec] = []
    seen_labels: Set[str] = set()
    for raw in values:
        normalized = raw.strip()
        if not normalized:
            continue
        if normalized in symbol_map:
            search_name = symbol_map[normalized]
            symbol = normalized
            base_label = f"{search_name}_{symbol}"
        else:
            search_name = normalized
            symbol = None
            base_label = search_name
        slug_base = _slug_keyword(base_label)
        label = slug_base
        counter = 1
        while label in seen_labels:
            counter += 1
            label = f"{slug_base}_{counter}"
        seen_labels.add(label)
        resolved.append(TargetSpec(search_term=search_name, symbol=symbol, label=label))
    return resolved


def _normalize_target_values(values: Optional[List[Union[str, int]]]) -> Optional[List[str]]:
    if not values:
        return None
    normalized: List[str] = []
    for value in values:
        if value is None:
            continue
        cleaned = str(value).strip()
        if cleaned:
            normalized.append(cleaned)
    return normalized or None


def _read_existing_latest_date(
    label: str,
    folder: str,
    output_format: OutputFormat,
) -> Optional[date]:
    formats: Iterable[OutputFormat] = (
        (output_format,) + tuple(fmt for fmt in OutputFormat if fmt != output_format)
    )
    for fmt in formats:
        results_path = get_stock_results_path(folder, label, fmt)
        latest = read_latest_published_date(results_path, fmt)
        if latest:
            return latest
    return None


def _latest_target_range(
    target: TargetSpec,
    folder: str,
    fallback_from: str,
    fallback_to: str,
    output_format: OutputFormat,
) -> Tuple[str, str]:
    latest_date = _read_existing_latest_date(
        target.label, folder, output_format
    )
    today = date.today()
    today_iso = today.isoformat()
    if not latest_date:
        return fallback_from, fallback_to
    if latest_date >= today:
        return today_iso, today_iso
    next_day = latest_date + timedelta(days=1)
    return next_day.isoformat(), today_iso


# rename function? keep same name maybe but adjust doc? We'll keep but rename parameter.
def _run_latest_updates(
    targets: List[TargetSpec],
    folder: str,
    limit: Optional[int],
    fallback_from: str,
    fallback_to: str,
    output_format: OutputFormat,
    search_delay: float,
    worker_delay: float,
    worker_count: Optional[int],
    proxy: Optional[str],
    fetch_all: bool,
    logger: Logger,
) -> None:
    for target in targets:
        from_date, to_date = _latest_target_range(
            target, folder, fallback_from, fallback_to, output_format
        )
        fetch_stock_news(
            target,
            folder,
            from_date,
            to_date,
            limit,
            logger=logger,
            output_format=output_format,
            search_delay=search_delay,
            worker_delay=worker_delay,
            worker_count=worker_count,
            proxy=proxy,
            fetch_all=fetch_all,
        )


def run_collection(
    folder: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: Optional[int] = DEFAULT_LIMIT,
    targets: Optional[List[Union[str, int]]] = None,
    update_latest: bool = False,
    output_format: Optional[Union[str, OutputFormat]] = OutputFormat.PARQUET,
    search_delay: float = 0,
    worker_delay: float = 0,
    worker_count: Optional[int] = 10,
    proxy: Optional[str] = None,
    fetch_all: bool = False,
    logger: Optional[Logger] = None,
) -> None:
    fmt = parse_output_format(output_format)
    symbol_map = fetch_symbol_mapping()
    default_targets = _normalize_target_values(DEFAULT_TARGETS)
    provided_targets = _normalize_target_values(targets)
    input_values = provided_targets or default_targets or list(symbol_map.keys())
    if not input_values:
        raise ValueError("需要提供至少一個股票代碼或關鍵字")

    resolved_targets = _resolve_targets(input_values, symbol_map)
    if not resolved_targets:
        raise ValueError("需要提供至少一個有效的股票代碼或關鍵字")
    from_date = from_date or DEFAULT_FROM_DATE
    to_date = to_date or DEFAULT_TO_DATE
    effective_limit = limit
    normalized_folder = folder or os.getcwd()
    effective_logger = logger or create_file_logger(normalized_folder)

    if update_latest:
        _run_latest_updates(
            resolved_targets,
            normalized_folder,
            effective_limit,
            from_date,
            to_date,
            fmt,
            search_delay=search_delay,
            worker_delay=worker_delay,
            worker_count=worker_count,
            proxy=proxy,
            fetch_all=fetch_all,
            logger=effective_logger,
        )
    else:
        fetch_batch_news(
            resolved_targets,
            normalized_folder,
            from_date,
            to_date,
            effective_limit,
            output_format=fmt,
            search_delay=search_delay,
            worker_delay=worker_delay,
            worker_count=worker_count,
            proxy=proxy,
            fetch_all=fetch_all,
            logger=effective_logger,
        )


def run_example(
    folder: str,
    targets: Optional[List[Union[str, int]]] = None,
    output_format: Optional[Union[str, OutputFormat]] = OutputFormat.PARQUET,
    fetch_all: bool = False,
    logger: Optional[Logger] = None,
) -> None:
    """用固定日期範例直接呼叫，讓使用者不用記得所有選項。"""
    run_collection(
        folder=folder,
        from_date=DEFAULT_FROM_DATE,
        to_date=DEFAULT_TO_DATE,
        limit=DEFAULT_LIMIT,
        targets=targets,
        update_latest=False,
        fetch_all=fetch_all,
        search_delay=0,
        worker_delay=0,
        proxy=None,
        logger=logger,
    )


def collect_stock_news(
    targets: List[TargetSpec],
    folder: str,
    from_date: str,
    to_date: str,
    limit: Optional[int] = DEFAULT_LIMIT,
    output_format: OutputFormat = OutputFormat.PARQUET,
    search_delay: float = 0,
    worker_delay: float = 0,
    worker_count: Optional[int] = None,
    proxy: Optional[str] = None,
    logger: Optional[Logger] = None,
    fetch_all: bool = False,
    ) -> List[Tuple[TargetSpec, Optional[str]]]:
    """Expose the batch collector for Python callers with format control."""
    return fetch_batch_news(
        targets,
        folder,
        from_date,
        to_date,
        limit,
        output_format=output_format,
        search_delay=search_delay,
        worker_delay=worker_delay,
        proxy=proxy,
        worker_count=worker_count,
        logger=logger,
        fetch_all=fetch_all,
    )
