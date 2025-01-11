import colorsys
import random
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Generate n random seed colors and display them in the terminal"

    def add_arguments(self, parser):
        parser.add_argument(
            "n",
            type=int,
            help="Number of seed colors to generate (1-10)",
        )

    def handle(self, *args, **options):
        n = options["n"]
        if not (1 <= n <= 10):
            self.stderr.write(self.style.ERROR("Error: n must be between 1 and 10"))
            return

        seed_colors = []
        for _ in range(n):
            hue = random.random()  # Random hue (0 to 1)
            saturation = random.uniform(0.6, 0.9)  # Ensures vibrant colors
            lightness = random.uniform(0.4, 0.7)  # Avoids too dark or too light

            rgb = colorsys.hls_to_rgb(hue, lightness, saturation)

            # Convert to HEX format
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            )
            seed_colors.append(hex_color)

        # Print colors with visual representation in the terminal
        for hex_color in seed_colors:
            r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
            color_block = f"\033[48;2;{r};{g};{b}m    \033[0m"  # ANSI escape code for background color
            self.stdout.write(f"{color_block} {hex_color}")

        # Print the HEX values in a single line for easy copy-pasting
        self.stdout.write("\n" + " ".join(seed_colors))
