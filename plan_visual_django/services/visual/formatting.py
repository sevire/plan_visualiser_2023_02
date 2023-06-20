from dataclasses import dataclass
from enum import Enum

from plan_visual_django.models import PlotableStyle


@dataclass()
class PlotableColor:
    """
    Wrapper for the colour library, which is a great resource for colour utilities but doesn't support alpha. So will
    expose key methods as required but include an alpha component.
    """
    red: int
    green: int
    blue: int
    alpha: float = 0

    def __post_init__(self):
        assert self.red in range(0, 256) and self.green in range(0, 256) and \
               self.blue in range(0, 256) and self.alpha in range(0, 1)


class VerticalPositioningOption(Enum):
    """
    NOTE: This needs to be aligned with what is defined in model.py.  At some point the two should be made part of the
          same data structure but that's for the future

          ToDo: Refactor this so that the CHOICES field used in the model is generated directly from this.
    """
    TRACK_NUMBER = "TRACK"
    RELATIVE_TRACK = "REL_TRACK"
    AUTO = "AUTO"


class LineStyle(Enum):
    SOLID = 1


class Font(Enum):
    """
    Simple class to store the name of a font (to begin with) for use in drawing objects.  May need to extend this
    functionality
    """
    ARIAL = 1


class TextHorizontalAlign(Enum):
    LEFT = 1
    RIGHT = 2
    CENTER = 3


class TextVerticalAlign(Enum):
    TOP = 1
    MIDDLE = 2
    BOTTOM = 3


class TextLayout(Enum):
    NOWRAP = 1
    WRAP = 2


@dataclass
class LineFormat:
    line_color: PlotableColor
    line_thickness: float
    line_style: LineStyle = LineStyle.SOLID


@dataclass
class FillFormat:
    fill_color: PlotableColor


@dataclass
class TextFormat:
    left_align: TextHorizontalAlign
    font: Font = Font.ARIAL


@dataclass
class PlotableFormat:
    line_format: LineFormat
    fill_format: FillFormat

    @classmethod
    def default(cls):
        fill_colour = PlotableColor(50, 50, 50)
        fill_format = FillFormat(fill_colour)

        line_colour = fill_colour
        line_format = LineFormat(line_color=line_colour, line_thickness=5)

        return cls(line_format, fill_format)

    @classmethod
    def from_db_choice(cls, format:PlotableStyle):
        """
        Create a plotable style object using the user selection from database.

        Was unclear whether to add this layer of abstraction - why can't I just use the Model Class for Plotable Style?
        In the end I decided it was better not to hard wire the dependency as I may wish to vary something later in one
        or the other without impacting the other one.

        :param format:
        :return:
        """
        line_color = PlotableColor(
            red=format.line_color.red,
            green=format.line_color.green,
            blue=format.line_color.blue,
            alpha=format.line_color.alpha
        )
        line_thickness = format.line_thickness
        line_format = LineFormat(line_color, line_thickness, LineStyle.SOLID)
        fill_color = PlotableColor(
            red=format.fill_color.red,
            green=format.fill_color.green,
            blue=format.fill_color.blue,
            alpha=format.fill_color.alpha
        )
        fill_format = FillFormat(fill_color)
        return cls(line_format, fill_format)
