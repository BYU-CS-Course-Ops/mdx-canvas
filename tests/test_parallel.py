from typing import Any

from mdxcanvas.parallel import threaded_execute
from canvasapi.exceptions import RateLimitExceeded


class FakeResponse:
    def __init__(self, status_code, headers=None):
        self.status_code = status_code
        self.headers = headers or {}


def test_threaded_execute_retries_rate_limit(monkeypatch):
    calls = {'count': 0}
    sleeps = []

    def fake_sleep(seconds):
        sleeps.append(seconds)

    monkeypatch.setattr('mdxcanvas.parallel.time.sleep', fake_sleep)

    def execute(_):
        calls['count'] += 1
        if calls['count'] == 1:
            raise RateLimitExceeded('Rate Limit Exceeded. X-Rate-Limit-Remaining: 3.14159265359')

    threaded_execute(
        items=[('a', 'data')],
        execute=execute,
        max_rate_limit_retries=2,
        rate_limit_cooldown_seconds=0.5,
    )

    assert calls['count'] == 2
    assert sleeps == [0.5]


def test_threaded_execute_does_not_retry_non_rate_limit_error():
    calls = {'count': 0}

    def execute(_):
        calls['count'] += 1
        raise ValueError('boom')

    try:
        threaded_execute(
            items=[('a', 'data')],
            execute=execute,
            max_rate_limit_retries=3,
            rate_limit_cooldown_seconds=0,
        )
        assert False, 'Expected ValueError'
    except ValueError:
        pass

    assert calls['count'] == 1


def test_threaded_execute_raises_after_retry_exhaustion(monkeypatch):
    calls = {'count': 0}

    monkeypatch.setattr('mdxcanvas.parallel.time.sleep', lambda _: None)

    def execute(_):
        calls['count'] += 1
        raise RateLimitExceeded('Rate Limit Exceeded. X-Rate-Limit-Remaining: 0')

    try:
        threaded_execute(
            items=[('a', 'data')],
            execute=execute,
            max_rate_limit_retries=2,
            rate_limit_cooldown_seconds=0,
        )
        assert False, 'Expected RateLimitExceeded'
    except RateLimitExceeded:
        pass

    assert calls['count'] == 3


def test_threaded_execute_validates_retry_options():
    try:
        threaded_execute(
            items=[('a', 'data')],
            execute=lambda _: None,
            max_rate_limit_retries=-1,
        )
        assert False, 'Expected ValueError for retries'
    except ValueError:
        pass

    try:
        threaded_execute(
            items=[('a', 'data')],
            execute=lambda _: None,
            rate_limit_cooldown_seconds=-1,
        )
        assert False, 'Expected ValueError for cooldown'
    except ValueError:
        pass
