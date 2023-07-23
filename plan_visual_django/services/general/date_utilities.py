from datetime import datetime, date, timedelta
import os
from calendar import monthrange
from enum import Enum

from dateutil.relativedelta import relativedelta


def date_from_string(date_string):
    date = datetime.strptime(date_string, '%d:%m:%Y').date()
    return date


def days_between_dates(start_date: date, end_date: date):
    num_days = end_date.toordinal() - start_date.toordinal() + 1
    return num_days


def get_path_name_ext(path):
    folder = os.path.dirname(path)
    file = os.path.basename(path)
    base, ext = os.path.splitext(file)

    return folder, base, ext


def first_day_of_month(date):
    return date.replace(day=1)


def last_day_of_month(date):
    return date.replace(day=monthrange(date.year, date.month)[1])


def month_increment(date:date, num_months):
    return date + relativedelta(months=num_months)


def day_increment(in_date, num_days):
    return in_date + relativedelta(days=num_days)


def num_months_between_dates(start_date, end_date):
    r = relativedelta(end_date, start_date)
    return r.years * 12 + r.months + 1


def iterate_months(date, num_months):
    yield date
    for month in range(num_months):
        yield month_increment(date, month)


def is_current(start_date, end_date):
    today = date.today()
    return start_date < today < end_date


def is_past(start_date, end_date):
    today = date.today()
    return start_date < end_date <= today


def is_future(start_date, end_date):
    today = date.today()
    return today < start_date < end_date


def is_nan(value: str):
    # Uses property that nan != nan in pandas/numpy
    ret_value = (value != value)
    return ret_value


class DateIncrementUnit(Enum):
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"

"""
Way of incrementing from a date by a number of specific units
"""
date_increment_dispatcher = {
    DateIncrementUnit.MONTH: month_increment
}


def increment_period(date, num_units, unit_type: DateIncrementUnit):
    increment_method = date_increment_dispatcher[unit_type]
    ret = increment_method(date, num_units)

    return ret
