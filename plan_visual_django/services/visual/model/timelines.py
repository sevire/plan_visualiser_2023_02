from abc import abstractmethod
from datetime import datetime, date
from plan_visual_django.services.general.date_utilities import DatePlotter, num_months_between_dates, month_increment, \
    last_day_of_month, first_day_of_month
from plan_visual_django.services.general.utilities import is_odd
from plan_visual_django.services.visual.rendering.visual_elements import VisualElementCollection, VisualElement
from plan_visual_django.services.visual.model.visual_settings import VisualSettings


class Timeline(VisualElementCollection):
    """
    Base class for any timeline.

    There is a bit of circular logic at play here.  A timeline can work out what it's start and end date would need
    to be based on the start and end dates of all the activities to be plotted.

    BUT: The different timelines will require different start and end dates as they need to align onto a specific
    unit, such as Quarter.

    Therefore, the dates which are passed in are the input dates, which the Timeline then uses to calculate and pass
    back the adjusted start and end dates for THIS timeline.  The caller will collect this information for all the
    different timelines and then set the visual start and end date which is what the Timeline will use to calculate
    it's actual Visual Elements.
    """
    def __init__(self, activity_start_date:datetime.date, activity_end_date:datetime.date, timeline_record):
        super().__init__()
        self.activity_start_date:date = activity_start_date
        self.activity_end_date:date = activity_end_date
        self.timeline_record = timeline_record

        self.visual_start_date:date|None = activity_start_date  # Will be set from outside orchestration logic.  Can't plot without.
        self.visual_end_date:date|None = activity_end_date  # Will be set from outside orchestration logic.  Can't plot without.

    @abstractmethod
    def calculate_date_range(self) -> (date, date):
        """
        Each timeline will need to calculate the start and end date for itself based on what type of timeline it is.

        :return: timeline_start_date, timeline_end_date
        """
        pass

    @classmethod
    def from_data_record(cls, start_date:date, end_date:date, timeline):
        """
        Works out which type of timeline to create based upon the type passed in the Timeline record from db, and
        then creates and returns that timeline.

        :param end_date:
        :param start_date:
        :param timeline:
        :return:
        """
        from plan_visual_django.models import TimelineForVisual
        if timeline.timeline_type == TimelineForVisual.TimelineLabelType.MONTHS:
            return MonthTimeline(start_date, end_date, timeline)
        elif timeline.timeline_type == TimelineForVisual.TimelineLabelType.QUARTERS:
            return QuarterTimeline(start_date, end_date, timeline)
        elif timeline.timeline_type == TimelineForVisual.TimelineLabelType.HALF_YEAR:
            return HalfYearTimeline(start_date, end_date, timeline)
        elif timeline.timeline_type == TimelineForVisual.TimelineLabelType.YEAR:
            return YearTimeline(start_date, end_date, timeline)


class MonthTimeline(Timeline):
    def __init__(self, start_date: datetime.date, end_date: datetime.date, timeline_record):
        super().__init__(start_date, end_date, timeline_record)

    def create_collection(self, visual_settings, timeline_settings, top_offset=0, left_offset=0):
        """
        By the time this method is called, the calculate_date_range method will have been called to allow the
        orchestration logic to work out the range for the whole visual.

        :return:
        """
        x_plot_start = left_offset
        x_plot_end = visual_settings.width
        date_plotter = DatePlotter(self.visual_start_date, self.visual_end_date, x_plot_start, x_plot_end)

        num_periods = num_months_between_dates(self.visual_start_date, self.visual_end_date)
        for period_num in range(0, num_periods):
            period_start_date = month_increment(self.visual_start_date, period_num)
            period_end_date = last_day_of_month(period_start_date)

            # ToDo: Implement settings to specify format of month text
            text = period_start_date.strftime("%b-%y")

            left = date_plotter.left(period_start_date)
            width = date_plotter.width(period_start_date, period_end_date)

            height = self.timeline_record.timeline_height

            # ToDo: Refactor vertical alignment and text flow so it isn't defined inside VisualActivity
            # ToDo: Replace hard-coded vertical alignment and text flow with config from database

            element = VisualElement()

            from plan_visual_django.models import PlotableShape
            element.plotable_id = f"timeline-{self.timeline_record.id}-{period_num+1:03}"
            element.shape=PlotableShape.PlotableShapeName.RECTANGLE
            element.top=top_offset
            element.left=left + left_offset
            element.width=width
            element.height=height

            # There may not be an even label styling so if not use odd label styling
            if self.timeline_record.plotable_style_even is None:
                even_plotable_style = self.timeline_record.plotable_style_odd
            else:
                even_plotable_style = self.timeline_record.plotable_style_even

            # Choose style for label depending upon whether this is an odd or even numbered label
            if is_odd(period_num + 1):
                element.plotable_style=self.timeline_record.plotable_style_odd
            else:
                element.plotable_style=even_plotable_style

            from plan_visual_django.models import VisualActivity
            element.text_vertical_alignment=VisualActivity.VerticalAlignment.MIDDLE
            element.text_flow=VisualActivity.TextFlow.FLOW_CENTRE

            element.text=text
            element.external_text_flag=False

            self.add_visual_element(element)

        return self

    def calculate_date_range(self):
        """
        Method wich will be called so that calling orchestration logic can work out the start and end date for the
        whole visual, based on the start, end date for each specific timeline, based on the timeline unit.

        The first and last date from the activities within the visual will be passed in.

        Example: For a month timeline we just need to calculate the first of the first month and the last day of
        the last month.

        :return:
        """
        timeline_start_date = first_day_of_month(self.activity_start_date)
        timeline_end_date = last_day_of_month(self.activity_end_date)

        return timeline_start_date, timeline_end_date


class HalfYearTimeline(Timeline):
    def __init__(self, start_date: datetime.date, end_date: datetime.date, timeline_record):
        super().__init__(start_date, end_date, timeline_record)

    def create_collection(self, visual_settings, timeline_settings, top_offset=0, left_offset=0):
        """
        By the time this method is called, the calculate_date_range method will have been called to allow the
        orchestration logic to work out the range for the whole visual.

        :return:
        """
        x_plot_start = left_offset
        x_plot_end = visual_settings.width
        date_plotter = DatePlotter(self.visual_start_date, self.visual_end_date, x_plot_start, x_plot_end)

        num_periods = num_months_between_dates(self.visual_start_date, self.visual_end_date) // 6
        for period_num in range(0, num_periods):
            period_start_date = month_increment(self.visual_start_date, period_num * 6)
            period_end_date = last_day_of_month(month_increment(period_start_date, 6-1))

            # ToDo: Implement settings to specify format of month text
            text = f'{period_start_date.strftime("%b-%y")} - {period_end_date.strftime("%b-%y")}'

            left = date_plotter.left(period_start_date)
            width = date_plotter.width(period_start_date, period_end_date)

            height = self.timeline_record.timeline_height

            # ToDo: Refactor vertical alignment and text flow so it isn't defined inside VisualActivity
            # ToDo: Replace hard-coded vertical alignment and text flow with config from database

            element = VisualElement()

            from plan_visual_django.models import PlotableShape
            element.plotable_id = f"timeline-{self.timeline_record.id}-{period_num+1:03}"
            element.shape=PlotableShape.PlotableShapeName.RECTANGLE
            element.top=top_offset
            element.left=left + left_offset
            element.width=width
            element.height=height

            # There may not be an even label styling so if not use odd label styling
            if self.timeline_record.plotable_style_even is None:
                even_plotable_style = self.timeline_record.plotable_style_odd
            else:
                even_plotable_style = self.timeline_record.plotable_style_even

            # Choose style for label depending upon whether this is an odd or even numbered label
            if is_odd(period_num + 1):
                element.plotable_style=self.timeline_record.plotable_style_odd
            else:
                element.plotable_style=even_plotable_style

            from plan_visual_django.models import VisualActivity
            element.text_vertical_alignment=VisualActivity.VerticalAlignment.MIDDLE
            element.text_flow=VisualActivity.TextFlow.FLOW_CENTRE

            element.text=text
            element.external_text_flag=False

            self.add_visual_element(element)

        return self

    def calculate_date_range(self):
        """
        Method which will be called so that calling orchestration logic can work out the start and end date for the
        whole visual, based on the start, end date for each specific timeline, based on the timeline unit.

        The first and last date from the activities within the visual will be passed in.

        Example: For a month timeline we just need to calculate the first of the first month and the last day of
        the last month.

        For a six monthly timeline with no offset feature the timeline must begin in either January or July.


        :return:
        """
        start_month = self.activity_start_date.month
        end_month = self.activity_end_date.month

        increment = start_month % 6 -1

        timeline_start_date_adjusted = month_increment(self.activity_start_date, -increment)
        timeline_start_date = first_day_of_month(timeline_start_date_adjusted)

        end_stage_2 = end_month % 6 - 6

        timeline_end_date_adjusted = month_increment(self.activity_end_date, -end_stage_2)
        timeline_end_date = last_day_of_month(timeline_end_date_adjusted)

        return timeline_start_date, timeline_end_date


class YearTimeline(Timeline):
    def __init__(self, start_date: datetime.date, end_date: datetime.date, timeline_record):
        super().__init__(start_date, end_date, timeline_record)

    def create_collection(self, visual_settings, timeline_settings, top_offset=0, left_offset=0):
        """
        By the time this method is called, the calculate_date_range method will have been called to allow the
        orchestration logic to work out the range for the whole visual.

        :return:
        """
        x_plot_start = left_offset
        x_plot_end = visual_settings.width
        date_plotter = DatePlotter(self.visual_start_date, self.visual_end_date, x_plot_start, x_plot_end)

        num_periods = num_months_between_dates(self.visual_start_date, self.visual_end_date) // 12
        for period_num in range(0, num_periods):
            period_start_date = month_increment(self.visual_start_date, period_num * 12)
            period_end_date = last_day_of_month(month_increment(period_start_date, 12-1))

            # ToDo: Implement settings to specify format of month text
            text = f'{period_start_date.strftime("%Y")}'

            left = date_plotter.left(period_start_date)
            width = date_plotter.width(period_start_date, period_end_date)

            height = self.timeline_record.timeline_height

            # ToDo: Refactor vertical alignment and text flow so it isn't defined inside VisualActivity
            # ToDo: Replace hard-coded vertical alignment and text flow with config from database

            element = VisualElement()

            from plan_visual_django.models import PlotableShape
            element.plotable_id = f"timeline-{self.timeline_record.id}-{period_num+1:03}"
            element.shape=PlotableShape.PlotableShapeName.RECTANGLE
            element.top=top_offset
            element.left=left + left_offset
            element.width=width
            element.height=height

            # There may not be an even label styling so if not use odd label styling
            if self.timeline_record.plotable_style_even is None:
                even_plotable_style = self.timeline_record.plotable_style_odd
            else:
                even_plotable_style = self.timeline_record.plotable_style_even

            # Choose style for label depending upon whether this is an odd or even numbered label
            if is_odd(period_num + 1):
                element.plotable_style=self.timeline_record.plotable_style_odd
            else:
                element.plotable_style=even_plotable_style

            from plan_visual_django.models import VisualActivity
            element.text_vertical_alignment=VisualActivity.VerticalAlignment.MIDDLE
            element.text_flow=VisualActivity.TextFlow.FLOW_CENTRE

            element.text=text
            element.external_text_flag=False

            self.add_visual_element(element)

        return self

    def calculate_date_range(self):
        """
        Method which will be called so that calling orchestration logic can work out the start and end date for the
        whole visual, based on the start, end date for each specific timeline, based on the timeline unit.

        The first and last date from the activities within the visual will be passed in.

        Example: For a month timeline we just need to calculate the first of the first month and the last day of
        the last month.

        For a six monthly timeline with no offset feature the timeline must begin in either January or July.

        For a year timeline it's straightforward:
        - Start date is first day of first month of year of start_date.
        - End date is last day of last month of year of end_date


        :return:
        """
        timeline_start_date = self.activity_start_date.replace(day=1, month=1)
        timeline_end_date = last_day_of_month(self.activity_end_date.replace(month=12))

        return timeline_start_date, timeline_end_date


class QuarterTimeline(Timeline):
    def create_collection(self, visual_settings:VisualSettings, timeline_settings, top_offset=0, left_offset=0):
        x_plot_start = left_offset
        x_plot_end = visual_settings.width
        date_plotter = DatePlotter(self.visual_start_date, self.visual_end_date, x_plot_start, x_plot_end)

        num_periods = num_months_between_dates(self.visual_start_date, self.visual_end_date) // 3
        for period_num in range(0, num_periods):
            period_start_date = month_increment(self.visual_start_date, period_num * 3)
            period_end_date = last_day_of_month(month_increment(period_start_date, 3-1))

            # ToDo: Implement settings to specify format of month text
            text = f'{period_start_date.strftime("%b-%y")} - {period_end_date.strftime("%b-%y")}'

            left = date_plotter.left(period_start_date)
            width = date_plotter.width(period_start_date, period_end_date)

            height = self.timeline_record.timeline_height

            # ToDo: Refactor vertical alignment and text flow so it isn't defined inside VisualActivity
            # ToDo: Replace hard-coded vertical alignment and text flow with config from database

            element = VisualElement()

            from plan_visual_django.models import PlotableShape
            element.shape = PlotableShape.PlotableShapeName.RECTANGLE
            element.top = top_offset
            element.left = left + left_offset
            element.width = width
            element.height = height

            # There may not be an even label styling so if not use odd label styling
            if self.timeline_record.plotable_style_even is None:
                even_plotable_style = self.timeline_record.plotable_style_odd
            else:
                even_plotable_style = self.timeline_record.plotable_style_even

            # Choose style for label depending upon whether this is an odd or even numbered label
            if is_odd(period_num + 1):
                element.plotable_style=self.timeline_record.plotable_style_odd
            else:
                element.plotable_style=even_plotable_style

            from plan_visual_django.models import VisualActivity
            element.text_vertical_alignment = VisualActivity.VerticalAlignment.MIDDLE
            element.text_flow = VisualActivity.TextFlow.FLOW_CENTRE
            element.text = text
            element.external_text_flag = False

            self.add_visual_element(element)

        return self

    def __init__(self, start_date: datetime.date, end_date: datetime.date, timeline, month_offset=1):
        super().__init__(start_date, end_date, timeline)
        self.month_offset = month_offset

    def calculate_date_range(self):
        """
        For a quarter timeline we just need to calculate the start and end months and then the first and last day of
        those.  The month offset allows the caller to choose which months the quarters align to.

        :param offset:
        :return:
        """
        start_month = self.activity_start_date.month
        end_month = self.activity_end_date.month

        increment = (start_month - self.month_offset) % 3

        timeline_start_date_adjusted = month_increment(self.activity_start_date, -increment)
        timeline_start_date = first_day_of_month(timeline_start_date_adjusted)

        end_stage_1 = end_month - self.month_offset
        end_stage_2 = end_stage_1 % 3 - 2

        timeline_end_date_adjusted = month_increment(self.activity_end_date, -end_stage_2)
        timeline_end_date = last_day_of_month(timeline_end_date_adjusted)

        return timeline_start_date, timeline_end_date
