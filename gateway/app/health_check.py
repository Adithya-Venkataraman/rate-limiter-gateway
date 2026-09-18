import asyncio
import logging

import httpx

from . import config
from .load_balancer import LoadBalancer

logger = logging.getLogger("gateway.health_check")


async def health_check_loop(load_balancer: LoadBalancer):
    """
    Runs forever in the background. Every HEALTH_CHECK_INTERVAL_SECONDS,
    pings each backend's /health endpoint. Marks it healthy/unhealthy in
    the load balancer based on whether it responds in time.
    """
    async with httpx.AsyncClient(timeout=config.HEALTH_CHECK_TIMEOUT_SECONDS) as client:
        while True:
            for backend_url in load_balancer.get_status()["all_backends"]:
                await _check_one_backend(client, backend_url, load_balancer)
            await asyncio.sleep(config.HEALTH_CHECK_INTERVAL_SECONDS)


async def _check_one_backend(client: httpx.AsyncClient, backend_url: str, load_balancer: LoadBalancer):
    try:
        response = await client.get(f"{backend_url}/health")
        if response.status_code == 200:
            load_balancer.mark_healthy(backend_url)
        else:
            logger.warning(f"{backend_url} returned status {response.status_code}, marking unhealthy")
            load_balancer.mark_unhealthy(backend_url)
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        logger.warning(f"{backend_url} health check failed ({e.__class__.__name__}), marking unhealthy")
        load_balancer.mark_unhealthy(backend_url)