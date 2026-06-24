from enum import Enum


class OptionType(Enum):
    """Enum for option types"""
    CALL = "call"
    PUT = "put"

    @classmethod
    def from_string(cls, s: str) -> "OptionType":
        """Create an OptionType from a string.

        Accepts values like 'call', 'CALL', 'Call', 'c', 'C', 'put', 'p', etc.
        Raises ValueError for unknown values.
        """
        if not isinstance(s, str):
            raise ValueError(f"OptionType must be created from a string, got {type(s)}")

        normalized = s.strip().lower()
        if normalized in ("call", "c"):
            return cls.CALL
        if normalized in ("put", "p"):
            return cls.PUT

        raise ValueError(f"Unknown OptionType: {s}")
