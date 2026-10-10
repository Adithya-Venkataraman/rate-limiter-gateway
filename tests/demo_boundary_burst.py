import time
import httpx

URL = "http://localhost:8000/work"
LIMIT = 10
WINDOW = 10  # must match RATE_LIMIT_WINDOW_SECONDS
HEADERS = {"X-API-Key": f"burst-{int(time.time())}"}  # fresh client each run


def burst(n):
    ok = 0
    for _ in range(n):
        r = httpx.get(URL, headers=HEADERS)
        ok += r.status_code == 200
    return ok


# Wait until ~1.5s before the next window boundary
boundary = (time.time() // WINDOW + 1) * WINDOW
time.sleep(max(0, boundary - 1.5 - time.time()))

first = burst(LIMIT)  # lands at the end of window N

# Wait until just after the boundary
time.sleep(max(0, boundary + 0.1 - time.time()))

second = burst(LIMIT)  # lands at the start of window N+1

print(f"Allowed before boundary: {first}")
print(f"Allowed after boundary:  {second}")
print(f"Total in ~2 seconds:     {first + second} (limit is {LIMIT} per {WINDOW}s)")