import os
import re
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Must run before any module that reads configuration at import time.
load_dotenv()

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import SQLAlchemyError

from logging_config import logger
from database.db import check_connection, init_models

from routes.user import router as user_router
from routes.conference import router as conference_router
from routes.student_dashboard import router as student_router
from routes.reviewer import router as reviewer_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Prepare the database without letting a failure stop the process.

    Creating tables here rather than at import time means an unreachable
    database produces a running service with failing data endpoints, instead
    of a crash loop that never binds a port and never answers at all.
    """
    logger.info("CRAB.AI backend starting")
    try:
        init_models()
        logger.info("Database ready")
    except Exception as exc:  # noqa: BLE001 - startup must not abort
        logger.error("Database unavailable at startup: %s", exc)
        logger.error("Service will start; data endpoints return 503 until it recovers")
    yield
    logger.info("CRAB.AI backend shutting down")


app = FastAPI(title="CRAB.AI Backend", lifespan=lifespan)

# Client libraries put credentials in URLs and messages. Returning an exception
# verbatim to the browser therefore leaks them: the Gemini client embeds the API
# key as a query parameter, so an upstream 400 would hand the key to any caller
# who can trigger an error.
_SECRET_PATTERNS = [
    (re.compile(r"([?&](?:key|api_key|apikey|access_token|token)=)[^&\s\"\']+", re.I), r"\1[REDACTED]"),
    (re.compile(r"(Bearer\s+)[A-Za-z0-9._\-]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"\b(postgresql?://[^:]+:)[^@]+(@)", re.I), r"\1[REDACTED]\2"),
]


def _redact(message: str) -> str:
    for pattern, replacement in _SECRET_PATTERNS:
        message = pattern.sub(replacement, message)
    return message


@app.middleware("http")
async def catch_unhandled_errors(request: Request, call_next):
    """Turn an unhandled exception into a JSON 500 that still carries CORS headers.

    Starlette's built-in ServerErrorMiddleware sits outside the CORS middleware,
    so a crash inside a route produces a bare 500 with no Access-Control-Allow-Origin
    header. The browser then reports it as a CORS failure, which sends you looking
    at CORS configuration when the real fault is an exception in the handler.
    """
    try:
        return await call_next(request)
    except Exception as exc:  # noqa: BLE001 - deliberately broad
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": _redact(f"{type(exc).__name__}: {exc}"),
            },
        )


# CORS. Set ALLOWED_ORIGINS to a comma-separated list to restrict it.
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # A wildcard origin cannot be combined with credentials per the CORS spec;
    # browsers reject the response outright.
    allow_credentials=origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(conference_router, prefix="/conference", tags=["conference"])
app.include_router(reviewer_router, prefix="/reviewer", tags=["reviewer"])
app.include_router(student_router, prefix="/api", tags=["student"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """A database outage is a 503, not a 500.

    Sessions connect lazily, so a dead database surfaces inside the route
    rather than in the dependency. Without this, every data endpoint would
    report an opaque Internal Server Error.
    """
    logger.error("Database error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


@app.get("/health", tags=["health"])
def health_check():
    """Liveness. Deliberately does not touch the database."""
    return {"status": "healthy"}


@app.get("/health/gemini", tags=["health"])
def health_gemini():
    """Report what the process sees for GEMINI_API_KEY, and whether it works.

    Reports shape only, never the value: whether it is set, its length, its
    first four characters, and whether it carries stray whitespace. Several key
    formats are valid, so the prefix is informational rather than a verdict;
    the live check is what decides.
    """
    raw = os.environ.get("GEMINI_API_KEY")
    if raw is None:
        return {
            "configured": False,
            "reason": "GEMINI_API_KEY is not set in the environment",
            "hint": "An older revision of this README named it GOOGLE_API_KEY, which nothing reads",
        }

    stripped = raw.strip()
    info = {
        "configured": True,
        "length": len(raw),
        "prefix": stripped[:4],
        "has_surrounding_whitespace": raw != stripped,
        "also_sees_legacy_GOOGLE_API_KEY": "GOOGLE_API_KEY" in os.environ,
    }

    info["model"] = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

    try:
        from google import genai

        probe = genai.Client(api_key=stripped)
        # Probe with the call the pipeline actually makes. models.list() returns
        # 401 for key formats that generate_content accepts, so it would report
        # a working key as broken.
        probe.models.generate_content(model=info["model"], contents="ok")
        info["key_accepted"] = True
        info["model_available"] = True
        info["live_check"] = "ok"
    except Exception as exc:  # noqa: BLE001 - reported, not raised
        info.setdefault("key_accepted", False)
        info.setdefault("model_available", False)
        info["live_check"] = "failed"
        info["error"] = _redact(f"{type(exc).__name__}: {exc}")[:300]
    return info


@app.get("/health/db", tags=["health"])
def health_db():
    """Readiness. Reports whether the database is actually reachable."""
    ok, detail = check_connection()
    return {"database": "connected" if ok else "unavailable", "detail": detail}


if __name__ == "__main__":
    # Hosts assign a port via $PORT; 10000 matches Render's default.
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
