from abc import ABC, abstractmethod

class VolatilityModel(ABC):
    """
    Abstract volatility model. Anything that can answer:
    'what is σ(K, T)?' qualifies.
    """

    @abstractmethod
    def get_vol(self, K, T) -> float:
        pass

    # @abstractmethod
    # def is_valid(self) -> bool:
    #     """Basic sanity check — did the fit succeed?"""
    #     pass