import django.db.utils
from django.core.management import BaseCommand
from django.core.management import CommandError
from plan_visual_django.models import Color
from plan_visual_django.services.auth.shared_user_services import get_shared_user
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Quick way of adding colours to the app."

    def add_arguments(self, parser):
        parser.add_argument("name", type=str)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--rgb",
            nargs=3,
            type=int,
            metavar=("RED", "GREEN", "BLUE"),
            help="Supply three integers for red, green, blue (0-255).",
        )
        group.add_argument(
            "--hex",
            dest="hex_color",
            type=str,
            help="Supply a hex colour string in the form #rrggbb or rrggbb.",
        )
        # Note: --verbosity / -v is provided globally by Django; no need to declare it here.

    def handle(self, *args, **options):
        """
        Creates a record on the Color table for supplied RGB parameters.

        :param name:
        :param red:
        :param green:
        :param blue:
        :return:
        """
        verbosity = int(options.get("verbosity", 1))
        name = options["name"]

        if verbosity >= 1:
            self.stdout.write(f"Starting add_color for name='{name}'")

        try:
            if options.get("rgb") is not None:
                try:
                    red, green, blue = map(int, options["rgb"])
                except ValueError:
                    self.stderr.write(self.style.ERROR("RGB values must be integers."))
                    raise CommandError("RGB values must be integers.")
                else:
                    logger.debug("Parsed RGB components: r=%s, g=%s, b=%s", red, green, blue)
                    if verbosity >= 2:
                        self.stdout.write(f"Using RGB components: ({red}, {green}, {blue})")
            else:
                hex_color = options.get("hex_color", "")
                if hex_color.startswith("#"):
                    hex_color = hex_color[1:]
                if len(hex_color) != 6:
                    self.stderr.write(self.style.ERROR("Hex colour must be 6 characters (rrggbb)."))
                    raise CommandError("Hex colour must be 6 characters (rrggbb).")
                try:
                    red = int(hex_color[0:2], 16)
                    green = int(hex_color[2:4], 16)
                    blue = int(hex_color[4:6], 16)
                except ValueError:
                    self.stderr.write(
                        self.style.ERROR("Hex colour must contain only hexadecimal digits (0-9, a-f).")
                    )
                    raise CommandError("Hex colour must contain only hexadecimal digits (0-9, a-f).")
                else:
                    logger.debug("Converted HEX '%s' to RGB: r=%s, g=%s, b=%s", hex_color, red, green, blue)
                    if verbosity >= 2:
                        self.stdout.write(f"Converted HEX to RGB: ({red}, {green}, {blue})")

            shared_user = get_shared_user()
            logger.info("Resolved shared user: %s", getattr(shared_user, "username", shared_user))
            if verbosity >= 2:
                self.stdout.write(f"Using shared user: {getattr(shared_user, 'username', shared_user)}")

            for comp, name_comp in ((red, "red"), (green, "green"), (blue, "blue")):
                if not (0 <= comp <= 255):
                    msg = f"{name_comp.capitalize()} component must be between 0 and 255."
                    self.stderr.write(self.style.ERROR(msg))
                    raise CommandError(msg)

            if verbosity >= 1:
                self.stdout.write(f"Creating color '{name}' with RGBA=({red}, {green}, {blue}, 1)")

            Color.objects.create(user=shared_user, name=name, red=red, green=green, blue=blue, alpha=1)

            self.stdout.write(self.style.SUCCESS(f"Color '{name}' created successfully."))
            logger.info("Color '%s' created for user '%s'", name, getattr(shared_user, "username", shared_user))

        except CommandError:
            logger.exception("CommandError during add_color for name='%s'", name)
            raise
        except django.db.utils.IntegrityError as exc:
            raise CommandError(f"Color '{name}' already exists for the shared user.") from exc
        except Exception as exc:
            logger.exception("Unexpected error during add_color for name='%s'", name)
            self.stderr.write(self.style.ERROR(f"Unexpected error: {exc}"))
            raise CommandError("add_color failed; see logs for details") from exc