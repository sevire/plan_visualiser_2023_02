from dataclasses import dataclass
from typing import List, Tuple
from PIL import Image, ImageDraw
from colour import Color
from django.conf import settings
from django.contrib.auth.models import User
from plan_visual_django.models import PlotableStyle, Font

from plan_visual_django.models import Color as DatabaseColor


@dataclass
class ColorForPalette:
    name: str  # We need to give each color a name as we will use that to identify it when it's in the database
    color: Color


class PaletteManager:
    """
    Creates and manages a palette of colors to be used for use in creating styles and themes for the app.
    Creates a palette given a set of seed colors and a number of variants to create for each color.
    Then allows the colors to be used in different styles.
    """
    def __init__(self, palette_name, num_variants: int, *hex_seed_colors: str):
        self.palette_name = palette_name
        self.seed_colors: Tuple[str, ...] = hex_seed_colors
        self.num_seed_colors: int = len(hex_seed_colors)
        self.num_variants: int = num_variants
        self._palette: List[List[ColorForPalette]] = []
        self._generate_all_color_variants()

    @classmethod
    def from_hash(cls, num_variants, *seed_colors):
        seed_colors_as_color_objects = [cls._hash_to_color(seed_color) for seed_color in seed_colors]
        return cls(num_variants, *seed_colors_as_color_objects)

    def get_color_variant(self, seed_color_number, variant_number) -> ColorForPalette:
        variant_color = self._palette[seed_color_number - 1][variant_number - 1]
        return variant_color

    def get_colors_for_style(self, *color_specs):
        """
        Each of the color specs is a tuple with a seed color number and a percentage.
        The method simply calculates which variant to use for each color and then converts into a Color
        and returns.

        :param color_specs:
        :return:
        """
        return [self.get_color_variant(color_num, percentage) for color_num, percentage in color_specs]

    def display_palette(self):
        block_width, block_height = 100, 100
        width = block_width * self.num_variants
        height = block_height * len(self._palette)

        # Create a new image with a white background
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # Draw color blocks
        for i, seed_color_variant in enumerate(self._palette):
            for j, shade_variant in enumerate(seed_color_variant):
                draw.rectangle([j * block_width, i * block_height, (j + 1) * block_width, (i + 1) * block_height], fill=tuple(int(255 * c) for c in shade_variant.get_rgb()))

        # Display the image
        image.show()

    def add_to_database(self, user):
        """
        Add colors to database for the palette, with the supplied name embedded so can be used as part of a theme.
        :return:
        """
        for seed_color_variant_num, seed_colour_variants in enumerate(self._palette):
            for seed_color_variant in seed_colour_variants:
                color_name_for_db = f"{seed_color_variant.name}"
                red, green, blue = Style.get_color_as_rgb_tuple(seed_color_variant.color)

                print(f"Adding color to database: {color_name_for_db}")

                DatabaseColor.objects.create(
                    user=user,
                    name=color_name_for_db,
                    red=red,
                    green=green,
                    blue=blue
                )

    def _generate_all_color_variants(self):
        for color_num, color in enumerate(self.seed_colors, start=1):
            self._palette.append(self._generate_variants_for_color(color_num, color))

    def _generate_variants_for_color(
        self,
        seed_color_num,  # Just used to generate name for variant
        original_color: str,
        num_variants: int = 7,
        min_lightness: float = 0.2,
        max_lightness: float = 0.8
    ):
        """
        Generate a series of color variants ranging from moderately light to moderately dark.
        The original color is the middle one.  Also stores a name with each variant to be used when adding color
        to the database (for example).
        :param seed_color_num:
        """
        # Convert hex color to RGB
        original_color = Color(original_color)
        norm = PaletteManager._normalize_color(original_color)

        # Generate variants
        step = (max_lightness - min_lightness) / (num_variants - 1)  # Step size for lightness variation
        variants = []

        for darkness_level in range(num_variants):
            # Slight hack to reverse logic to create increasing darkness not increasing lightness
            # ToDo: Clean logic up around color variants to create from light to dark (remove hack)
            lightness_level = num_variants - darkness_level - 1
            # Calculate new lightness within the defined range
            if lightness_level == num_variants // 2:
                new_l = norm.get_luminance()  # Keep the original lightness for the middle variant
            else:
                # Adjust lightness around the middle
                new_l = max(min_lightness,
                            min(max_lightness, (lightness_level - (num_variants // 2)) * step + norm.get_luminance()))

            # Convert back to RGB
            variant = Color(hsl=(norm.hue, norm.saturation, new_l))

            variant_name = f"{self.palette_name}-var-{seed_color_num:02}-{darkness_level+1:02}"  # Form var_nn - will be used to construct longer name for colors in DB.
            variants.append(ColorForPalette(variant_name, variant))

        return variants

    @staticmethod
    def _normalize_color(color: Color):
        """
        Normalize the color by averaging the brightness and retaining the hue and saturation.
        """
        # Normalize color by setting lightness to 0.5 (average)
        normalized = Color(hsl=(color.hue, color.saturation,  0.5))

        return normalized

    @classmethod
    def _hash_to_color(cls, hex_color):
        return Color(hex_color)

    def variant_from_seed_color_num_and_percentage(self, seed_color_num: int, percentage: int):
        variant_num_from_percentage = self._variant_num_from_percentage(percentage)
        palette_color = self._palette[seed_color_num-1][variant_num_from_percentage-1]

        return palette_color

    def _variant_num_from_percentage(self, percentage: int):
        return round(percentage * (self.num_variants - 1) / 100) + 1


@dataclass
class Style:
    """
    This is a class which stores key attributes of a style, to be later used to generate a PlotableStyle record in the
    database.

    As we aren't going to add colors or styles to the database until invoked by the user, we need a way of
    naming colors within a style so that we can use that name when we add the colors to the database and later when we
    create Plotable Styles be able to
    """
    style_name: str
    fill_color: ColorForPalette
    line_color: ColorForPalette
    font_color: ColorForPalette

    @staticmethod
    def get_color_as_rgb_tuple(color) -> Tuple[int, ...]:
        return tuple(int(255 * c) for c in color.rgb)

    def get_style_color_as_rgb_tuple(self, attribute):
        color = getattr(self, attribute+"_color")
        return Style.get_color_as_rgb_tuple(color.color)


class VisualTheme:
    """
    Class representing a collection of styles for different visible elements on a Plan Visual.

    A theme comprises a selection of styles, typically at least two for each element which might appear
    on the visual (e.g. activity, swimlane).

    Styles are added in the order in which they need to be numbered so that when sorted they appear in a pre-determined
    order.
    """
    def __init__(self, theme_name):
        self.theme_name = theme_name
        self.style_count = 0  # Used to give each style in the theme a number for sorting.
        self.style_element_instance_counts = {}  # Keep track of how many styles are for each element for numbering
        self.styles = {}

    def __str__(self):
        return f"Theme Name: {self.theme_name}, Number of Styles: {len(self.styles)}"

    def num_styles(self):
        return len(self.styles)

    def add_style(self, visual_element_name: str, fill, line, font):
        """
        Adds the supplied style to the theme, using a name which represents
        :param font:
        :param line:
        :param fill:
        :param visual_element_name:
        :return:
        """
        style_name = self._generate_style_name(visual_element_name)
        style = Style(style_name, fill, line, font)
        self.styles[style_name] = style
        print(f"Creating style number {self.style_count}, {style_name}")

    def _generate_style_name(self, visual_element_name: str):
        """
        Generates a string to be used for the name of a style which includes the following components:
        - Theme name
        - Overall style sequence num within the theme (used to order theme in dropdowns so order is controlled)
        - Element name of element this style is designed for
        - Sequence num of styles for this element (used in ordering)
        :param visual_element_name:
        :return:
        """
        self.style_count += 1

        # Get and increment count for instance num to use in the style name.
        if visual_element_name not in self.style_element_instance_counts:
            self.style_element_instance_counts[visual_element_name] = 0

        self.style_element_instance_counts[visual_element_name] += 1
        element_instance_num = self.style_element_instance_counts[visual_element_name]

        return f"{self.theme_name}-{self.style_count:03}-{visual_element_name}-{element_instance_num:02}"


class ThemeManager:
    theme_driver = {
        # Format of a style is (fill, line, font)
        1: {
            "activities": [
                ((1, 70), (1, 80), (1, 0))
            ],
            "milestones": [
                ((1, 100), (1, 80), (1, 0))
            ],
            "swimlanes": [
                ((1, 10), (1, 40), (1, 80)),
                ((1, 20), (1, 60), (1, 80))
            ],
            "timelines": [
                ((1, 10), (1, 40), (1, 80)),
                ((1, 20), (1, 60), (1, 80))
            ]
        },
        2: {
            "activities": [
                ((1, 70), (1, 80), (1, 0)),
                ((1, 70), (2, 70), (1, 0))
            ],
            "milestones": [
                ((1, 70), (2, 70), (1, 0))

            ],
            "swimlanes": [
                ((1, 70), (2, 70), (1, 0))

            ],
            "timelines": [
                ((1, 70), (2, 70), (1, 0))

            ]
        },
        3: {
            "activities": [
                ((1, 70), (1, 80), (1, 0)),
                ((2, 70), (2, 80), (2, 0)),
                ((3, 70), (3, 80), (3, 0)),
            ],
            "milestones": [
                ((1, 90), (1, 100), (1, 0)),
                ((2, 90), (2, 100), (2, 0))
            ],
            "swimlanes": [
                ((2, 0), (2, 15), (2, 100)),
                ((3, 0), (3, 15), (2, 100))
            ],
            "timelines": [
                ((1, 40), (1, 50), (1, 100)),
                ((3, 40), (2, 50), (3, 100))
            ]
        }
    }

    def __init__(self, theme_name: str, num_color_variants: int, *seed_colors: str):
        """
        Accepts a number of seed colors and generates a theme with a number of variants of styles for each of the
        components of a visual (activities, milestones, swimlanes, timeline).

        The order of the seed colors matters, and also the number of seed colors will affect how the colors are
        applied to the various styles in the theme.

        :param theme_name:
        :param seed_colors:
        """
        self.palette = PaletteManager(f"palette-for-theme-{theme_name}", num_color_variants, *seed_colors)
        self.theme = VisualTheme(theme_name)
        self.generate_all_style_variants()

    def generate_all_style_variants(self):
        print(f"Theme {self.theme.theme_name} Generating styles for theme...")

        driver_data = ThemeManager.theme_driver[self.palette.num_seed_colors]

        for element_type in driver_data:
            for style in driver_data[element_type]:
                colors_for_style = (self.palette.variant_from_seed_color_num_and_percentage(*color) for color in style)
                self.theme.add_style(element_type, *colors_for_style)

    def display_theme(self):
        block_width, block_height = 100, 100
        width = block_width * 3  # Each row will display fill, line and font colors
        vertical_gap = 20  # Gap between rectangles
        height = (block_height + vertical_gap) * self.theme.num_styles()

        # Create a new image with a white background
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # Draw color blocks
        for style_num, style_data in enumerate(self.theme.styles.items()):
            style_name, style = style_data

            # Draw rectangle for outline first
            draw.rectangle((0, style_num*(block_height+vertical_gap), width, style_num*(block_height+vertical_gap)+block_height), fill=style.get_style_color_as_rgb_tuple("line"))
            draw.rectangle((0+5, style_num*(block_height+vertical_gap)+5, width-5, style_num*(block_height+vertical_gap)+block_height-5), fill=style.get_style_color_as_rgb_tuple("fill"))

            # Draw name of style over top of colours
            draw.text((10, style_num*(block_height+vertical_gap)+block_height/2), style_name, fill=style.get_style_color_as_rgb_tuple("font"))
        # Display the image
        image.show()

    def add_to_database(self):
        """
        Adds all the styles for the theme to the database as PlotableStyles under the shared_data_user.
        :return:
        """
        # First add all the colors to the database
        user = User.objects.get(username=settings.SHARED_DATA_USER_NAME)
        self.palette.add_to_database(user=user)

        for style_name, style in self.theme.styles.items():
            theme_style_name = f"{style_name}"

            # Get the colors from the database for this style to add to PlotableStyle
            fill_color = DatabaseColor.objects.get(name=style.fill_color.name)
            line_color = DatabaseColor.objects.get(name=style.line_color.name)
            font_color = DatabaseColor.objects.get(name=style.font_color.name)

            # ToDo: Change this when we have more sophisticated font handling
            font = Font.objects.all().first()  # Bit of a hack until we do a bit more with fonts!

            PlotableStyle.objects.create(
                user=user,
                style_name=theme_style_name,
                fill_color=fill_color,
                line_color=line_color,
                font_color=font_color,
                line_thickness=10,
                font=font
            )

