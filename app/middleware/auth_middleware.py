import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware"""

    async def dispatch(self, request: Request, call_next):
        # Skip public routes
        public_routes = [
            "/login",
            "/auth/",
            "/static/",
            "/health",
            "/docs",
            "/redoc",
            "/debug-tables"
        ]

        if any(request.url.path.startswith(route) for route in public_routes):
            return await call_next(request)

        # For API routes, additional checks can be added here
        if (request.url.path.startswith("/api/") or
            request.url.path.startswith("/documents/") or
            request.url.path.startswith("/search/")):
            # Authentication is handled by dependencies
            pass

        response = await call_next(request)
        return response
