import os

# Comma-separated list of backend URLs, e.g. "http://backend-1:8080,http://backend-2:8080"
BACKEND_URLS = os.environ.get("BACKEND_URLS", "").split(",")
BACKEND_URLS = [url.strip() for url in BACKEND_URLS if url.strip()]

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

# How often (seconds) the gateway checks each backend's /health endpoint
HEALTH_CHECK_INTERVAL_SECONDS = float(os.environ.get("HEALTH_CHECK_INTERVAL_SECONDS", 5))

# How long (seconds) to wait for a backend to respond before considering it dead
HEALTH_CHECK_TIMEOUT_SECONDS = float(os.environ.get("HEALTH_CHECK_TIMEOUT_SECONDS", 2))
RATE_LIMIT_REQUEST=int(os.environ.get("RATE_LIMIT_REQUEST", 10))
RATE_LIMIT_WINDOW_SECONDS=int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", 10))