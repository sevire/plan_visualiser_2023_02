from django.test import TestCase
from plan_visual_django.services.styling.style_utilities import ThemeManager, PaletteManager

seed_colors = "#fa8900", "#905678", "#678910"

class TestStyleGeneration(TestCase):
    def test_colors_from_percentages(self):
        """
        Tests ability to correctly use percentages to choose which color variants to use for a style.
        :return:
        """
        palette = PaletteManager.from_hash(7, *seed_colors)
        palette.display_palette()
        variant = palette.variant_num_from_percentage(10)
        self.assertEqual(variant, None)

    def test_theme_generation(self):
        theme_manager = ThemeManager("test-theme-01", 7, *seed_colors)
        theme_manager.generate_theme()
        theme_manager.display_theme()

