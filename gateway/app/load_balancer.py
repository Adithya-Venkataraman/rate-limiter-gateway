import threading
from typing import List, Optional


class LoadBalancer:
    """
    Simple round-robin load balancer.

    Keeps a list of all known backends and a separate set of backends
    currently considered healthy (updated by the health checker). Only
    picks from the healthy set, so dead backends are automatically
    skipped without the caller needing to know about health at all.
    """

    def __init__(self, backend_urls: List[str]):
        self._all_backends = list(backend_urls)
        self._healthy_backends = list(backend_urls)  # assume healthy until proven otherwise
        self._index = 0
        self._lock = threading.Lock()  # protects _index and _healthy_backends from races

    def get_next_backend(self) -> Optional[str]:
        """Returns the next backend URL to send a request to, or None if all are down."""
        with self._lock:
            if not self._healthy_backends:
                return None
            backend = self._healthy_backends[self._index % len(self._healthy_backends)]
            self._index += 1
            return backend

    def mark_healthy(self, backend_url: str):
        with self._lock:
            if backend_url not in self._healthy_backends and backend_url in self._all_backends:
                self._healthy_backends.append(backend_url)

    def mark_unhealthy(self, backend_url: str):
        with self._lock:
            if backend_url in self._healthy_backends:
                self._healthy_backends.remove(backend_url)

    def get_status(self) -> dict:
        with self._lock:
            return {
                "all_backends": self._all_backends,
                "healthy_backends": list(self._healthy_backends),
            }