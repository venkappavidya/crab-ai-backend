import os
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


@app.get("/health/db", tags=["health"])
def health_db():
    """Readiness. Reports whether the database is actually reachable."""
    ok, detail = check_connection()
    return {"database": "connected" if ok else "unavailable", "detail": detail}


if __name__ == "__main__":
    # Hosts assign a port via $PORT; 10000 matches Render's default.
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
