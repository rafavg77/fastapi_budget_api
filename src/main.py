from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
import logging
import logging.config
from datetime import datetime

from app.api.v1 import auth, cards, transactions
from app.core.middleware import SecurityHeadersMiddleware, RateLimitingMiddleware, BruteForceProtectionMiddleware
from app.core.error_handling import (
    validation_error_handler,
    sqlalchemy_error_handler,
    http_exception_handler,
    general_exception_handler
)
from app.database.database import engine
from app.models import models

# Configure logging
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        },
    }
})

logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Budget API",
    description="API for managing personal budget and card transactions",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Add security middlewares in correct order
app.add_middleware(BruteForceProtectionMiddleware, max_attempts=5, lockout_time=300)
app.add_middleware(RateLimitingMiddleware, rate_limit=100, time_window=60)
app.add_middleware(SecurityHeadersMiddleware)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(cards.router, prefix="/api/v1", tags=["cards"])
app.include_router(transactions.router, prefix="/api/v1", tags=["transactions"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Budget API"}

@app.get("/api/v1/")
async def read_api_root():
    return {"version": "1.0.0", "status": "active"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/metrics")
async def metrics():
    return (
        "http_requests_total{method=\"GET\"} 100\n"
        "http_requests_total{method=\"POST\"} 50\n"
        "http_request_duration_seconds{method=\"GET\"} 0.123\n"
        "http_request_duration_seconds{method=\"POST\"} 0.456\n"
    )