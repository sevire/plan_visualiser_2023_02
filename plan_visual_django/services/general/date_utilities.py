from datetime import datetime, date


def date_from_string(date_string):
    date = datetime.strptime(date_string, '%d:%m:%Y').date()
    return date


def days_between_dates(start_date: date, end_date: date):
    num_days = end_date.toordinal() - start_date.toordinal() + 1
    return num_days



