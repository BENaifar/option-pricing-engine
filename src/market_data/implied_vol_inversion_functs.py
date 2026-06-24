import numpy as np
from scipy.stats import norm

from src.instruments.option_types import OptionType

def calculate_d1(S, K, r, q, sigma, T):
    return (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

def calculate_delta(S, K, r, q, sigma, T, option_type):
    d1 = calculate_d1(S, K, r, q, sigma, T)

    if option_type == "call":
        return norm.cdf(d1)
    elif option_type == "put":
        return norm.cdf(d1) - 1
    else:
        raise ValueError("The option type is not recognized")

def price_fn_bs(S, K, r, q, sigma, T, option_type):
    d1 = calculate_d1(S, K, r, q, sigma, T)
    d2 = d1 - sigma * np.sqrt(T)

    if (option_type == "call"):
        price = S * np.exp(-q * T) * norm.cdf(d1) - K * \
            np.exp((-r) * T) * norm.cdf(d2)
        return float(price)
    elif (option_type == "put"):
        price = K * np.exp((-r) * T) * norm.cdf(-d2) - S * \
            np.exp(-q * T) * norm.cdf(-d1)
        return float(price)

    else:
        raise ValueError("The option type is not recognized")

def price_fn_prime(S, K, r, q, sigma, T):
    d1 = calculate_d1(S, K, r, q, sigma, T)

    return float(S * np.sqrt(T) * norm.pdf(d1) * np.exp(-q * T))
