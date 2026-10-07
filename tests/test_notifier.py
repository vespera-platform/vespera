import asyncio

import httpx

from vespera.notifier.main import send_with_retry


def run_with_statuses(statuses):
    codes = iter(statuses)
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(next(codes))

    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as c:
            return await send_with_retry(c, "http://hook", {"id": "e1"}, delays=(0, 0, 0))

    return asyncio.run(go()), len(calls)


def test_succeeds_on_third_attempt():
    ok, n = run_with_statuses([500, 500, 200])
    assert ok is True
    assert n == 3


def test_gives_up_after_all_attempts():
    ok, n = run_with_statuses([500, 500, 500, 500])
    assert ok is False
    assert n == 4