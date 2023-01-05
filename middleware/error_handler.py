"""
Error Handler Middlerware script.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse


class ErrorHandler(BaseHTTPMiddleware):
    """
    Error Handler class based on Starlette Base HTTP Middleware
    """
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request,
                       call_next) -> Response | JSONResponse:
        try:
            return await call_next(request)
        except HTTPException as exc:
            return JSONResponse(status_code=500, content={'error': str(exc)})
