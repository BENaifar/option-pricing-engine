import re

def to_years(value: str) -> float:
    """
    Convert time expressions into years.
    
    Rules:
    - '1', '10', '30' -> years (int)
    - '1M', '3M', '6M' -> months converted to years
    """
    value = value.strip().upper()

    # Case 1: months (e.g., "3M")
    match = re.match(r"^(\d+)M$", value)
    if match:
        months = int(match.group(1))
        return months / 12

    # Case 2: years (e.g., "10")
    if value.isdigit():
        return float(value)

    raise ValueError(f"Unsupported format: {value}")