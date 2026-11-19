import os
import sys
import time

import httpx


def step(name: str, ok: bool, detail: str = "") -> bool:
    if ok:
        print(f"OK: {name}")
    else:
        print(f"FAIL: {name}: {detail}")
    return ok


def main() -> int:
    base_url = os.environ["POSTDEPLOY_BASE_URL"]
    target_url = os.environ["POSTDEPLOY_TARGET_URL"]
    expected = os.environ["POSTDEPLOY_EXPECTED_VERSION"]
    timeout = int(os.environ.get("POSTDEPLOY_TIMEOUT", "60"))

    with httpx.Client(
        base_url=base_url, timeout=5.0, limits=httpx.Limits(max_keepalive_connections=0)
    ) as client:
        r = client.get("/readyz")
        if not step("readyz", r.status_code == 200, f"status {r.status_code}"):
            return 1

        v = client.get("/version")
        got = v.json()["version"]
        if not step("version", got == expected, f"jest {got}, oczekiwano {expected}"):
            return 1

        r = client.post(
            "/targets",
            json={
                "name": f"postdeploy-{int(time.time())}",
                "url": target_url,
            },
        )
        if not step("create target", r.status_code == 201, f"status {r.status_code}"):
            return 1
        target_id = r.json()["id"]

        try:
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                r = client.get(f"/targets/{target_id}/checks")
                checks = r.json()
                if checks and checks[0]["ok"]:
                    step("target UP", True)
                    break
                time.sleep(5)
            else:
                step("target UP", False, f"brak UP w {timeout} s")
                return 1
        finally:
            r = client.delete(f"/targets/{target_id}")
            step("delete target", r.status_code == 204, f"status {r.status_code}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
