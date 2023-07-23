from datetime import datetime


def date_from_string(date_string: str):
    """

    :param date_string: Date string of form "YYYY-MM-DD"
    :return:
    """
    return datetime.strptime(date_string, "%Y-%m-%d")