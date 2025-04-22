from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import os
from .monitoring import record_security_event

limiter = Limiter(key_func=get_remote_address)

class RequestSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.headers.get('content-length'):
            if int(request.headers['content-length']) > 5 * 1024 * 1024:  # 5MB limit
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request too large"}
                )
        response = await call_next(request)
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

def init_middleware(app: FastAPI) -> None:
    # CORS configuration
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["X-Total-Count"]
    )

    # Request size limiting
    app.add_middleware(RequestSizeMiddleware)

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate limiting configuration
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc):
        record_security_event(
            event_type="rate_limit_exceeded",
            ip_address=get_remote_address(request),
            path=request.url.path
        )
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )

    # Request timing middleware
    @app.middleware("http")
    async def add_timing_header(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    return app