import os

import numpy as np
import pandas as pd

from src.core.config import read_config
from src.time.str_to_date import safe_parse_date
from src.time.to_years import to_years
from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider


class CsvMarketDataProvider(BaseMarketDataProvider):
    
    def fetch(self, ticker: str) -> pd.DataFrame:
        path = read_config("paths", "raw_data") + f"/{ticker}.csv"
        
        data = pd.read_csv(
            path,
            sep=",",
            parse_dates=["Date"],
            dayfirst=False,
            index_col="Date"
        ).sort_values(by=["Date"])

        return data
    
    def fetch_spot(self, ticker: str):
        path = read_config("paths", "raw_data_tickers") + f"/{ticker}.csv"
        
        data = pd.read_csv(
            path,
            sep=",",
            parse_dates=["Date"],
            dayfirst=False,
            index_col="Date"
        ).sort_values(by=["Date"])

        return data
    
    def fetch_rate(self) -> pd.DataFrame:
        path = read_config("paths", "raw_data_rates")
        
        result = {
            "maturities" : [],
            "rates": []
        }

        for file in os.listdir(path):
            if file.endswith('.csv'):
                full_path = os.path.join(path, file)
                data = pd.read_csv(full_path, sep=",")
                rate = float(pd.to_numeric(data.iloc[-1, -1]) / 100)
                maturity = file[3:-4]
                result["maturities"].append(maturity)
                result["rates"].append(rate)

        return pd.DataFrame(result)
    
    def fetch_dividend(self, ticker: str) -> pd.DataFrame:
        path = read_config("paths", "raw_data_tickers") + f"/{ticker}_div.csv"

        data = pd.read_csv(
            path,
            parse_dates=["Date"],
            dayfirst=False,
        ).sort_values(by=['Date'])

        return data

if __name__ == "__main__":
    provider = CsvMarketDataProvider()

    divs = provider.fetch_dividend('appl')

    dates = divs["Date"].tolist()
    dates = [d.date() for d in dates]
    values = divs["Dividend($)"].tolist()

    print(dates)
    print(values)

    

        

