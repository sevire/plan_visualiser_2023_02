from dataclasses import dataclass

from plan_visual_django.models import VisualActivity
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


@dataclass
class VisualSettings:
    """
    Holds key information about the visual which is required to physically plot it.

    Largely size and shape information.
    """
    width: float = 600
    height: float = 400
    track_height: float = 10
    track_gap: float = 2
    milestone_width = 6
    swimlane_gap: float = 5

    swimlane_settings: SwimlaneSettings = SwimlaneSettings(swimlanes=["Default"], swimlane_gap=5)
