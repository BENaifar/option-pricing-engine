import os

import numpy as np
import pandas as pd

from src.core.config import read_config
from src.time.str_to_date import safe_parse_date
from src.time.to_years import to_years
from src.market_data.providers.base_market_data_provider import BaseMarketDataProvider


class CsvMarketDataProvider(BaseMarketDataProvider):
    def fetch_rate(self) -> dict:
        path = read_config("paths", "raw_data_rates")

        dfs = {}

        for file in os.listdir(path):
            if file.endswith('.csv'):
                full_path = os.path.join(path, file)
                data = pd.read_csv(full_path, sep=",")

                # extract maturity label (same logic you used)
                maturity = file[3:-4]  # e.g. "DGS10" or similar

                # convert last value
                rate = float(pd.to_numeric(data.iloc[-1, -1]) / 100)

                # create a proper DataFrame expected by build_rate_curve
                df = pd.DataFrame(
                    {maturity: [rate]},
                    index=[pd.to_datetime("today").normalize()]  # or real date if available in file
                )

                dfs[maturity] = df

        return dfs

    

        

