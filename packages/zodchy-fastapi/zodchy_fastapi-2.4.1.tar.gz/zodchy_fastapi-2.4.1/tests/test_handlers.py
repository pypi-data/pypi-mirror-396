import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel

from zodchy_fastapi.patterns.handlers import ExceptionHandler


class RequestBody(BaseModel):
    """Sample request body for testing validation errors."""

    name: str
    value: int


def test_exception_handler_initializes_with_defaults() -> None:
    """Test that ExceptionHandler initializes with default values."""
    app = FastAPI()
    handler = ExceptionHandler(app)

    assert handler._app is app
    assert handler._logger is None
    assert handler._response_class is JSONResponse


def test_exception_handler_initializes_with_logger() -> None:
    """Test that ExceptionHandler accepts a logger."""
    app = FastAPI()
    logger = logging.getLogger("test")
    handler = ExceptionHandler(app, logger=logger)

    assert handler._logger is logger


def test_exception_handler_returns_app_on_call() -> None:
    """Test that __call__ returns the FastAPI app."""
    app = FastAPI()
    handler = ExceptionHandler(app)

    result = handler(422)

    assert result is app


def test_422_handler_returns_validation_error_response() -> None:
    """Test that _422 handler returns proper validation error response."""
    app = FastAPI()
    handler = ExceptionHandler(app)
    handler(422)

    @app.post("/test")
    async def test_endpoint(body: RequestBody) -> dict:
        return {"status": "ok"}

    client = TestClient(app)
    response = client.post("/test", json={"name": 123, "value": "not_an_int"})

    assert response.status_code == 422
    payload = response.json()
    assert "data" in payload
    assert payload["data"]["code"] == 422
    assert payload["data"]["message"] == "Validation error"
    assert isinstance(payload["data"]["details"], list)
    assert len(payload["data"]["details"]) > 0

    # Check that each detail has required fields
    for detail in payload["data"]["details"]:
        assert "field" in detail
        assert "message" in detail
        assert "type" in detail


def test_422_handler_includes_field_path_in_details() -> None:
    """Test that field paths are correctly formatted in error details."""
    app = FastAPI()
    handler = ExceptionHandler(app)
    handler(422)

    @app.post("/test")
    async def test_endpoint(body: RequestBody) -> dict:
        return {"status": "ok"}

    client = TestClient(app)
    # Send invalid data - value should be int
    response = client.post("/test", json={"name": "test", "value": "not_int"})

    assert response.status_code == 422
    payload = response.json()
    details = payload["data"]["details"]

    # Find the error for the 'value' field
    value_errors = [d for d in details if "value" in d["field"]]
    assert len(value_errors) > 0


def test_422_handler_with_missing_fields() -> None:
    """Test validation error when required fields are missing."""
    app = FastAPI()
    handler = ExceptionHandler(app)
    handler(422)

    @app.post("/test")
    async def test_endpoint(body: RequestBody) -> dict:
        return {"status": "ok"}

    client = TestClient(app)
    response = client.post("/test", json={})

    assert response.status_code == 422
    payload = response.json()
    assert payload["data"]["code"] == 422
    # Should have errors for both missing 'name' and 'value'
    assert len(payload["data"]["details"]) >= 2


def test_422_handler_with_logger_logs_error() -> None:
    """Test that _422 handler logs errors when logger is provided."""
    log_records: list[logging.LogRecord] = []

    class ListHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            log_records.append(record)

    logger = logging.getLogger("test_422_logger")
    logger.setLevel(logging.ERROR)
    logger.handlers.clear()
    logger.addHandler(ListHandler())
    logger.propagate = False

    app = FastAPI()
    handler = ExceptionHandler(app, logger=logger)
    handler(422)

    @app.post("/test")
    async def test_endpoint(body: RequestBody) -> dict:
        return {"status": "ok"}

    client = TestClient(app)
    response = client.post("/test", json={"invalid": "data"})

    assert response.status_code == 422
    assert len(log_records) == 1
    assert "Validation error for POST /test" in log_records[0].getMessage()


def test_500_handler_returns_internal_server_error() -> None:
    """Test that _500 handler returns proper internal server error response."""
    app = FastAPI()
    handler = ExceptionHandler(app)
    handler(500)

    @app.get("/test")
    async def test_endpoint() -> dict:
        raise RuntimeError("Something went wrong")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/test")

    assert response.status_code == 500
    payload = response.json()
    assert "data" in payload
    assert payload["data"]["code"] == 500
    assert payload["data"]["message"] == "Internal server error"
    assert payload["data"]["details"] == []


def test_500_handler_with_logger_logs_error() -> None:
    """Test that _500 handler logs errors when logger is provided."""
    log_records: list[logging.LogRecord] = []

    class ListHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            log_records.append(record)

    logger = logging.getLogger("test_500_logger")
    logger.setLevel(logging.ERROR)
    logger.handlers.clear()
    logger.addHandler(ListHandler())
    logger.propagate = False

    app = FastAPI()
    handler = ExceptionHandler(app, logger=logger)
    handler(500)

    @app.get("/test")
    async def test_endpoint() -> dict:
        raise RuntimeError("Test error message")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/test")

    assert response.status_code == 500
    assert len(log_records) == 1
    assert "Internal server error for GET /test" in log_records[0].getMessage()


def test_exception_handler_with_multiple_codes() -> None:
    """Test that multiple error codes can be registered."""
    app = FastAPI()
    handler = ExceptionHandler(app)

    result = handler(422, 500)

    assert result is app


def test_422_handler_handles_nested_validation_errors() -> None:
    """Test validation errors with nested model fields."""

    class NestedModel(BaseModel):
        inner_value: int

    class OuterModel(BaseModel):
        nested: NestedModel

    app = FastAPI()
    handler = ExceptionHandler(app)
    handler(422)

    @app.post("/test")
    async def test_endpoint(body: OuterModel) -> dict:
        return {"status": "ok"}

    client = TestClient(app)
    response = client.post("/test", json={"nested": {"inner_value": "not_int"}})

    assert response.status_code == 422
    payload = response.json()
    details = payload["data"]["details"]

    # Check that nested field path is correctly formatted
    assert any("nested" in d["field"] and "inner_value" in d["field"] for d in details)


def test_422_handler_handles_list_validation_errors() -> None:
    """Test validation errors with list fields."""

    class ListModel(BaseModel):
        items: list[int]

    app = FastAPI()
    handler = ExceptionHandler(app)
    handler(422)

    @app.post("/test")
    async def test_endpoint(body: ListModel) -> dict:
        return {"status": "ok"}

    client = TestClient(app)
    response = client.post("/test", json={"items": [1, "not_int", 3]})

    assert response.status_code == 422
    payload = response.json()
    details = payload["data"]["details"]

    # Should have error for the invalid item in the list
    assert len(details) > 0
    # The field path should include the index (e.g., "body.items.1")
    assert any("items" in d["field"] for d in details)


def test_exception_handler_without_logger_does_not_raise() -> None:
    """Test that handler works correctly without a logger."""
    app = FastAPI()
    handler = ExceptionHandler(app)  # No logger
    handler(422)

    @app.post("/test")
    async def test_endpoint(body: RequestBody) -> dict:
        return {"status": "ok"}

    client = TestClient(app)
    response = client.post("/test", json={"invalid": "data"})

    # Should not raise and should return proper response
    assert response.status_code == 422


def test_422_response_structure_matches_expected_format() -> None:
    """Test that the response structure exactly matches the expected format."""
    app = FastAPI()
    handler = ExceptionHandler(app)
    handler(422)

    @app.post("/test")
    async def test_endpoint(body: RequestBody) -> dict:
        return {"status": "ok"}

    client = TestClient(app)
    response = client.post("/test", json={"name": "test"})  # Missing 'value'

    payload = response.json()

    # Verify exact structure
    assert set(payload.keys()) == {"data"}
    assert set(payload["data"].keys()) == {"code", "message", "details"}
    assert isinstance(payload["data"]["code"], int)
    assert isinstance(payload["data"]["message"], str)
    assert isinstance(payload["data"]["details"], list)

    if payload["data"]["details"]:
        detail = payload["data"]["details"][0]
        assert set(detail.keys()) == {"field", "message", "type"}


def test_422_handler_with_query_parameter_validation() -> None:
    """Test validation errors for query parameters."""
    app = FastAPI()
    handler = ExceptionHandler(app)
    handler(422)

    @app.get("/test")
    async def test_endpoint(limit: int) -> dict:
        return {"limit": limit}

    client = TestClient(app)
    response = client.get("/test?limit=not_an_int")

    assert response.status_code == 422
    payload = response.json()
    assert payload["data"]["code"] == 422
    details = payload["data"]["details"]
    assert any("limit" in d["field"] for d in details)


def test_422_handler_with_path_parameter_validation() -> None:
    """Test validation errors for path parameters."""
    app = FastAPI()
    handler = ExceptionHandler(app)
    handler(422)

    @app.get("/items/{item_id}")
    async def test_endpoint(item_id: int) -> dict:
        return {"item_id": item_id}

    client = TestClient(app)
    response = client.get("/items/not_an_int")

    assert response.status_code == 422
    payload = response.json()
    assert payload["data"]["code"] == 422


def test_valid_request_passes_through_handler() -> None:
    """Test that valid requests are not affected by the exception handler."""
    app = FastAPI()
    handler = ExceptionHandler(app)
    handler(422)

    @app.post("/test")
    async def test_endpoint(body: RequestBody) -> dict:
        return {"name": body.name, "value": body.value}

    client = TestClient(app)
    response = client.post("/test", json={"name": "test", "value": 42})

    assert response.status_code == 200
    payload = response.json()
    assert payload == {"name": "test", "value": 42}
