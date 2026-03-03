class Option:
    def __init__(self, S0:float, K:float, T:float, sigma:float, r:float, option_type='call'):    
        self.S0 = S0
        self.K = K
        self.T = T
        self.sigma = sigma
        self.r = r
        self.option_type = option_type.lower()
    
    def __str__(self):
        return f"Option(S0={self.S0}, K={self.K}, T={self.T}, sigma={self.sigma}, r={self.r}, option_type='{self.option_type}')"
    
    def payoff(self, ST:float) -> float | None:
        if(self.option_type == 'put'):
            return max(self.K - ST, 0)
        elif(self.option_type == 'call'):
            return max(ST - self.K, 0)
