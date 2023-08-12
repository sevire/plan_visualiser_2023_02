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
    """
    Increments a date by a number of days.

    Must be an integer number of days.  If the value passed in is not an int then take the floor of the value.
    :param in_date:
    :param num_days:
    :return:
    """
    if not isinstance(num_days, int):
        num_days = int(num_days)
    return in_date + relativedelta(days=num_days)


def num_months_between_dates(start_date, end_date):
    r = relativedelta(end_date, start_date)
    return r.years * 12 + r.months + 1


def proportion_between_dates(start_date, end_date, proportion):
    """
    Returns a date which is proportion of the way between start_date and end_date
    :param start_date:
    :param end_date:
    :param proportion:
    :return:
    """
    num_days = days_between_dates(start_date, end_date)
    num_days_to_add = num_days * proportion
    ret = day_increment(start_date, num_days_to_add)

    return ret


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

class DatePlotter:
    """
    Utility class which helps with calculating the x-coordinate for a visual.
    """
    def __init__(self, earliest_date: datetime.date, latest_date: datetime.date, x_plot_start: float, x_plot_end: float):
        """
        Sets up by working out the number of days the activities cover based on the supplied list of start and end
        dates.

        Then for a given date it calculates the x value to use when plotting on the visual.

        """
        self.latest_date = latest_date
        self.earliest_date = earliest_date
        self.num_days_in_visual = self.num_days_between_dates(earliest_date, latest_date)
        self.x_plot_start = x_plot_start
        self.x_plot_end = x_plot_end

    @property
    def activity_plot_width(self):
        return self.x_plot_end - self.x_plot_start

    @staticmethod
    def get_earliest_latest_dates(activities:[]):
        """
        Get earliest start date and latest end date from list of tuples of start and end date

        :param activities:
        :return:
        """
        earliest_date = min([start_date for start_date, _ in activities])
        latest_date = max([end_date for _, end_date in activities])

        return earliest_date, latest_date


    @staticmethod
    def num_days_between_dates(start_date, end_date):
        num_days = end_date - start_date + timedelta(days=1)

        return num_days

    def x_coordinate_for_date(self, date: datetime.date, end_flag = False, mid_point=False) -> float:
        """
        Calculates the x coordinate for a given date within the visual.

        Note that as a date isn't a point but an interval, and the x coordinate can be used to represent either
        the start of the day (start_date) or the end of the day (end_date) the end_flag is used to indicate
        which case is required.

        :param date:
        :param end_flag:
        :return:
        """

        additional_amount = timedelta(days=0)
        if end_flag:
            additional_amount = timedelta(days=1)
        elif mid_point:
            additional_amount = timedelta(hours=12)

        day_number_in_activities = date - self.earliest_date + additional_amount
        proportion_of_width = day_number_in_activities / self.num_days_in_visual
        x = self.x_plot_start + proportion_of_width * self.activity_plot_width

        return x

    def left(self, date: datetime.date):
        return self.x_coordinate_for_date(date)

    def width(self, start_date: datetime.date, end_date: datetime.date):
        width = self.x_coordinate_for_date(end_date, end_flag=True) - self.left(start_date)

        return width

    def midpoint(self, date):
        """
        Used mostly for plotting milestones (probably) - calculates the mid-point of a given day.

        :param date:
        :return:
        """
        midpoint = self.x_coordinate_for_date(date, mid_point=True)
        return midpoint

