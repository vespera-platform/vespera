from dataclasses import dataclass
import httpx
import time

TIMEOUT_S = 5.0


@dataclass
class ProbeResult:
    ok: bool
    status_code: int | None
    latency_ms: int | None
    error: str | None


def probe(url: str) -> ProbeResult:
    start = time.perf_counter()
    try:
        r = httpx.get(url, timeout=TIMEOUT_S)
        latency_ms = int((time.perf_counter() - start) * 1000)
    except httpx.TimeoutException:
        return ProbeResult(False, None, None, "timeout")
    except httpx.RequestError as e:
        return ProbeResult(False, None, None, str(e))
    return ProbeResult(r.status_code < 500, r.status_code, latency_ms, None)
