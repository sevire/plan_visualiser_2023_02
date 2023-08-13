from dataclasses import dataclass

from plan_visual_django.models import VisualActivity, PlotableShape, PlotableShapeType, PlanVisual
from plan_visual_django.services.visual.formatting import PlotableFormat, \
    LineFormat, PlotableColor, LineStyle, FillFormat


@dataclass
class SwimlaneSettings:
    """
    Holds key information which drives how swimlanes are laid out on the visual, including the order
    """
    swimlanes: []
    swimlane_gap: float = 5
    swimlane_formats: [PlotableFormat] = None  # Defines alternating formats where required for banded style visuals
    swimlane_label_horizontal_alignment: VisualActivity.HorizontalAlignment = VisualActivity.HorizontalAlignment.LEFT
    swimlane_label_vertical_alignment: VisualActivity.VerticalAlignment = VisualActivity.VerticalAlignment.TOP
    margin: float = 10  # Used to create space from the edge of the swimlane for the label.
    swimlanes_enabled: bool = True

    def __post_init__(self):
        if self.swimlane_formats is None:
            default_line = LineFormat(PlotableColor(50, 50, 50), 3, LineStyle.SOLID)
            default_fill = FillFormat(PlotableColor(70, 70, 70))
            default_format = PlotableFormat(default_line, default_fill)
            self.swimlane_formats = [default_format]
        self.num_swimlane_formats = len(self.swimlane_formats)

    def get_swimlane_format_for_swimlane(self, swimlane_number: int) -> PlotableFormat:
        """
        Selects the appropriate format for current swimlane based on what number is being plotted.  Rotates around
        all the supplied formats.

        :param swimlane_number: Starts at 1
        :return:
        """
        return self.swimlane_formats[(swimlane_number - 1) % self.num_swimlane_formats]


class VisualSettings:
    """
    Holds key information about the visual which is required to physically plot it.

    Most of this will come from the VisualActivity object, but some will be hard-coded or calculated.
    """

    def __init__(self, visual_id: int):
        self.visual_id = visual_id
        self.visual = PlanVisual.objects.get(id=visual_id)

        self.width: float = self.visual.width
        self.height: float = self.visual.max_height
        self.track_height: float = self.visual.track_height
        self.track_gap: float = self.visual.track_gap
        self.milestone_width = self.visual.milestone_width
        self.swimlane_gap: float = self.visual.swimlane_gap

        self.default_milestone_shape = self.visual.default_milestone_shape
        self.default_activity_shape = self.visual.default_activity_shape
        self.default_activity_plotable_style = self.visual.default_activity_plotable_style
        self.default_milestone_plotable_style = self.visual.default_milestone_plotable_style
        self.default_swimlane_plotable_style = self.visual.default_swimlane_plotable_style
