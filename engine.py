import argparse
import sys

# Instruments
from src.instruments.base_option import BaseOption
from src.instruments.european_option import EuropeanOption
from src.instruments.american_option import AmericanOption

# Models
from src.models.base_model import BaseModel
from src.models.black_scholes_model import BlackScholesModel

# Pricers
from src.pricers.black_scholes import BlackScholesPricer
from src.pricers.monte_carlo import MonteCarloPricer
from src.pricers.binomial_tree import BinomialTree

# Schemes
from src.schemes.base_scheme import BaseScheme
from src.schemes.euler_scheme import EulerScheme
from src.schemes.exact_gbm_scheme import ExactGBMScheme


def positive_float(value: str) -> float:
    value_float = float(value)
    if value_float <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return value_float


def non_negative_float(value: str) -> float:
    value_float = float(value)
    if value_float < 0:
        raise argparse.ArgumentTypeError("value must be zero or positive")
    return value_float


def positive_int(value: str) -> int:
    value_int = int(value)
    if value_int <= 0:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return value_int


parser = argparse.ArgumentParser(description="An option pricing engine")
parser.add_argument("spot", metavar="Spot", type=positive_float,
                    help="The current price of the underlying stock")
parser.add_argument("rate", metavar="Rate", type=float,
                    help="The rate of return (risk free) yearly")
parser.add_argument("sigma", metavar="Volatility", type=positive_float,
                    help="The current volatility yearly")
parser.add_argument("dividend", metavar="dividend", type=non_negative_float,
                    help="Yearly dividend yield")
parser.add_argument("option", metavar="Option Type", choices=["european", "american"], type=str.lower,
                    help="The type of option to price")
parser.add_argument("model", metavar="Model", choices=["black_scholes"], type=str.lower,
                    help="The world (assumption) model to use")
parser.add_argument("scheme", metavar="Scheme", choices=["euler", "exact_gbm", "closed_form"], type=str.lower,
                    help="The numerical scheme to use")
parser.add_argument("pricer", metavar="Pricer", choices=["black_scholes", "monte_carlo", "binomial_tree"], type=str.lower,
                    help="The pricer to use")
parser.add_argument("--strike", type=positive_float, default=100.0,
                    help="Option strike price (default: 100)")
parser.add_argument("--maturity", type=positive_float, default=1.0,
                    help="Time to maturity in years (default: 1)")
parser.add_argument("--paths", type=positive_int, default=10000,
                    help="Number of Monte Carlo paths (default: 10000)")
parser.add_argument("--seed", type=int, default=0,
                    help="Random seed for Monte Carlo simulation (default: 0)")
parser.add_argument("--steps", type=positive_int, default=100,
                    help="Number of binomial tree steps (default: 100)")

args = parser.parse_args()


def validate_arguments(arguments: argparse.Namespace) -> None:
    if arguments.option == "american" and arguments.pricer == "black_scholes":
        raise ValueError("Black-Scholes pricer only supports European options.")

    if arguments.pricer == "monte_carlo" and arguments.scheme == "closed_form":
        raise ValueError("Monte Carlo pricer requires a numerical scheme, not closed_form.")

    if arguments.pricer == "binomial_tree" and arguments.scheme != "closed_form":
        return


def build_option(arguments: argparse.Namespace) -> BaseOption:
    if arguments.option == "european":
        return EuropeanOption(strike=arguments.strike, maturity=arguments.maturity, option_type="call")
    return AmericanOption(strike=arguments.strike, maturity=arguments.maturity, option_type="call")


def build_scheme(arguments: argparse.Namespace) -> BaseScheme | None:
    if arguments.scheme == "euler":
        return EulerScheme()
    if arguments.scheme == "exact_gbm":
        return ExactGBMScheme()
    return None


def build_pricer(arguments: argparse.Namespace, model: BaseModel, scheme: BaseScheme | None):
    if arguments.pricer == "black_scholes":
        return BlackScholesPricer(model)

    if arguments.pricer == "monte_carlo" and scheme is not None:
        return MonteCarloPricer(model, scheme, arguments.paths, arguments.seed)

    return BinomialTree(arguments.spot, arguments.rate, arguments.sigma, arguments.dividend, arguments.steps)


def main() -> int:
    try:
        validate_arguments(args)
        option = build_option(args)
        model = BlackScholesModel(rate=args.rate, sigma=args.sigma, dividend_yield=args.dividend)
        scheme = build_scheme(args)
        pricer = build_pricer(args, model, scheme)

        if isinstance(pricer, BinomialTree):
            price = pricer.price(option)
        else:
            price = pricer.price(option, args.spot)

        print(f"The option price is: {price}")
        return 0

    except (ValueError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


