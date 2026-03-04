from src.models.option import Option

class EuropeanOption(Option):
    def __init__(self, S0:float, K:float, T:float, sigma:float, r:float, option_type='call'):
        super().__init__(S0, K, T, sigma, r, option_type)
    
    def __str__(self):
        return f"EuropeanOption(S0={self.S0}, K={self.K}, T={self.T}, sigma={self.sigma}, r={self.r}, option_type='{self.option_type}')"