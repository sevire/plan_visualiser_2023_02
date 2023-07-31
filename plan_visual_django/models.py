from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint
from plan_visual_django.services.general.date_utilities import date_from_string


class PlanField(models.Model):
    """
    Includes an entry for each field which is required (or optional) for each activity within the plan.

    The field names defined here need map directly on to the variable names for each field used within the app, so
    these need to be maintained to be consistent with the code.

    To do this I've restricted the choices for the field, but allowed other attributes to be entered.
    """

    # Classes to support Enums which drive Choices in the model and can be used in code. Neat!
    class PlanFieldName(models.TextChoices):
        STICKY_UID = "unique_sticky_activity_id", 'Unique id for activity'
        NAME = "activity_name", 'Name of activity'
        DURATION = "duration", 'Duration of activity'
        START = "start_date", 'Start date of activity'
        END = "end_date", 'End date of activity'
        LEVEL = "level", 'The level in the hierarchy of the an activity'

    class StoredPlanFieldType(models.TextChoices):
        INTEGER = "INT", "Integer"
        STRING = "STR", "String"
        DATE = "DATE", "Date (without time)"

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
    def plan_headings():
        headings = [field.field_name for field in PlanField.objects.all()]
        return headings


class PlanFieldMappingType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.name


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
    original_file_name = models.CharField(max_length=100)
    file = models.FileField(upload_to="plan_files", null=True)
    file_type = models.ForeignKey(FileType, on_delete=models.CASCADE)

    class Meta:
        constraints: list[UniqueConstraint] = \
            [UniqueConstraint(fields=['user', 'original_file_name'], name="unique_filename_for_user")]

    def __str__(self):
        return f'{self.original_file_name}:{self.file_type}'


class PlanActivity(models.Model):
    """
    When a new plan is added, read in all the activities as a base which the various
    visuals can be based upon.  Only store the fields which are relevant to the plan.
    """
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    unique_sticky_activity_id = models.CharField(max_length=50)
    activity_name = models.CharField(max_length=200)
    duration = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    level = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = " Plan activities"

    def __str__(self):
        return f'{self.activity_name:.20}'


class Color(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    red = models.IntegerField(null=False, default=0)
    green = models.IntegerField(null=False, default=0)
    blue = models.IntegerField(null=False, default=0)
    alpha = models.FloatField(null=False, default=0)

    class Meta:
        constraints = [
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

    def __str__(self):
        return f"([{self.name}]-{self.red},{self.green},{self.blue},{self.alpha})"


class Font(models.Model):
    font_name = models.CharField(max_length=100)

    def __str__(self):
        return self.font_name


class PlotableStyle(models.Model):
    style_name = models.CharField(max_length=100)
    fill_color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name="plotablestyle_fill")
    line_color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name="plotablestyle_line")
    font_color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name="plotablestyle_font")
    line_thickness = models.IntegerField()
    font = models.ForeignKey(Font, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.style_name}, fill:{self.fill_color.name}, line:{self.line_color.name}'


class PlotableShapeType(models.Model):
    """
    Eek! I'm struggling to remember why I had ShapeType and Shape!  I'm guessing that it was something like the
    fact that certain families of shapes use a similar set of parameters to plot them.  So for example
    a lot (most or all in practice I suspect) of shapes are plotted by specifying...

    top, left, width, height

    so there will be a family of shapes with that shape type.

    """

    class PlotableShapeTypeName(models.TextChoices):
        RECTANGLE = "RECTANGLE", "Rectangle"
        ROUNDED_RECTANGLE = "ROUNDED_RECTANGLE", "Rectangle"
        DIAMOND = "DIAMOND", "Diamond"
        ISOSCELES_TRIANGLE = "ISOSCELES", "Isosceles Triangle"

    name = models.CharField(max_length=20, choices=PlotableShapeTypeName.choices)

    def __str__(self):
        return f'{self.name}'

    def get_plotable_shape_type(self):
        return self.PlotableShapeTypeName(self.name)


class PlotableShape(models.Model):
    shape_type = models.ForeignKey(PlotableShapeType, on_delete=models.CASCADE)

    def __str__(self):
        return self.shape_type.name

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

    def __str__(self):
        return f"{self.name}"

    def get_visual_activities(self):
        """
        Only return activities which have been selected for this visual.

        Note the visual activities only include the attributes which are relevant to formatting the visual.  The actual
        activity information (such as name, start_date etc.) is stored in the plan accessed by the unique id.

        :return:
        """
        # First get all the visual activity records for this visual (which are enabled)
        activities = self.visualactivity_set.filter(enabled=True)

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
            activity_record['plotable_shape'] = activity.plotable_shape.shape_type.name

            activity_record['vertical_positioning_type'] = activity.get_vertical_positioning_type()
            activity_record['vertical_positioning_value'] = activity.vertical_positioning_value
            activity_record['height_in_tracks'] = activity.height_in_tracks
            activity_record['text_horizontal_alignment'] = activity.get_horizontal_alignment()
            activity_record['text_vertical_alignment'] = activity.get_vertical_alignment()
            activity_record['text_flow'] = activity.get_text_flow()
            activity_record['plotable_style'] = activity.plotable_style

            # Now add the plan activity record data for this activity
            activity_record['activity_name'] = plan_activity.activity_name
            activity_record['duration'] = plan_activity.duration
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
DEFAULT_PLOTABLE_STYLE_NAME = "(default)"