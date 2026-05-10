import time

from parallel import parallel_map


def test_parallel_map_preserves_order():
    items = [3, 1, 4, 1, 5, 9, 2, 6]
    result = parallel_map(lambda x: x * 10, items, max_workers=4)
    assert result == [30, 10, 40, 10, 50, 90, 20, 60]


def test_parallel_map_empty_list():
    assert parallel_map(lambda x: x, [], max_workers=4) == []


def test_parallel_map_collects_failures_as_none():
    def fn(x):
        if x == 2:
            raise RuntimeError("boom")
        return x * 2

    errors = []
    result = parallel_map(
        fn,
        [1, 2, 3],
        max_workers=3,
        on_error=lambda item, exc: errors.append((item, str(exc))),
    )

    assert result == [2, None, 6]
    assert errors == [(2, "boom")]


def test_parallel_map_actually_runs_concurrently():
    # 4 items × 0.2s sleep each. Sequential ≥ 0.8s; parallel with 4 workers ≤ 0.5s.
    def slow(_):
        time.sleep(0.2)
        return True

    start = time.perf_counter()
    parallel_map(slow, [1, 2, 3, 4], max_workers=4)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.5, f"expected concurrent execution, took {elapsed:.2f}s"


def test_parallel_map_respects_cancellation():
    cancelled = {"value": False}

    def fn(x):
        time.sleep(0.05)
        return x

    def cancel_check():
        return cancelled["value"]

    # Cancel immediately — pool should not schedule any work.
    cancelled["value"] = True
    result = parallel_map(fn, [1, 2, 3], max_workers=2, is_cancelled=cancel_check)
    assert result == [None, None, None]
