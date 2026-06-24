from abc import ABC, abstractmethod

class VolatilityModel(ABC):
    """
    Abstract volatility model. Anything that can answer:
    'what is σ(K, T)?' qualifies.
    """

    @abstractmethod
    def vol(self, K: float, T: float) -> float:
        """Return implied vol for strike K and maturity T."""
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        """Basic sanity check — did the fit succeed?"""
        pass