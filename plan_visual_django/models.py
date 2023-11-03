from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint
from plan_visual_django.services.general.date_utilities import date_from_string
from plan_visual_django.services.plan_file_utilities.plan_parsing import extract_summary_plan_info


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

        return mapped_compulsory_fields.count() == expected_compulsory_fields.count()


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

        return f'{self.plan_field_mapping_type}:{self.mapped_field}:{self.input_field_name}:{self.input_field_type}'


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
    file_name = models.CharField(max_length=100)
    file = models.FileField(upload_to="plan_files", null=True)
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

    def get_visual_activities(self, to_dict=True, include_disabled=False):
        """
        Only return activities which have been selected for this visual.

        Note the visual activities only include the attributes which are relevant to formatting the visual.  The actual
        activity information (such as name, start_date etc.) is stored in the plan accessed by the unique id.

        :return:
        """
        # First get all the visual activity records for this visual (which are enabled)
        if include_disabled:
            activities = self.visualactivity_set.all()
        else:
            activities = self.visualactivity_set.filter(enabled=True)

        # If caller doesn't need the data as a dict then just return the queryset
        if not to_dict:
            return activities

        # Now consolidate them into an array of dicts (not using comprehension for this is it's likely to be unreadable)
        # ToDo: Look for ways to simplify and improve performance of consolidation of activity data
        activities_consolidated = []
        for activity in activities:
            activity_record = {}
            # Get the record from the plan for this visual to get at the plan data (dates etc.)
            plan_activity = PlanActivity.objects.get(plan_id=self.plan_id, unique_sticky_activity_id=activity.unique_id_from_plan)

            # Now set up each field we want to be included

            # Start with the positioning and formatting fields for this activity
            activity_record['unique_id_from_plan'] = activity.unique_id_from_plan
            activity_record['swimlane'] = activity.swimlane.swim_lane_name
            activity_record['plotable_shape'] = activity.plotable_shape.name

            activity_record['vertical_positioning_type'] = activity.get_vertical_positioning_type()
            activity_record['vertical_positioning_value'] = activity.vertical_positioning_value
            activity_record['height_in_tracks'] = activity.height_in_tracks
            activity_record['text_horizontal_alignment'] = activity.get_horizontal_alignment()
            activity_record['text_vertical_alignment'] = activity.get_vertical_alignment()
            activity_record['text_flow'] = activity.get_text_flow()
            activity_record['plotable_style'] = activity.plotable_style

            # Now add the plan activity record data for this activity
            activity_record['activity_name'] = plan_activity.activity_name
            activity_record['milestone_flag'] = plan_activity.milestone_flag
            activity_record['start_date'] = plan_activity.start_date
            activity_record['end_date'] = plan_activity.end_date
            activity_record['level'] = plan_activity.level

            activities_consolidated.append(activity_record)

        return activities_consolidated

    def get_earliest_date(self):
        pass

    def get_latest_date(self):
        pass


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

    def get_timeline_label_type(self) -> TimelineLabelType:
        return self.TimelineLabelType(self.timeline_type)


class SwimlaneForVisual(models.Model):
    plan_visual = models.ForeignKey(PlanVisual, on_delete=models.CASCADE)
    swim_lane_name = models.CharField(max_length=51)
    plotable_style = models.ForeignKey(PlotableStyle, on_delete=models.CASCADE)
    sequence_number = models.IntegerField()

    class Meta:
        unique_together = ('plan_visual', 'swim_lane_name')
        ordering = ['plan_visual', 'sequence_number']

    def __str__(self):
        return self.swim_lane_name

    def get_next_unused_track_number(self):
        """
        Returns the next track number to be used for a new activity in the given swimlane.
        :return:
        """
        if self.visualactivity_set.count() > 0:
            max_track_number = max([activity.vertical_positioning_value for activity in self.visualactivity_set.all()])
            return max_track_number + 1
        else:
            return 1


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
    def get_text_flow(self) -> TextFlow:
        return self.TextFlow(self.text_flow)

    def get_vertical_positioning_type(self) -> VerticalPositioningType:
        return self.VerticalPositioningType(self.vertical_positioning_type)

    def get_horizontal_alignment(self) -> HorizontalAlignment:
        return self.HorizontalAlignment(self.text_horizontal_alignment)

    def get_vertical_alignment(self) -> VerticalAlignment:
        return self.VerticalAlignment(self.text_vertical_alignment)

    def to_json(self, plot_parameters):
        # Hard code during development
        plot_parameters = {
            'min_date': date_from_string('01/01/2023'),
            'max_date': date_from_string('12/01/2023'),
            'visual_top': 0,
            'visual_left': 0,
            'visual_width': 400,
            'visual_height': 200,
            'track_height': 10,
            'track_gap': 2
        }
        # ToDo: Come back and finish activity.to_json()


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