from fastapi import APIRouter, Depends, Path
from fastapi.concurrency import run_in_threadpool

from src.api.dependencies import get_pipeline
from src.api.mappers.market_data_response_mapper import market_data_response_from_snapshot
from src.api.schemas import TICKER_PATTERN, MarketDataResponse
from src.pipeline.pricing_pipeline import PricingPipeline

router = APIRouter()


@router.get("/market-data/{ticker}", response_model=MarketDataResponse)
async def market_data(
    ticker: str = Path(pattern=TICKER_PATTERN),
    refresh: bool = False,
    pipeline: PricingPipeline = Depends(get_pipeline),
) -> MarketDataResponse:
    snapshot = await run_in_threadpool(pipeline.get_snapshot, ticker, refresh)
    return market_data_response_from_snapshot(snapshot)
