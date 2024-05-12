from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint, Max, Min, Sum
from plan_visual_django.services.general.date_utilities import DatePlotter
from plan_visual_django.services.plan_file_utilities.plan_parsing import extract_summary_plan_info
from plan_visual_django.services.visual.plotables import get_plotable
from plan_visual_django.services.visual.visual_elements import Timeline


class PlanField(models.Model):
    """
    Includes an entry for each field which is required (or optional) for each activity within the plan.

    The field names defined here need map directly on to the variable names for each field used within the app, so
    these need to be maintained to be consistent with the code.

    To do this I've restricted the choices for the field, but allowed other attributes to be entered.
    """

    # Classes to support Enums which drive Choices in the model and can be used in code. Neat!
    class PlanFieldName(models.TextChoices):
        STICKY_UID = "unique_sticky_activity_id", True, 'Unique id for activity'
        NAME = "activity_name", True, 'Name of activity'
        DURATION = "duration", False, 'Work effort for activity (not stored, used to work out whether this is a milestone)'
        MILESTONE_FLAG = "milestone_flag", True, 'Is this activity a milestone'
        START = "start_date", True, 'Start date of activity'
        END = "end_date", True, 'End date of activity'
        LEVEL = "level", True, 'The level in the hierarchy of the an activity'


        """
        Controls creation of a PlanFieldName object so that it stores the 
        """
        def __new__(cls, value, is_stored):
            obj = str.__new__(cls, value)
            obj._value_ = value
            obj.is_stored = is_stored
            return obj

    class StoredPlanFieldType(models.TextChoices):
        INTEGER = "INT", "Integer"
        STRING = "STR", "String"
        DATE = "DATE", "Date (without time)"
        BOOL = "BOOL", "Boolean"

    field_name = models.CharField(max_length=50, choices=PlanFieldName.choices, help_text="field name used in common datastructure for plan")
    field_type = models.CharField(max_length=20, choices=StoredPlanFieldType.choices)
    field_description = models.TextField(max_length=1000)
    required_flag = models.BooleanField(default=True)
    sort_index = models.IntegerField()

    class Meta:
        ordering = ('sort_index', )

    def get_plan_field_name(self):
        return self.PlanFieldName(self.field_name)

    def get_stored_plan_field_type(self):
        return self.StoredPlanFieldType(self.field_type)
    def __str__(self):
        return f'{self.field_name}:{self.field_type}'

    @staticmethod
    def plan_headings(include_not_stored=False):
        headings = [field.field_name for field in PlanField.objects.all() if field.get_plan_field_name().is_stored is True]
        return headings


class PlanFieldMappingType(models.Model):
    """
    Schema which defines how input fields from a plan are mapped to stored fields for that plan.
    In practice there will be a PlanMappedField record for every input field which references
    the appropriate mapping type as a foreign key.
    """
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.name

    def is_complete(self):
        """
        Checks whether all the compulsoary fields have a mapping.
        :return:
        """
        mapped_compulsory_fields = self.planmappedfield_set.filter(mapped_field__required_flag=True)
        expected_compulsory_fields = PlanField.objects.filter(required_flag=True)

        mapped_count = mapped_compulsory_fields.count()
        expected_count = expected_compulsory_fields.count()

        return mapped_count == expected_count


class PlanMappedField(models.Model):
    class PlanFieldType(models.TextChoices):
        INTEGER = "INT", "Integer"
        FLOAT = "FLOAT", "Decimal Number"
        STRING = "STR", "String"
        STRING_OR_INT = "STR_OR_INT", "String or integer"
        STRING_nnd = "STR_nnd", "String of form nnd where nn is an integer value"
        STRING_nn_Days = "STR_duration_msp", "String representing duration from MSP project in Excel"
        STRING_DATE_DMY_01 = "STR_DATE_DMY_01", "String of form dd MMM YYYY"
        STRING_DATE_DMY_02 = "STR_DATE_DMY_02", "String of form dd MMMMM YYYY HH:MM"
        STRING_MILESTONE_YES_NO = "STR_MSTONE_YES_NO", "Milestone flag as string, Yes or No"
        DATE = "DATE", "Date (without time)"

    plan_field_mapping_type = models.ForeignKey(PlanFieldMappingType, on_delete=models.CASCADE)
    mapped_field = models.ForeignKey(PlanField, on_delete=models.CASCADE)
    input_field_name = models.CharField(max_length=50)
    input_field_type = models.CharField(max_length=20, choices=PlanFieldType.choices)

    def get_plan_field_type(self):
        return self.PlanFieldType(self.input_field_type)

    def __str__(self):

        return f'{self.plan_field_mapping_type}:{self.mapped_field} -> {self.input_field_name}:{self.input_field_type}'


class FileType(models.Model):
    """
    Each plan is assigned a given file type, which encapsulates two properties of the plan, which are:
    - What is the technical format that the plan is provided in, which is needed in order to dispatch the file
      to the right logic to read it correctly.
    - What is the mapping schema for the plan, which maps input fields to the fields needed in the app which
      define the plan.

    NOTE: At the time of writing we only support Excel input files so we only need to store the mapping type
          for now.

    The File Type describes the technical format within which the plan data is expected to be provided for a given plan.
    """
    file_type_name = models.CharField(max_length=50)
    file_type_description = models.CharField(max_length=100)
    plan_field_mapping_type = models.ForeignKey(PlanFieldMappingType, on_delete=models.CASCADE)

    def __str__(self):
        return self.file_type_name


class Plan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Upload files into folder under MEDIA_ROOT
    plan_name = models.CharField(max_length=100)  # Name for this plan - independent of file name.
    file_name = models.CharField(max_length=100)  # Name of file uploaded (may be stored with different name to make unique)
    file = models.FileField(upload_to="plan_files", null=True)  # Includes a File object pointing to the actual file to be parsed
    file_type = models.ForeignKey(FileType, on_delete=models.CASCADE)

    class Meta:
        constraints: list[UniqueConstraint] = \
            [UniqueConstraint(fields=['user', 'plan_name'], name="unique_filename_for_user")]

    def __str__(self):
        return f'{self.plan_name}({self.file_name}:{self.file_type})'

    def get_plan_summary_data(self):
        """
        Extracts summary information from the plan. This is used to populate the plan summary page.
        """
        summary = extract_summary_plan_info(self)
        return summary


class PlanActivity(models.Model):
    """
    When a new plan is added, read in all the activities as a base which the various
    visuals can be based upon.  Only store the fields which are relevant to the plan.
    """
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    unique_sticky_activity_id = models.CharField(max_length=50)
    activity_name = models.CharField(max_length=200)
    milestone_flag = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    level = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = " Plan activities"

    def __str__(self):
        return f'{self.activity_name:.20}'


class Color(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    red = models.IntegerField(null=False, default=0)
    green = models.IntegerField(null=False, default=0)
    blue = models.IntegerField(null=False, default=0)
    alpha = models.FloatField(null=False, default=0)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'name'], name="unique-color-name-for-user"),
            models.CheckConstraint(
                check=models.Q(red__gte=0) & models.Q(red__lte=255),
                name="Red component must be between 0 and 255 (inclusive)",
            ),
            models.CheckConstraint(
                check=models.Q(green__gte=0) & models.Q(green__lte=255),
                name="Green component must be between 0 and 255 (inclusive)",
            ),
            models.CheckConstraint(
                check=models.Q(blue__gte=0) & models.Q(blue__lte=255),
                name="Blue component must be between 0 and 255 (inclusive)",
            ),
            models.CheckConstraint(
                check=models.Q(alpha__gte=0) & models.Q(alpha__lte=1),
                name="Alpha value must be between 0 and 1",
            ),
        ]

        ordering = ["user", "name"]

    def __str__(self):
        return f"{self.name}"

    def to_dict(self):
        """
        Returns a dictionary for use in API calls. Assumes that use case is for fillStyle in Canvas for now
        :return:
        """
        return f"rgb({self.red},{self.green},{self.blue})"


class Font(models.Model):
    font_name = models.CharField(max_length=100)

    def __str__(self):
        return self.font_name


class PlotableStyle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    style_name = models.CharField(max_length=100)
    fill_color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name="plotablestyle_fill")
    line_color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name="plotablestyle_line")
    font_color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name="plotablestyle_font")
    line_thickness = models.IntegerField()
    font = models.ForeignKey(Font, on_delete=models.PROTECT)
    font_size = models.IntegerField(default=10)  # Font size in points (probably!)

    class Meta:
        ordering = ["user", "style_name"]
        constraints = [
            UniqueConstraint(fields=['user', 'style_name'], name="unique-style-name-for-user")
        ]

    def __str__(self):
        return f'{self.style_name}, fill:{self.fill_color.name}, line:{self.line_color.name}'

    def to_dict(self):
        """
        Create dict structure which can be converted to JSON for use in API calls.
        :return:
        """
        return {
            "user": self.user.username,
            "style_name": self.style_name,
            "fill_color": self.fill_color.to_dict(),
            "line_color": self.line_color.to_dict(),
            "font_color": self.font_color.to_dict(),
            "line_thickness": self.line_thickness,
            "font": self.font.font_name,
            "font_size": self.font_size
        }

    def font_render_string(self):
        """
        Returns string representing the size and font, which can be used for rendering in Canvas and (probably) other
        formats.

        :return:
        """
        return f"{self.font_size}px {self.font.font_name}"


class PlotableShapeType(models.Model):
    """
    I'm re-factoring this as I move the app to a server for alpha testing.  I'm struggling to remember how I originally
    envisaged this working but I have decide how I now think it should work and am re-working around that.

    So...

    A Shape Type is a category which indicates the way a shape is defined.  For example, almost every shape
    I will use in the visual (or even every shape) will be based around a rectangle and be defined by the scheme:

    - top
    - left
    - width
    - height

    There may be additional parameters which impact things like corner radius for a rounded rectangle which
    will be added through shape specific models.

    At some point I may introduce more sophisticate shape types, to allow less regular shapes to be used (although I'm
    not sure whether that will really be necessary), such as shapes defined by a set of points, or svg shapes.

    Then each shape will fit into one of the defined shape types.
    """
    name = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.name}'


class PlotableShape(models.Model):
    class PlotableShapeName(models.TextChoices):
        RECTANGLE = "RECTANGLE", "Rectangle"
        ROUNDED_RECTANGLE = "ROUNDED_RECTANGLE", "Rounded Rectangle"
        DIAMOND = "DIAMOND", "Diamond"
        ISOSCELES_TRIANGLE = "ISOSCELES", "Isosceles Triangle"

    shape_type = models.ForeignKey(PlotableShapeType, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=PlotableShapeName.choices)

    def get_plotable_shape(self):
        return self.PlotableShapeName(self.name)

    def __str__(self):
        return self.name

    def to_json(self):
        return self.shape_type


class PlotableShapeAttributesRectangle(models.Model):
    plotable_shape = models.ForeignKey(PlotableShape, on_delete=models.CASCADE)
    width = models.FloatField()
    height = models.FloatField()


class PlotableShapeAttributesDiamond(models.Model):
    plotable_shape = models.ForeignKey(PlotableShape, on_delete=models.CASCADE)
    width = models.FloatField()
    height = models.FloatField()


class PlanVisual(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100)
    width = models.FloatField(default=30)
    max_height = models.FloatField(default=20)
    include_title = models.BooleanField(default=True)
    track_height = models.FloatField(default=20)
    track_gap = models.FloatField(default=4)
    milestone_width = models.FloatField(default=10)
    swimlane_gap = models.FloatField(default=5)
    default_milestone_shape = models.ForeignKey(PlotableShape, on_delete=models.CASCADE, related_name="default_milestone_shape")
    default_activity_shape = models.ForeignKey(PlotableShape, on_delete=models.CASCADE, related_name="default_activity_shape")
    default_activity_plotable_style = models.ForeignKey(PlotableStyle, on_delete=models.CASCADE, related_name="default_activity_plotable_style")
    default_milestone_plotable_style = models.ForeignKey(PlotableStyle, on_delete=models.CASCADE, related_name="default_milestone_plotable_style")
    default_swimlane_plotable_style = models.ForeignKey(PlotableStyle, on_delete=models.CASCADE, related_name="default_swimlane_plotable_style")

    class Meta:
        unique_together = ["plan", "name"]

    def __str__(self):
        return f"{self.name}"

    def activity_count(self, include_disabled=False):
        """
        Counts number of activities included within this visual.  Usually we don't want those which are disabled as they
        are not currently in the visual, but there is a flag to override this.

        :param include_disabled:
        :return:
        """
        if include_disabled is False:
            return self.visualactivity_set.filter(enabled=True).count()
        else:
            return self.visualactivity_set.all().count()

    def get_visual_activity(self, unique_id):
        visual_activity = self.visualactivity_set.filter(unique_id_from_plan=unique_id)[0]
        activity_record = {}
        # Get the record from the plan for this visual to get at the plan data (dates etc.)
        plan_activity = PlanActivity.objects.get(plan_id=self.plan_id,
                                                 unique_sticky_activity_id=visual_activity.unique_id_from_plan)

        # Now set up each field we want to be included

        # Start with the positioning and formatting fields for this activity
        activity_record['enabled'] = visual_activity.enabled
        activity_record['unique_id_from_plan'] = visual_activity.unique_id_from_plan
        activity_record['swimlane'] = visual_activity.swimlane.swim_lane_name
        activity_record['plotable_shape'] = visual_activity.plotable_shape.name

        activity_record['vertical_positioning_type'] = visual_activity.get_vertical_positioning_type()
        activity_record['vertical_positioning_value'] = visual_activity.vertical_positioning_value
        activity_record['height_in_tracks'] = visual_activity.height_in_tracks
        activity_record['text_horizontal_alignment'] = visual_activity.get_horizontal_alignment()
        activity_record['text_vertical_alignment'] = visual_activity.get_vertical_alignment()
        activity_record['text_flow'] = visual_activity.get_text_flow()
        activity_record['plotable_style'] = visual_activity.plotable_style.to_dict()

        # Now add the plan activity record data for this activity
        activity_record['activity_name'] = plan_activity.activity_name
        activity_record['milestone_flag'] = plan_activity.milestone_flag

        activity_record['start_date'] = plan_activity.start_date.isoformat()
        activity_record['end_date'] = plan_activity.end_date.isoformat()
        activity_record['level'] = plan_activity.level

        return activity_record

    def get_visual_activities(self, to_dict=True, include_disabled=False):
        """
        Only return activities which have been selected for this visual.

        Note the visual activities only include the attributes which are relevant to formatting the visual.  The actual
        activity information (such as name, start_date etc.) is stored in the plan accessed by the unique id.

        :return:
        """
        # First get all the visual activity records for this visual (which are enabled)
        if include_disabled:
            activities = self.visualactivity_set()
        else:
            activities = self.visualactivity_set.filter(enabled=True)

        # If caller doesn't need the data as a dict then just return the queryset
        if not to_dict:
            return activities

        activity_unique_ids = list(activities.values('unique_id_from_plan'))
        # Now consolidate them into an array of dicts (not using comprehension for this is it's likely to be unreadable)
        # ToDo: Look for ways to simplify and improve performance of consolidation of activity data
        activities_consolidated = [self.get_visual_activity(activity["unique_id_from_plan"]) for activity in activity_unique_ids]
        return activities_consolidated

    def get_visual_earliest_latest_plan_date(self):
        """
        Returns the earliest start date and the latest end date for all activities in the plan.  Doesn't adjust for
        timelines!

        :return:
        """
        earliest_start_date = min(visual_activity.get_plan_activity().start_date for visual_activity in self.visualactivity_set.all())
        latest_end_date = max(visual_activity.get_plan_activity().end_date for visual_activity in self.visualactivity_set.all())

        return earliest_start_date, latest_end_date

    def get_visual_earliest_latest_date(self):
        """
        Returns the earliest date of all activities included in the visual, adjusted to take account of the dates
        covered by timelines - as the timelines will typically round up to a whole unit, such as month, week etc.
        :return:
        """
        # Get all unique_id_from_plan values for enabled VisualActivity objects related to this PlanVisual instance
        visual_ids = self.visualactivity_set.filter(enabled=True).values_list('unique_id_from_plan', flat=True)

        # Filter PlanActivity objects by plan and unique_sticky_activity_id(from the previous query),
        # then get the minimum start_date
        earliest_start_date = self.plan.planactivity_set.filter(unique_sticky_activity_id__in=visual_ids).aggregate(Min('start_date'))['start_date__min']
        latest_end_date = self.plan.planactivity_set.filter(unique_sticky_activity_id__in=visual_ids).aggregate(Max('end_date'))['end_date__max']

        timeline_records = self.timelineforvisual_set.all()

        # Create dictionary of timeline objects based on timeline data from database
        self.timeline_objects = {timeline.timeline_name: Timeline.from_data_record(earliest_start_date, latest_end_date, timeline) for timeline in timeline_records}

        # If there are no timelines, then the earliest and latest dates are based on which activities are in the visual.
        # Otherwise ask each timeline object to calculate its earliest and latest date and calculate the true start and end
        # date for the overall visual.
        if len(self.timeline_objects) == 0:
            visual_start_date_final = earliest_start_date
            visual_end_date_final = latest_end_date
        else:
            visual_start_date_final = min([start_date for start_date, end_date in [timeline.calculate_date_range() for timeline in self.timeline_objects.values()]])
            visual_end_date_final = max([end_date for start_date, end_date in [timeline.calculate_date_range() for timeline in self.timeline_objects.values()]])

        return visual_start_date_final, visual_end_date_final

    def get_timelines_height(self, sequence_num=None):
        """
        (SHOULD BE TEMPORARY)
        ToDo: Refactor to remove need for calculating Timeline height from visual.

        Work out height of all the timelines as this is required to calculate the position of
        swimlanes and activities.

        If sequence_num is provide then calculate the height of all the timelines not including the one
        with the supplied sequence number (used to calculate the top of current timeline)
        :return:
        """
        if sequence_num is None:
            timelines = self.timelineforvisual_set.all()
        else:
            timelines = self.timelineforvisual_set.filter(sequence_number__lt=sequence_num)
        timeline_height = timelines.aggregate(total_sum=Sum('timeline_height'))['total_sum'] or 0

        return timeline_height

    def get_timeline_plotables(self, sequence_number=None):
        """
        Works out dimensions for the timeline area on the visual.

        The timeline (at the moment) is positioned at the top of the visual and that is hard-coded into the
        logic.
        :param top:
        :param left:
        :param width:
        :param height:
        :return:
        """
        if sequence_number:
            timelines = self.timelineforvisual_set.filter(sequence_number__lt=sequence_number)
        else:
            timelines = self.timelineforvisual_set.all()

        timeline_plotables = [timeline.get_plotables() for timeline in timelines]
        return timeline_plotables

    def get_swimlane_plotables(self, sequence_number=None):
        if sequence_number:
            swimlanes = self.swimlaneforvisual_set.filter(sequence_number__lt=sequence_number)
        else:
            swimlanes = self.swimlaneforvisual_set.all()

        swimlane_plotables = [swimlane.get_plotable() for swimlane in swimlanes]
        return swimlane_plotables

    def get_visual_activity_plotables(self):
        """
        Returns plotables for all visual activities in this visual, not including activites
        which are not enabled.
        :return:
        """
        visual_activities = [visual_activity.get_plotable() for visual_activity in self.visualactivity_set.filter(enabled=True)]

        return visual_activities



    def get_swimlanesforvisual_dimensions(self, sequence_number=None, top=None, left=None, width=None, height=None):
        """
        Works out dimensions for area containing swimlanes in the visual.

        If sequence_number is specified then get the dimensions just of the area contain the swimlanes up to but
        not including the specified one.  Also don't include the final swimlane gap so that the dimensions only
        include the swimlanes themselves.  The caller will need to add a gap if calculating the dimensons for a
        swimlane which sits underneath those used in the calculation herein.

        Hard coding logic that the Timeline Labels will come above the swimlanes.  This is fine for now but
        maybe this should be more data driven.

        :param top:
        :param left:
        :param width:
        :param height:
        :return:
        """
        # First get height of timelines as the swimlanes sit below them.
        height_of_timelines = self.get_timelines_height()

        if sequence_number:
            swimlanes = self.swimlaneforvisual_set.filter(sequence_number__lt=sequence_number)
        else:
            swimlanes = self.swimlaneforvisual_set.all()
        num_swimlanes = len(swimlanes)
        total_gap = max(0, num_swimlanes-1) * self.swimlane_gap
        total_height_of_swimlanes = sum(swimlane.get_height() for swimlane in swimlanes)
        height_of_swimlane_area = total_height_of_swimlanes + total_gap

        return height_of_timelines, 0, self.width, height_of_swimlane_area

    def get_plotables(self):
        """
        Returns all plotable elements for the visual (and by recursion all sub-elements of those elements.

        Specifically, returns:
        - timelines (which will implicitly return timeline_labels)
        - swimlanes
        - visual activities

        :return:
        """
        plotables = {
            "timelines": self.get_timeline_plotables(),
            "swimlanes": self.get_swimlane_plotables(),
            "visual_activities": self.get_visual_activity_plotables()
        }
        return plotables



class TimelineForVisual(models.Model):
    class TimelineLabelType(models.TextChoices):
        MONTHS = "MONTHS", 'One label for each month'
        QUARTERS = "QUARTERS", 'One label for each sequence of three months, variable start'

    class TimelineLabelBandingType(models.TextChoices):
        NO_BANDING = "NO_BANDING", 'All labels the same style'
        ALTERNATE_AUTO_SHADE = "ALTERNATE_AUTO", "Alternate banding, second style automatically generated from first"
        ALTERNATE_SPECIFIED_COLOR = "ALTERNATE_SPECIFIC", "Alternate banding where both styles specified"

    plan_visual = models.ForeignKey(PlanVisual, on_delete=models.CASCADE)
    timeline_type = models.CharField(max_length=20, choices=TimelineLabelType.choices)
    timeline_name = models.CharField(max_length=50)
    timeline_height = models.FloatField(default=10)
    plotable_style = models.ForeignKey(PlotableStyle, on_delete=models.CASCADE)
    sequence_number = models.IntegerField()

    class Meta:
        unique_together = [
            ('plan_visual', 'sequence_number')
        ]
        ordering = ['plan_visual', 'sequence_number']

    def get_timeline_label_type(self) -> TimelineLabelType:
        return self.TimelineLabelType(self.timeline_type)

    def get_height(self):
        return self.timeline_height

    def get_plot_parameters(self, json_flag=False):
        """
        ToDo: Rethink whether I need get_plot_paramters for Timeline given refactor into Plotables
        Calculated the overall dimensions of a given Timeline - that is the dimensions of the imaginary
        rectangle that encloses all the Timeline labels.

        :param json_flag:
        :return:
        """
        plotables = self.get_plotables()

        timeline_enclosing_top = min(plotable.get_top() for plotable in plotables)
        timeline_enclosing_bottom = max(plotable.get_bottom() for plotable in plotables)
        timeline_enclosing_left = min(plotable.get_left() for plotable in plotables)
        timeline_enclosing_right = max(plotable.get_right() for plotable in plotables)

        timeline_enclosing_height = timeline_enclosing_bottom - timeline_enclosing_top
        timeline_enclosing_width = timeline_enclosing_right - timeline_enclosing_left

        return timeline_enclosing_top, timeline_enclosing_left, timeline_enclosing_width, timeline_enclosing_height

    def get_plotables(self):
        """
        Calculates the labels for a given timeline.  This involves:
        - Getting overall start and end date for the visual based on the activities and all the timelines (as timelines
          will round down and up to the nearest unit (month, quarter etc) depending upon the configuration of the timeline
        - Create a list of labels, each of which has a start and end date and a label.
        :return:
        """

        earliest_visual_date, latest_visual_date = self.plan_visual.get_visual_earliest_latest_date()

        timeline_settings = {}  # Don't think this is used but need to assign something for now.
        # ToDo: Go back and delete timeline_settings from Timeline classes as should just use data from model

        timeline = Timeline.from_data_record(
            earliest_visual_date,
            latest_visual_date,
            self,
        )

        timeline.initialise_collection()
        top_offset = self.plan_visual.get_timelines_height(sequence_num=self.sequence_number)
        collection = timeline.create_collection(visual_settings=self.plan_visual, timeline_settings=timeline_settings, top_offset=top_offset, left_offset=0)

        collection_as_plotables = [element.plot_element() for element in collection.collection]

        return collection_as_plotables


class SwimlaneForVisual(models.Model):
    plan_visual = models.ForeignKey(PlanVisual, on_delete=models.CASCADE)
    swim_lane_name = models.CharField(max_length=51)
    plotable_style = models.ForeignKey(PlotableStyle, on_delete=models.CASCADE)
    sequence_number = models.IntegerField()

    class Meta:
        unique_together = [
            ('plan_visual', 'swim_lane_name'),
            ('plan_visual', 'sequence_number')
        ]
        ordering = ['plan_visual', 'sequence_number']

    def __str__(self):
        return self.swim_lane_name

    def get_visual_activities(self, include_disabled=False, date_order=False):
        """
        Returns all the visual activities for this swimlane.
        :return:
        """
        if include_disabled:
            if date_order:
                activities = self.visualactivity_set.all()
            else:
                activities = self.visualactivity_set.all()
        else:
            if date_order:
                activities = self.visualactivity_set.filter(enabled=True)
            else:
                activities = self.visualactivity_set.filter(enabled=True)

        return activities

    def get_max_track(self, include_disabled=False):
        """
        Returns the maximum track number in this swimlane, by taking the max of all the track numbers for all the
        visual activities in the swimlane.

        Usually we won't include activities which are disabled as they won't show up on the visual but the
        include disabled flag allows this to be overridden.

        :param include_disabled:
        :return:
        """

        if self.get_visual_activities().count() > 0:
            max_value = self.get_visual_activities(include_disabled=include_disabled).aggregate(Max('vertical_positioning_value'))['vertical_positioning_value__max']
            return max_value
        else:
            return 0

    def get_next_unused_track_number(self):
        """
        Returns the next track number to be used for a new activity in the given swimlane.  Don't count disabled
        activities as they are not currently in the visual.
        :return:
        """
        return self.get_max_track() + 1

    def get_height_of_tracks(self, num_tracks):
        """
        Utility function which simply works out the height of an activity which spans multiple tracks, or the height
        of a number of tracks above the one we are working out the top for.
        :return:
        """
        height_of_tracks = num_tracks * self.plan_visual.track_height + max(0, num_tracks-1) * self.plan_visual.track_gap

        return height_of_tracks

    def get_top_of_track(self, track_number):
        """
        The top of a track in a swimlane is defined by:
        - The top of the swimlane
        - The height of all the previous tracks
        - Plus the track gap if this isn't the first track in the swimlane

        :param track_number:
        :return:
        """

        top_of_swimlane, _, _, _, _, _ = self.get_plotable().get_dimensions()

        # If this isn't the top track then add a gap after the previous one otherwise don't.
        additional_gap = 0 if track_number == 1 else self.plan_visual.track_gap

        top_of_track = top_of_swimlane + self.get_height_of_tracks(track_number-1) + additional_gap

        return top_of_track

    def get_height(self):
        """
        Calculates the height of this swimlane by working out how many tracks there are on the swimlane and then
        calculating based on track height and track gap.
        :return:
        """
        track_height = self.plan_visual.track_height
        track_gap = self.plan_visual.track_gap
        num_tracks = self.get_max_track()

        # If there are zero or 1 tracks than there are no track gaps.
        height = (num_tracks * track_height) + max(0, num_tracks - 1) * track_gap

        return height

    def get_plotable(self):
        dims_of_previous_swimlanes = self.plan_visual.get_swimlanesforvisual_dimensions(self.sequence_number)
        previous_s_lane_top, previous_s_lane_left, previous_s_lane_width, previous_s_lane_height = dims_of_previous_swimlanes

        # If height of all previous swimlanes is zero then this is the first visible swimlane so don't add a gap.
        gap = 0 if previous_s_lane_height == 0 else self.plan_visual.swimlane_gap

        # Top of this swimlane is top of previous + height of previous + swimlane gap.
        this_top = previous_s_lane_top + previous_s_lane_height + gap

        swimlane_plotable = get_plotable(
            PlotableShape.PlotableShapeName.RECTANGLE,  # Note for now swimlanes will always be rectangles so hard-code
            top=this_top,
            left=0,  # Hard-coding for now as nothing will appear to the left of the swimlane
            width=self.plan_visual.width,
            height=self.get_height(),
            format=self.plotable_style,
            text_vertical_alignment=VisualActivity.VerticalAlignment.TOP,
            text_flow=VisualActivity.TextFlow.FLOW_TO_RIGHT,
            text=self.swim_lane_name,
            external_text_flag=False  # Only relevant for VisualActivity
        )

        return swimlane_plotable

    def get_activity_plotables(self):
        """
        Returns an Iterable object with a Plotable object for each activity which sits within this swimlane.

        :return:
        """
        activity_plotables = []
        for activity in self.visualactivity_set.all():
            activity_plotables.append(activity.get_plotable())

        return activity_plotables


class VisualActivity(models.Model):
    """
    Entity which represents data about an activity which has been added to a specific visual.

    Note the information in this table is mostly around the formatting and layout of the activity rather than the
    plan related information such as start date, duration, which is held in the plan from which the visual has been
    created, via the "unique_id_from_plan" field.
    """

    # Django provided Enums to drive the choices for fixed dropdown values.  This is very neat!
    class TextFlow(models.TextChoices):
        FLOW_TO_LEFT = "LFLOW", 'Align right, flow to left'
        FLOW_TO_RIGHT = "RFLOW", 'Align left, flow to right'
        FLOW_WITHIN_SHAPE = "WSHAPE", 'Align centre, flow left/right'
        FLOW_CLIPPED = "CLIPPED", 'Align centre, clipped to shape'
        FLOW_CENTRE = "CENTRE", 'Align centre'

    class VerticalPositioningType(models.TextChoices):
        TRACK_NUMBER = "TRACK", 'Specify track #'
        RELATIVE_TRACK = "REL_TRACK", 'Specify relative to last positioned activity'
        AUTO = "AUTO", 'Automatic positioning'

    class HorizontalAlignment(models.TextChoices):
        LEFT = 'LEFT', 'Left',
        CENTER = 'CENTER', 'Center',
        RIGHT = 'RIGHT', 'Right'

    # ToDo: VerticalAlignment should sit outside VisualActivity as it applies to any plotable object.
    class VerticalAlignment(models.TextChoices):
        TOP = 'TOP', 'Top',
        MIDDLE = 'MIDDLE', 'Middle',
        BOTTOM = 'BOTTOM', 'Bottom'

    visual = models.ForeignKey(PlanVisual, on_delete=models.CASCADE)
    unique_id_from_plan = models.CharField(max_length=50)  # ID from imported plan which will not change
    enabled = models.BooleanField()
    swimlane = models.ForeignKey(SwimlaneForVisual, on_delete=models.CASCADE)
    plotable_shape = models.ForeignKey(PlotableShape, on_delete=models.CASCADE)
    vertical_positioning_type = models.CharField(max_length=20, choices=VerticalPositioningType.choices)
    vertical_positioning_value = models.FloatField()
    height_in_tracks = models.FloatField(default=1)
    text_horizontal_alignment = models.CharField(max_length=20, choices=HorizontalAlignment.choices)
    text_vertical_alignment = models.CharField(max_length=20, choices=VerticalAlignment.choices)
    text_flow = models.CharField(max_length=20, choices=TextFlow.choices)
    plotable_style = models.ForeignKey(PlotableStyle, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'visual activities'
        unique_together = ['visual', 'unique_id_from_plan']

    def __str__(self):
        return f'Visual:{self.visual.name} unique_plan_activity_id:{self.unique_id_from_plan}'

    # Several methods to return Enum value for relevant choice selection
    def get_plan_activity(self):
        plan_activity = self.visual.plan.planactivity_set.get(unique_sticky_activity_id=self.unique_id_from_plan)
        return plan_activity

    def get_text_flow(self) -> TextFlow:
        return self.TextFlow(self.text_flow)

    def get_vertical_positioning_type(self) -> VerticalPositioningType:
        return self.VerticalPositioningType(self.vertical_positioning_type)

    def get_horizontal_alignment(self) -> HorizontalAlignment:
        return self.HorizontalAlignment(self.text_horizontal_alignment)

    def get_vertical_alignment(self) -> VerticalAlignment:
        return self.VerticalAlignment(self.text_vertical_alignment)

    def get_plotable(self):
        """
        Works out plot parameters for this visual activity.  Does this by:
        - If the activity isn't enabled then it doesn't appear on the visual so return None
        - Get which swimlane the activity is in.
        - Get which track the activity is in.
        - Get how many tracks the activity will cover.

        The above allows us to work out where the top of the activity is and its height. Then...
        - Calculate left and width by calculating based on the details of the activities in the plan and
          the properties of the visual (width in particular).

        :return:
        """
        if self.enabled is not True:
            return None

        # Get swimlane this activity is in then work out its top.
        activity_top = self.swimlane.get_top_of_track(self.vertical_positioning_value)
        activity_height = self.swimlane.get_height_of_tracks(self.height_in_tracks)

        earliest_visual_date, latest_visual_date = self.visual.get_visual_earliest_latest_date()

        date_plotter = DatePlotter(
            earliest_visual_date,
            latest_visual_date,
            0,
            self.visual.width
        )
        plan_activity = self.get_plan_activity()

        if plan_activity.milestone_flag is True:
            # This is a milestone, so we plot in the middle of the day to the specified width for a milestone.
            left = date_plotter.midpoint(plan_activity.start_date) - self.visual.milestone_width / 2
            width = self.visual.milestone_width
        else:
            left = date_plotter.left(plan_activity.start_date)
            width = date_plotter.width(plan_activity.start_date, plan_activity.end_date)

        plotable = get_plotable(
            self.plotable_shape.name,
            top=activity_top,
            left=left,
            width=width,
            height=activity_height,
            format=self.plotable_style,
            text_vertical_alignment=self.get_vertical_alignment(),
            text_flow=self.get_text_flow(),
            text=self.get_plan_activity().activity_name,
            external_text_flag=True if self.get_plan_activity().milestone_flag else False
        )

        return plotable


# Defaults to use when creating a new visual before any formatting or layout has been done.
DEFAULT_SWIMLANE_NAME = "(default)"
DEFAULT_VERTICAL_POSITIONING_TYPE = VisualActivity.VerticalPositioningType.TRACK_NUMBER
DEFAULT_VERTICAL_POSITIONING_VALUE = 1
DEFAULT_HEIGHT_IN_TRACKS = 1
DEFAULT_TEXT_HORIZONTAL_ALIGNMENT = VisualActivity.HorizontalAlignment.LEFT
DEFAULT_TEXT_VERTICAL_ALIGNMENT = VisualActivity.VerticalAlignment.MIDDLE
DEFAULT_TEXT_FLOW = VisualActivity.TextFlow.FLOW_TO_LEFT
DEFAULT_PLOTABLE_SHAPE_NAME = "RECTANGLE"
DEFAULT_MILESTONE_PLOTABLE_SHAPE_NAME = "DIAMOND"
DEFAULT_PLOTABLE_STYLE_NAME = "(default)"
