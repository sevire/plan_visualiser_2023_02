from colour import Color

"""
Utilities to convert between different color formats and similar utilities.

This uses a library called colour but I am wrapping it in a class to make the api more appropriate for this application,
to protect against changes in the library and to add additional functionality if required.
"""


class ColorLib:
    def __init__(self, color: Color):
        self.color = color

    @classmethod
    def from_rgb_255(cls, r, g, b):
        """
        Returns a Color object from RGB values in the range 0-255
        """
        return ColorLib(Color(rgb=(r/255, g/255, b/255)))

    @classmethod
    def from_hex6(cls, hex6):
        """
        Returns a Color object from a hex color string
        """
        return ColorLib(Color(hex=hex6))

    def to_hex3(self):
        """
        Returns a hex color string from a Color object
        """
        return self.color.hex

    def to_hex6(self):
        """
        Returns a hex color string from a Color object
        """
        return self.color.hex_l

    def to_rgb_255(self):
        """
        Returns a tuple of RGB values in the range 0-255 from a Color object
        """
        return tuple([int(x*255) for x in self.color.rgb])