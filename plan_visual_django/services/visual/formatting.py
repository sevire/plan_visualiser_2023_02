from dataclasses import dataclass
from enum import Enum
from typing import List


@dataclass()
class PlotableColor:
    """
    Wrapper for the colour library, which is a great resource for colour utilities but doesn't support alpha. So will
    expose key methods as required but include an alpha component.
    """
    red: int
    green: int
    blue: int
    alpha: int = 0

    def __post_init__(self):
        assert self.red in range(0, 256) and self.green in range(0, 256) and \
               self.blue in range(0, 256) and self.alpha in range(0, 256)


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
    line_colour: PlotableColor
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
        line_format = LineFormat(line_colour=line_colour, line_thickness=5)

        return cls(line_format, fill_format)
