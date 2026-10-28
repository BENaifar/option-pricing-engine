from fastapi import FastAPI

from src.api.errors import register_error_handlers
from src.api.routers.health import router as health_router
from src.api.routers.market_data import router as market_data_router
from src.api.routers.pricing import router as pricing_router
from src.api.routers.reports import router as reports_router
from src.pipeline.pricing_pipeline import PricingPipeline
from src.reporting.pdf.pdf_report_renderer import PdfReportRenderer
from src.reporting.report_service import ReportService


def create_app() -> FastAPI:
    application = FastAPI(
        title="Option Pricing Engine",
        description="Black-Scholes pricing (closed form, binomial tree, Monte Carlo) on live market data.",
        version="0.1.0",
    )

    pipeline = PricingPipeline()
    application.state.pipeline = pipeline
    application.state.report_service = ReportService(pipeline)
    application.state.report_renderer = PdfReportRenderer()

    register_error_handlers(application)

    application.include_router(health_router)
    application.include_router(pricing_router)
    application.include_router(market_data_router)
    application.include_router(reports_router)

    return application


app = create_app()
