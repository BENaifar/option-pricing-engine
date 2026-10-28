from src.api.mappers.option_request_mapper import maturity_from_request, pricing_settings_from_request
from src.api.schemas import ReportRequest
from src.reporting.option_report_request import OptionReportRequest


def option_report_request_from_request(request: ReportRequest) -> OptionReportRequest:
    return OptionReportRequest(
        ticker=request.ticker,
        strike=request.strike,
        maturity=maturity_from_request(request),
        option_type=request.option_type,
        style=request.style,
        pricers=request.pricers,
        settings=pricing_settings_from_request(request),
        run_tests=request.run_tests,
    )


def report_filename(request: ReportRequest) -> str:
    return f"{request.ticker.upper()}_{request.option_type.value}_{request.strike:g}_report.pdf"
