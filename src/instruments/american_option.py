from dataclasses import dataclass

from src.instruments.base_option import BaseOption

@dataclass
class AmericanOption(BaseOption):

    def is_american(self) -> bool:
        return True