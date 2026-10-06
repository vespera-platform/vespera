import asyncio

import httpx

from vespera.checker.probe import probe

def run_probe(handler):
    async def go():
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            return await probe(client, "http://test/")

    return asyncio.run(go())

def test_is_up_200():
    r = run_probe(lambda request: httpx.Response(200))
    assert r.status_code == 200
    assert r.ok == True

def test_is_down_503():
    r = run_probe(lambda request: httpx.Response(503))
    assert r.status_code == 503
    assert r.ok == False

def test_is_down_timeout():
    def handler(request):
        raise httpx.ReadTimeout("za wolno", request=request)
    r = run_probe(handler)
    assert r.ok == False
    assert r.status_code == None
    assert r.error == "timeout"

def test_connection_error_is_down():
    def handler(request):
        raise httpx.ConnectError("odmowa", request=request)
    r = run_probe(handler)
    assert r.ok == False
    assert r.status_code == None
    assert r.error == "odmowa"

def test_is_down_500():
    r = run_probe(lambda request: httpx.Response(500))
    assert r.ok is False


def test_is_up_499():
    r = run_probe(lambda request: httpx.Response(499))
    assert r.ok is True