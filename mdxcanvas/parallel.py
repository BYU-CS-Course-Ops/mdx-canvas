"""Parallel execution utilities with dependency-aware scheduling."""

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import TypeVar, Callable, Sequence, Hashable
from canvasapi.exceptions import RateLimitExceeded, CanvasException

from .our_logging import get_logger

K = TypeVar('K', bound=Hashable)
T = TypeVar('T')


def _execute_with_rate_limit_retry(
    key: Hashable,
    data: T,
    execute: Callable[[T], None],
    max_rate_limit_retries: int,
    rate_limit_cooldown_seconds: float,
) -> None:
    logger = get_logger()

    for attempt in range(max_rate_limit_retries + 1):
        try:
            execute(data)
            return
        except (RateLimitExceeded, CanvasException) as e:
            if not isinstance(e, RateLimitExceeded) and not (
                isinstance(e, CanvasException) and 'status code 429' in e.message
            ):
                raise
            if attempt == max_rate_limit_retries:
                raise
            retry_number = attempt + 1
            logger.warning(
                f'Rate limited while processing task {key!r}; '
                f'retrying in {rate_limit_cooldown_seconds:.1f}s '
                f'({retry_number}/{max_rate_limit_retries})'
            )
            time.sleep(rate_limit_cooldown_seconds)


def threaded_execute(
    items: Sequence[tuple[K, T]],
    execute: Callable[[T], None],
    get_dependencies: Callable[[K], Sequence[K]] | None = None,
    max_rate_limit_retries: int = 3,
    rate_limit_cooldown_seconds: float = 2.0,
):
    """
    Execute tasks in parallel using a thread pool, respecting dependency ordering.

    Items are submitted to the thread pool in the order given. If get_dependencies is
    provided, each item waits for its dependency futures to complete before being submitted.
    Multiple items may share the same key; all futures for a key are tracked together.

    Args:
        items: Sequence of (key, data) pairs in desired scheduling order.
            Keys are used for dependency tracking. Data is passed to the execute callable.
        execute: Callable that processes each item's data. Called once per item.
            May be called from different threads; callers are responsible for
            thread safety of any shared state accessed within execute.
        get_dependencies: Optional callable that returns dependency keys for a given key.
            If provided, an item will not start until all its dependencies with futures
            have completed. Only keys present in items are meaningful.
        max_rate_limit_retries: Number of retry attempts after an initial
            rate-limit failure (HTTP 429 / "Rate Limit Exceeded").
        rate_limit_cooldown_seconds: Sleep duration between rate-limit retries.

    Raises:
        Any exception raised by an execute callable is propagated.
    """
    if not items:
        return

    if max_rate_limit_retries < 0:
        raise ValueError('max_rate_limit_retries must be >= 0')
    if rate_limit_cooldown_seconds < 0:
        raise ValueError('rate_limit_cooldown_seconds must be >= 0')

    futures_by_key: dict[K, list] = defaultdict(list)
    futures = []

    with ThreadPoolExecutor() as executor:
        for key, data in items:
            # Wait in the main thread for dependency futures before submitting
            if get_dependencies:
                for dep_key in get_dependencies(key):
                    for fut in futures_by_key.get(dep_key, []):
                        fut.result()

            fut = executor.submit(
                _execute_with_rate_limit_retry,
                key,
                data,
                execute,
                max_rate_limit_retries,
                rate_limit_cooldown_seconds,
            )
            futures_by_key[key].append(fut)
            futures.append(fut)

        # Wait for all remaining futures and propagate exceptions
        for fut in as_completed(futures):
            fut.result()
