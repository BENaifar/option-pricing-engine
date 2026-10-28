from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from src.api.dependencies import get_pipeline
from src.api.mappers.option_request_mapper import maturity_from_request, pricing_settings_from_request
from src.api.mappers.price_response_mapper import price_response_from_result
from src.api.schemas import PriceRequest, PriceResponse
from src.pipeline.pricing_pipeline import PricingPipeline

router = APIRouter()


@router.post("/price", response_model=PriceResponse)
async def price(request: PriceRequest, pipeline: PricingPipeline = Depends(get_pipeline)) -> PriceResponse:
    result = await run_in_threadpool(
        pipeline.price,
        ticker=request.ticker,
        strike=request.strike,
        maturity=maturity_from_request(request),
        option_type=request.option_type,
        style=request.style,
        pricers=request.pricers,
        compute_greeks=request.greeks,
        settings=pricing_settings_from_request(request),
    )
    return price_response_from_result(result)
