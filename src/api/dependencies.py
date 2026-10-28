from fastapi import Request

from src.pipeline.pricing_pipeline import PricingPipeline
from src.reporting.pdf.pdf_report_renderer import PdfReportRenderer
from src.reporting.report_service import ReportService


def get_pipeline(request: Request) -> PricingPipeline:
    return request.app.state.pipeline


def get_report_service(request: Request) -> ReportService:
    return request.app.state.report_service


def get_report_renderer(request: Request) -> PdfReportRenderer:
    return request.app.state.report_renderer
