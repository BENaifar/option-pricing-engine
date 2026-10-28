import numpy as np

from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.models.option_quote import OptionQuote


class ImpliedSpotFromParity:
    """
    Spot implied by the option market through put-call parity:
        C - P = S e^{-qT} - K e^{-rT}   =>   S = (C - P + K e^{-rT}) e^{qT}

    The equity price and the option chain come from different feeds / timestamps, so the quoted spot
    can be out of sync with the options. Pricing off it shifts every forward and biases the vol skew.

    Only near-the-money pairs priced from a bid/ask mid are used: that is where quotes are liquid and
    where the early exercise premium of listed (American) options, which breaks exact parity, is smallest.

    The spot only uses short maturities: any error in the carry (r - q) shifts the implied spot by ~ S (r - q) T.
    The carry itself is calibrated per expiry with implied_forwards.
    """

    def __init__(
        self,
        moneyness_band: float = 0.05,
        min_maturity: float = 7 / 365,
        max_maturity: float = 45 / 365,
        min_pairs: int = 3,
        max_relative_gap: float = 0.02
    ):
        self.moneyness_band = moneyness_band
        self.min_maturity = min_maturity
        self.max_maturity = max_maturity
        self.min_pairs = min_pairs
        self.max_relative_gap = max_relative_gap

    def _pairs(
        self,
        option_quotes: list[OptionQuote],
        quoted_spot: float,
        min_maturity: float,
        max_maturity: float
    ) -> tuple[dict, dict]:
        """Near-the-money call and put mids keyed by (K, T), for (K, T) quoted on both sides."""
        calls, puts = {}, {}

        for quote in option_quotes:
            if not quote.is_mid:
                continue
            if not min_maturity <= quote.T <= max_maturity:
                continue
            if abs(quote.K / quoted_spot - 1) > self.moneyness_band:
                continue

            side = calls if quote.type == "call" else puts
            side[(quote.K, quote.T)] = quote.price

        keys = calls.keys() & puts.keys()
        return {k: calls[k] for k in keys}, {k: puts[k] for k in keys}

    def implied_spots(
        self,
        option_quotes: list[OptionQuote],
        quoted_spot: float,
        yield_curve: YieldCurve,
        dividend_curve: DividendCurve
    ) -> list[float]:
        calls, puts = self._pairs(option_quotes, quoted_spot, self.min_maturity, self.max_maturity)

        spots = []
        for K, T in calls:
            r, q = yield_curve.r(T), dividend_curve.q(T)
            spots.append(float((calls[(K, T)] - puts[(K, T)] + K * np.exp(-r * T)) * np.exp(q * T)))

        return spots

    def get_spot(
        self,
        option_quotes: list[OptionQuote],
        quoted_spot: float,
        yield_curve: YieldCurve,
        dividend_curve: DividendCurve
    ) -> float | None:
        """Median parity-implied spot, or None when there is not enough reliable data to trust it."""
        spots = self.implied_spots(option_quotes, quoted_spot, yield_curve, dividend_curve)

        # outside trading hours bid/ask are often missing: not enough pairs
        if len(spots) < self.min_pairs:
            return None

        implied_spot = float(np.median(spots))

        # a large gap means bad data rather than a timing mismatch
        if abs(implied_spot / quoted_spot - 1) > self.max_relative_gap:
            return None

        return implied_spot

    def implied_forwards(
        self,
        option_quotes: list[OptionQuote],
        quoted_spot: float,
        yield_curve: YieldCurve,
        min_maturity: float = 30 / 365,
        max_maturity: float = 3.0,
        min_pairs_per_expiry: int = 2
    ) -> dict[float, float]:
        """
        Forward per expiry from parity: C - P = e^{-rT} (F - K)  =>  F = (C - P) e^{rT} + K.
        Short expiries are left out: turning F into a carry divides its noise by T.
        """
        calls, puts = self._pairs(option_quotes, quoted_spot, min_maturity, max_maturity)

        forwards_by_expiry: dict[float, list[float]] = {}
        for K, T in calls:
            forward = (calls[(K, T)] - puts[(K, T)]) * np.exp(yield_curve.r(T) * T) + K
            forwards_by_expiry.setdefault(T, []).append(float(forward))

        return {
            T: float(np.median(forwards))
            for T, forwards in sorted(forwards_by_expiry.items())
            if len(forwards) >= min_pairs_per_expiry
        }
