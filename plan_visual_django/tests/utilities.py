from datetime import datetime


def date_from_string(date_string: str):
    return datetime.strptime(date_string, "%Y-%m-%d")