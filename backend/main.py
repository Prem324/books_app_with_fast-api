import os
import asyncio
import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlalchemy import text

import models
from database import engine

from routers import users, books


models.Base.metadata.create_all(bind=engine)

# Keep existing databases compatible when adding new optional columns.
with engine.begin() as conn:
    conn.execute(text("ALTER TABLE books ADD COLUMN IF NOT EXISTS year INTEGER"))
    conn.execute(text("ALTER TABLE books ADD COLUMN IF NOT EXISTS isbn VARCHAR(32)"))
    conn.execute(text("ALTER TABLE books ADD COLUMN IF NOT EXISTS description VARCHAR"))
    conn.execute(text("ALTER TABLE books ADD COLUMN IF NOT EXISTS image_url VARCHAR"))
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR"))
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_code_hash VARCHAR"))
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_code_expires_at TIMESTAMP"))

app = FastAPI()
frontend_origins = os.getenv("FRONTEND_ORIGINS", "*")
allow_origins = [origin.strip() for origin in frontend_origins.split(",") if origin.strip()]
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("books_api")
rate_limit_store: dict[str, list[float]] = {}
rate_lock = asyncio.Lock()


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if RATE_LIMIT_PER_MIN <= 0:
        return await call_next(request)

    now = time.time()
    key = request.client.host if request.client else "unknown"
    async with rate_lock:
        window = rate_limit_store.get(key, [])
        window = [ts for ts in window if now - ts < 60]
        if len(window) >= RATE_LIMIT_PER_MIN:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        window.append(now)
        rate_limit_store[key] = window

    return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms) ip=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request.client.host if request.client else "unknown",
    )
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(books.router)


@app.get("/")
def home():
    return {"msg": "Books API Running"}
