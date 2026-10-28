import configparser
from pathlib import Path

# resolve config.ini from the project root, not from the current working directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.ini"

def create_config():
    config = configparser.ConfigParser()

    config["greek_bumps"] = {
        "spot_rel": '0.02',
        "gamma_rel": '0.02',
        "vol_abs": '0.005',
        "rate_abs": '1e-4',
        "time_days": str(1/365)
    }

    config["paths"] = {
        "raw_data_tickers": "data/raw/tickers",
        "raw_data_rates": "data/raw/DGS"
    }

    # Write the configuration to a file
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)

def read_config(key: str, value: str):
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read(CONFIG_PATH)

    # Access values from the configuration file
    result = config.get(key, value)

    return result

def read_config_float(key: str, value: str):
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read(CONFIG_PATH)

    # Access values from the configuration file
    result = config.getfloat(key, value)

    return result

if __name__ == "__main__":
    create_config()