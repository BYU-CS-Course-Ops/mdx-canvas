"""Parallel execution utilities with dependency-aware scheduling."""

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, TypeVar, Callable, Sequence, Hashable

K = TypeVar('K', bound=Hashable)
T = TypeVar('T')


def threaded_execute(
        items: Sequence[tuple[K, T]],
        execute: Callable[[T], None],
        get_dependencies: Optional[Callable[[K], Sequence[K]]] = None,
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

    Raises:
        Any exception raised by an execute callable is propagated.
    """
    if not items:
        return

    futures_by_key: dict[K, list] = defaultdict(list)
    futures = []

    with ThreadPoolExecutor() as executor:
        for key, data in items:
            # Wait in the main thread for dependency futures before submitting
            if get_dependencies:
                for dep_key in get_dependencies(key):
                    for fut in futures_by_key.get(dep_key, []):
                        fut.result()

            fut = executor.submit(execute, data)
            futures_by_key[key].append(fut)
            futures.append(fut)

        # Wait for all remaining futures and propagate exceptions
        for fut in as_completed(futures):
            fut.result()
