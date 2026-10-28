import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions import (
    InvalidOptionRequestError,
    MarketDataUnavailableError,
    PricingEngineError,
    TickerNotFoundError,
)

logger = logging.getLogger(__name__)

STATUS_CODES: dict[type[PricingEngineError], int] = {
    TickerNotFoundError: 404,
    InvalidOptionRequestError: 422,
    MarketDataUnavailableError: 503,
}


async def handle_pricing_engine_error(request: Request, error: PricingEngineError) -> JSONResponse:
    status_code = next((code for kind, code in STATUS_CODES.items() if isinstance(error, kind)), 400)
    return JSONResponse(status_code=status_code, content={"detail": str(error)})


async def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


def register_error_handlers(application: FastAPI) -> None:
    application.add_exception_handler(PricingEngineError, handle_pricing_engine_error)
    application.add_exception_handler(Exception, handle_unexpected_error)
