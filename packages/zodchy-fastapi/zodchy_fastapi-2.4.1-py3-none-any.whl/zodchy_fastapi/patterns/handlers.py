from logging import Logger

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response


class ExceptionHandler:
    def __init__(
        self,
        app: FastAPI,
        response_class: type[Response] = JSONResponse,
        logger: Logger | None = None,
    ) -> None:
        self._response_class = response_class
        self._app = app
        self._logger = logger

    # Mapping of error codes to exception types
    _EXCEPTION_TYPES: dict[int, type[Exception]] = {
        422: RequestValidationError,
        500: Exception,
    }

    def __call__(self, *codes: int) -> FastAPI:
        for code in codes:
            if exception_type := self._EXCEPTION_TYPES.get(code):
                self._app.add_exception_handler(
                    exception_type,
                    getattr(self, f"_{code}"),
                )
        return self._app

    async def _500(self, request: Request, exc: Exception) -> Response:
        if self._logger:
            body = None
            try:
                body = await request.body()
            except RuntimeError:
                # Body may not be available in exception handler context
                pass
            self._logger.error(
                f"Internal server error for {request.method} {request.url.path}",
                extra={
                    "error_message": str(exc),
                    "request_body": body,
                },
            )
        return self._response_class(
            status_code=500,
            content={
                "data": {
                    "code": 500,
                    "message": "Internal server error",
                    "details": [],
                }
            },
        )

    async def _422(self, request: Request, exc: RequestValidationError) -> Response:
        if self._logger:
            body = None
            try:
                body = await request.body()
            except RuntimeError:
                # Body may not be available in exception handler context
                pass
            self._logger.error(
                f"Validation error for {request.method} {request.url.path}",
                extra={
                    "validation_errors": exc.errors(),
                    "request_body": body,
                },
            )
        return self._response_class(
            status_code=422,
            content={
                "data": {
                    "code": 422,
                    "message": "Validation error",
                    "details": [
                        {
                            "field": ".".join(map(str, err["loc"])),
                            "message": err["msg"],
                            "type": err["type"],
                        }
                        for err in exc.errors()
                    ],
                }
            },
        )
