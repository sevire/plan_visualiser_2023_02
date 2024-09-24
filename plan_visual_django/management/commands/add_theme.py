from django.core.management import BaseCommand
from plan_visual_django.services.styling.style_utilities import ThemeManager


class Command(BaseCommand):
    """
    NOTE: The app doesn't support themes at time of implementation. This offers a nod towards it.

    This offers a bit of a halfway house whereby a set of colors and styles are created with structured names which
    can be used to color a visual using a set of colors and styles which work well together.  There is also an intention
    to write a separate command which will color a visual according to a given theme by matching style names for
    a supplied theme name.

    As each style includes a fill color, a line color and a font color, then some colors will be used more than once
    across the range of styles for a theme.

    Generally the following guidelines will be used in creating themes to ensure they are readable:
    - A theme will either be of type normal or reversed.
    - A normal theme will have light colored swimlanes and darker colored activities and milestones.
    - A reversed theme will have dark colored swimlanes and lighter colored activities and milestones.
    - Whichever type a theme is the font color for a style will be the opposite type to the fill color.
    - For a normal type theme
      - Swimlanes will be light.
      - Activities and milestones will be dark.
      - Timelines will be middle lightness, typically different colors from the swimlanes and the milestones.

    The command will create styles according to a data structure which defines styles with specific colors from
    a palette for each visual element.

    - xxxxx-01-activity-variant-01
    - xxxxx-02-activity-variant-02
    - xxxxx-03-activity-variant-03 (Only when at least two seed colors have been created)
    - xxxxx-04-milestone-variant-01
    - xxxxx-05-milestone-variant-02
    - xxxxx-06-milestone-variant-03 (Only when at least two seed colors have been created)
    - xxxxx-07-swimlane-variant-01
    - xxxxx-08-swimlane-variant-02
    - xxxxx-09-swimlane-variant-03 (Only when at least two seed colors have been created)
    - xxxxx-10-timeline-variant-01
    - xxxxx-11-timeline-variant-02

    The command will do the following:
    - Create a range of colors based on the supplied seed colors, according to the following rules:
    - Create a range of styles depending upon how many seed colors were provided.

    """
    help = "Add set of theme colors and styles based on seed color"

    def add_arguments(self, parser):
        parser.add_argument('theme-name', type=str, help='Theme name')
        parser.add_argument('colors', nargs='+', type=str, help='Hex RGB colors')

    def handle(self, *args, **options):
        theme_name = options['theme-name']
        colors = options['colors']
        if len(colors) > 3:
            self.stdout.write(self.style.ERROR(f"You supplied {len(colors)} colors - max of 3 allowed"))
            return

        theme=ThemeManager(theme_name, 7, *colors)
        theme.display_theme()
        theme.add_to_database()