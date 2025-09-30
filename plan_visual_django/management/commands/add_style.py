from django.core.management import BaseCommand, CommandError
from plan_visual_django.models import Color, PlotableStyle, Font
from plan_visual_django.services.auth.shared_user_services import get_shared_user


class Command(BaseCommand):
    help = "Create a PlotableStyle for the shared user using existing colour names (fill, line, font)."

    def add_arguments(self, parser):
        parser.add_argument("style_name", type=str, help="Name of the style to create.")
        parser.add_argument("fill_color_name", type=str, help="Existing fill colour name under the shared user.")
        parser.add_argument("line_color_name", type=str, help="Existing line colour name under the shared user.")
        parser.add_argument("font_color_name", type=str, help="Existing font colour name under the shared user.")

        parser.add_argument(
            "--line-thickness",
            dest="line_thickness",
            type=int,
            default=1,
            help="Line thickness (default 1).",
        )
        parser.add_argument(
            "--font-size",
            dest="font_size",
            type=int,
            default=10,
            help="Font size in points (default 10).",
        )

    def handle(self, *args, **options):
        style_name = options["style_name"]
        fill_name = options["fill_color_name"]
        line_name = options["line_color_name"]
        font_name = options["font_color_name"]
        line_thickness = options["line_thickness"]
        font_size = options["font_size"]

        shared_user = get_shared_user()

        # Validate that style name does not already exist for shared user
        if PlotableStyle.objects.filter(user=shared_user, style_name=style_name).exists():
            raise CommandError(f"A style named '{style_name}' already exists for the shared user.")

        # Resolve colors by name for shared user
        try:
            fill_color = Color.objects.get(user=shared_user, name=fill_name)
        except Color.DoesNotExist:
            raise CommandError(f"Fill colour '{fill_name}' not found for the shared user.")

        try:
            line_color = Color.objects.get(user=shared_user, name=line_name)
        except Color.DoesNotExist:
            raise CommandError(f"Line colour '{line_name}' not found for the shared user.")

        try:
            font_color = Color.objects.get(user=shared_user, name=font_name)
        except Color.DoesNotExist:
            raise CommandError(f"Font colour '{font_name}' not found for the shared user.")

        # Choose a font (keep this simple)
        font = Font.objects.order_by("font_name").first()
        if not font:
            raise CommandError("No Font records exist. Please add a Font first.")

        PlotableStyle.objects.create(
            user=shared_user,
            style_name=style_name,
            fill_color=fill_color,
            line_color=line_color,
            font_color=font_color,
            line_thickness=line_thickness,
            font=font,
            font_size=font_size,
        )

        self.stdout.write(self.style.SUCCESS(f"Created style '{style_name}' for the shared user."))