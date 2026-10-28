from fastapi import APIRouter, Depends, Response
from fastapi.concurrency import run_in_threadpool

from src.api.dependencies import get_report_renderer, get_report_service
from src.api.mappers.report_request_mapper import option_report_request_from_request, report_filename
from src.api.schemas import ReportRequest
from src.reporting.pdf.pdf_report_renderer import PdfReportRenderer
from src.reporting.report_service import ReportService

router = APIRouter()


@router.post("/report", response_class=Response, responses={200: {"content": {"application/pdf": {}}}})
async def report(
    request: ReportRequest,
    report_service: ReportService = Depends(get_report_service),
    report_renderer: PdfReportRenderer = Depends(get_report_renderer),
) -> Response:
    """PDF report: inputs, prices, Greeks, model vs live market quotes, test results, limitations."""
    option_request = option_report_request_from_request(request)
    data = await run_in_threadpool(report_service.build, option_request)
    pdf = await run_in_threadpool(report_renderer.render_bytes, data)

    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{report_filename(request)}"'},
    )
