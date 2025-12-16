from __future__ import annotations

import os
from typing import List, Optional, Sequence, Union

from GetStockNews import Logger, OutputFormat, run_collection


def run_get_stock_news(
    folder: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: Optional[int] = None,
    targets: Optional[Sequence[Union[str, int]]] = None,
    update_latest: bool = False,
    output_format: Optional[Union[str, OutputFormat]] = OutputFormat.PARQUET,
    search_delay: float = 0,
    worker_delay: float = 0,
    worker_count: Optional[int] = None,
    proxy: Optional[str] = None,
    fetch_all: bool = False,
    logger: Optional[Logger] = None,
) -> None:
    """Run the stock-news collection with the defaults used by the CLI."""
    resolved_targets: Optional[List[Union[str, int]]] = None
    if targets:
        resolved_targets = list(targets)
    run_collection(
        folder=folder or os.getcwd(),
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        targets=resolved_targets,
        update_latest=update_latest,
        output_format=output_format,
        search_delay=search_delay,
        worker_delay=worker_delay,
        worker_count=worker_count,
        proxy=proxy,
        fetch_all=fetch_all,
        logger=logger,
    )
