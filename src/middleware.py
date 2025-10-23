from fastapi import FastAPI, Request, status
import time
import logging
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_logging_middleware(request: Request, call_next):

        start_time = time.perf_counter()

        response = await call_next(request)

        End_Time = time.perf_counter() - start_time

        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} - Completed after {End_Time:.6f} sec"

        print(message)

        return response

    # @app.middleware("http")
    # async def authorization(request: Request, call_next):
    #     open_routes = ["/api/v1/auth/signup", "/api/v1/auth/login"]

    #     if any(request.url.path.startswith(route) for route in open_routes):
    #         return await call_next(request)

    #     if not "Authorization" in request.headers:
    #         return JSONResponse(
    #             content={
    #                 "message": "Not Authenticated",
    #                 "resolution": "please provide the right credentials to proceed",
    #             },
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #         )

        response = await call_next(request)
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
