from django.core.management import BaseCommand
from plan_visual_django.services.initialisation.db_initialisation import create_shared_data_user, apply_standard_colors, \
    add_plan_fields, add_plan_field_mapping_types, add_plan_mapped_fields, add_shape_types, add_shapes, add_file_type


class Command(BaseCommand):
    """
    Add common data items required by all users.  Includes:
    - Field mapping types for each file format
    - Field mapping for each field in each file format
    - Color palette
    - Plotable styles
    """
    help = "Add set of common data items required by all users."

    def handle(self, *args, **options):
        """
        Creates standard shared data for following:
        - Colors
        - Styles
        - Field mapping types
        - Field mappings
        """
        user = create_shared_data_user()

        add_plan_fields()
        add_plan_field_mapping_types()
        add_plan_mapped_fields()
        add_file_type()

        apply_standard_colors(user=user)

        add_shape_types()
        add_shapes()