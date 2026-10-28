"""
Entry point.

    python main.py price AAPL --strike 350 --maturity 0.5 --type call
    python main.py price AAPL --strike 350 --expiry 2027-01-15 --style american
    python main.py market-data AAPL
    python main.py report AAPL --strike 350 --maturity 0.5 --type call --out reports/AAPL.pdf
    python main.py serve --port 8000          (docs at http://127.0.0.1:8000/docs)
"""
import argparse
from datetime import date
from pathlib import Path

from src.core.exceptions import PricingEngineError
from src.instruments.option_types import OptionType
from src.pipeline.pricing_pipeline import ExerciseStyle, MonteCarloScheme, PricerName, PricingPipeline, PricingSettings
from src.pricers.monte_carlo import VarianceReductionTechnique


def _maturity_from_args(args) -> float:
    if (args.maturity is None) == (args.expiry is None):
        raise SystemExit("Give exactly one of --maturity (years) or --expiry (YYYY-MM-DD).")
    if args.maturity is not None:
        return args.maturity
    days = (date.fromisoformat(args.expiry) - date.today()).days
    if days <= 0:
        raise SystemExit("--expiry must be in the future.")
    return days / 365.0


def _settings_from_args(args) -> PricingSettings:
    return PricingSettings(
        tree_steps=args.tree_steps,
        mc_paths=args.mc_paths,
        mc_steps=args.mc_steps,
        mc_scheme=MonteCarloScheme(args.mc_scheme),
        mc_variance_reduction=VarianceReductionTechnique(args.mc_variance_reduction),
        mc_confidence_level=args.mc_confidence_level,
        seed=args.seed,
    )


def run_price(args):
    pipeline = PricingPipeline()
    result = pipeline.price(
        ticker=args.ticker,
        strike=args.strike,
        maturity=_maturity_from_args(args),
        option_type=OptionType.from_string(args.type),
        style=ExerciseStyle(args.style),
        pricers=[PricerName(p) for p in args.pricers] if args.pricers else None,
        compute_greeks=not args.no_greeks,
        settings=_settings_from_args(args),
    )

    print(f"{result.ticker}  spot={result.spot:.4f} [{result.spot_source}, quoted {result.quoted_spot:.4f}]  ({result.market_data_source}, {result.market_data_timestamp})")
    print(f"{result.style.value} {result.option_type.value}  K={result.strike}  T={result.maturity:.4f}y")
    print(f"r={result.rate:.4%}  q={result.dividend_yield:.4%}  sigma={result.volatility:.4%}\n")

    header = f"{'pricer':<22}{'price':>12}"
    if not args.no_greeks:
        header += "".join(f"{g:>12}" for g in ("delta", "gamma", "theta", "vega", "rho"))
    print(header)

    for r in result.results:
        line = f"{r.pricer.value:<22}{r.price:>12.4f}"
        if r.greeks is not None:
            g = r.greeks
            line += "".join(f"{v:>12.4f}" for v in (g.delta, g.gamma, g.theta, g.vega, g.rho))
        print(line)

    for r in result.results:
        if r.statistics is not None:
            s = r.statistics
            low, high = s.confidence_interval
            print(f"\n{r.pricer.value}: standard error {s.standard_error:.4f}, "
                  f"{args.mc_confidence_level:.0%} CI [{low:.4f}, {high:.4f}], {s.observations:,} observations "
                  f"({args.mc_variance_reduction})")


def run_market_data(args):
    snapshot = PricingPipeline().get_snapshot(args.ticker)
    surface = snapshot.sigma

    print(f"{snapshot.ticker}  spot={snapshot.spot:.4f} [{snapshot.spot_source}, quoted {snapshot.quoted_spot:.4f}]  ({snapshot.source}, {snapshot.timestamp})")
    print("rates: " + "  ".join(f"{t}y={snapshot.rate.r(t):.4%}" for t in (0.25, 1, 2, 5, 10, 30)))
    carries = "  ".join(f"{t}y={snapshot.dividend_yield.q(t):.4%}" for t in (0.25, 0.5, 1, 2))
    print(f"dividend / carry yield [{snapshot.dividend_source}]: {carries}\n")

    moneyness = (0.8, 0.9, 1.0, 1.1, 1.2)
    print(f"{'T (years)':<12}" + "".join(f"{m:>10.0%}" for m in moneyness))
    for T in getattr(surface, "times", []):
        print(f"{T:<12.4f}" + "".join(f"{surface.get_vol(m * snapshot.spot, T):>10.2%}" for m in moneyness))


def run_report(args):
    from src.reporting.option_report_request import OptionReportRequest
    from src.reporting.pdf.pdf_report_renderer import PdfReportRenderer
    from src.reporting.report_service import ReportService

    data = ReportService(PricingPipeline()).build(OptionReportRequest(
        ticker=args.ticker,
        strike=args.strike,
        maturity=_maturity_from_args(args),
        option_type=OptionType.from_string(args.type),
        style=ExerciseStyle(args.style),
        pricers=[PricerName(p) for p in args.pricers] if args.pricers else None,
        settings=_settings_from_args(args),
        run_tests=not args.skip_tests,
    ))

    out = Path(args.out or f"reports/{data.pricing.ticker}_{data.pricing.option_type.value}_{args.strike:g}_report.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    PdfReportRenderer().render(data, out)
    print(f"Report written to {out.resolve()}")


def run_serve(args):
    import uvicorn

    uvicorn.run("src.api.app:app", host=args.host, port=args.port, reload=args.reload)


def _add_option_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("ticker")
    parser.add_argument("--strike", type=float, required=True)
    parser.add_argument("--maturity", type=float, help="Time to maturity in years")
    parser.add_argument("--expiry", help="Expiry date YYYY-MM-DD")
    parser.add_argument("--type", default="call", help="call or put")
    parser.add_argument("--style", default="european", choices=[s.value for s in ExerciseStyle])
    parser.add_argument("--pricers", nargs="+", choices=[p.value for p in PricerName])
    parser.add_argument("--tree-steps", type=int, default=1000)
    parser.add_argument("--mc-paths", type=int, default=100_000)
    parser.add_argument("--mc-steps", type=int, default=64)
    parser.add_argument("--mc-scheme", default="exact", choices=[s.value for s in MonteCarloScheme])
    parser.add_argument("--mc-variance-reduction", default=VarianceReductionTechnique.NONE.value, choices=[t.value for t in VarianceReductionTechnique])
    parser.add_argument("--mc-confidence-level", type=float, default=0.95)
    parser.add_argument("--seed", type=int, default=42)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Option pricing engine")
    commands = parser.add_subparsers(dest="command", required=True)

    price = commands.add_parser("price", help="Price an option on live market data")
    _add_option_arguments(price)
    price.add_argument("--no-greeks", action="store_true")
    price.set_defaults(func=run_price)

    report = commands.add_parser("report", help="Write a PDF report for an option")
    _add_option_arguments(report)
    report.add_argument("--out", help="Output PDF path (default: reports/<ticker>_<type>_<strike>_report.pdf)")
    report.add_argument("--skip-tests", action="store_true", help="Do not run the test suite")
    report.set_defaults(func=run_report)

    market_data = commands.add_parser("market-data", help="Show the market data snapshot for a ticker")
    market_data.add_argument("ticker")
    market_data.set_defaults(func=run_market_data)

    serve = commands.add_parser("serve", help="Run the FastAPI server")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--reload", action="store_true")
    serve.set_defaults(func=run_serve)

    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    try:
        args.func(args)
    except PricingEngineError as error:
        raise SystemExit(f"error: {error}")
