"""Concurrency helpers for I/O-bound pipeline stages.

The video-generation pipeline runs three loops that hit the network once per
item and don't depend on each other within the loop: Pexels search per term,
video download per URL, and TTS per sentence. We parallelize those with a
shared thread pool helper that preserves input order, propagates cancellation,
and never raises on individual failures (callers decide what missing entries
mean).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Optional, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def parallel_map(
    fn: Callable[[T], R],
    items: List[T],
    *,
    max_workers: int = 8,
    on_error: Optional[Callable[[T, Exception], None]] = None,
    is_cancelled: Optional[Callable[[], bool]] = None,
) -> List[Optional[R]]:
    """Run ``fn`` over ``items`` concurrently, preserving input order.

    Failures are caught and converted to ``None`` in the result list (the
    optional ``on_error`` callback is invoked with the offending item and the
    exception). If ``is_cancelled()`` returns truthy, in-flight work is allowed
    to finish but no new tasks are scheduled and the partial results are
    returned with ``None`` in the unfinished slots.
    """
    if not items:
        return []

    workers = max(1, min(max_workers, len(items)))
    results: List[Optional[R]] = [None] * len(items)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_to_index = {}
        for index, item in enumerate(items):
            if is_cancelled and is_cancelled():
                break
            future_to_index[pool.submit(fn, item)] = (index, item)

        for future in list(future_to_index.keys()):
            index, item = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as exc:
                if on_error is not None:
                    on_error(item, exc)

    return results
