import pytest

from src.instruments.european_option import EuropeanOption
from src.instruments.option_types import OptionType

def test_option_strike_validation():
    with pytest.raises(ValueError):
        option = EuropeanOption(-1, 1, OptionType.CALL)
    
    with pytest.raises(ValueError):
        option = EuropeanOption(0, 1, OptionType.CALL)

def test_option_maturity_validation():
    with pytest.raises(ValueError):
        option = EuropeanOption(100, -1, OptionType.CALL)

    with pytest.raises(ValueError):
        option = EuropeanOption(100, 0, OptionType.CALL)

def test_option_type_validation():
    with pytest.raises(ValueError):
        option = EuropeanOption(100, 1, "call")
