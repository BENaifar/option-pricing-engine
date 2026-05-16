from datetime import date, datetime

def safe_parse_date(date_str: str | date):
    if type(date_str) == date:
        return date_str
    
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").date()
    except ValueError:
        raise ValueError("The date input was either not a date or in the incorrect format. \n The format mm/dd/yyyy is needed")