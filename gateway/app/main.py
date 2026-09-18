import asyncio
import logging

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from . import config
from .health_check import health_check_loop
from .load_balancer import LoadBalancer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway.main")

app = FastAPI()
load_balancer = LoadBalancer(config.BACKEND_URLS)

# Reused across requests instead of opening a new connection every time
http_client: httpx.AsyncClient | None = None


@app.on_event("startup")
async def startup():
    global http_client
    http_client = httpx.AsyncClient(timeout=5.0)
    # Run health checks forever in the background, without blocking requests
    asyncio.create_task(health_check_loop(load_balancer))
    logger.info(f"Gateway starting. Known backends: {config.BACKEND_URLS}")


@app.on_event("shutdown")
async def shutdown():
    if http_client:
        await http_client.aclose()


@app.get("/status")
def status():
    """Shows which backends are currently considered healthy."""
    return load_balancer.get_status()


@app.get("/work")
async def proxy_work():
    """
    Main endpoint clients hit. Picks a healthy backend (round-robin) and
    forwards the request to it. This is the load-balancing path — rate
    limiting will be added in front of this in Week 2.
    """
    backend_url = load_balancer.get_next_backend()

    if backend_url is None:
        raise HTTPException(status_code=503, detail="No healthy backends available")

    try:
        response = await http_client.get(f"{backend_url}/work")
        return JSONResponse(status_code=response.status_code, content=response.json())
    except (httpx.ConnectError, httpx.TimeoutException):
        # Backend died between the last health check and now — mark it
        # unhealthy immediately instead of waiting for the next check cycle.
        load_balancer.mark_unhealthy(backend_url)
        raise HTTPException(status_code=502, detail=f"Backend {backend_url} unreachable")