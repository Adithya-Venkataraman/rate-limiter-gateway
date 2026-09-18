import os
import random
import time

from fastapi import FastAPI

app = FastAPI()

SERVER_NAME = os.environ.get("SERVER_NAME", "unknown-backend")


@app.get("/health")
def health():
    """Used by the gateway's health checker to know this server is alive."""
    return {"status": "ok", "server": SERVER_NAME}


@app.get("/work")
def do_work():
    """Simulates doing some real work, with a small random delay."""
    delay = random.uniform(0.01, 0.1)  # 10-100ms fake processing time
    time.sleep(delay)
    return {
        "server": SERVER_NAME,
        "delay_ms": round(delay * 1000, 2),
        "message": f"Request handled by {SERVER_NAME}",
    }