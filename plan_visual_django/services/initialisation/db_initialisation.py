import json
import os.path
from functools import partial

from django.conf import settings
from django.contrib.auth.models import User
from plan_visual_django.models import Color, PlotableStyle, PlanFieldMappingType, PlanMappedField, PlanField, \
    PlotableShapeType, PlotableShape, FileType

root = settings.BASE_DIR
json_dir = 'plan_visual_django/fixtures'

plan_fields = 'plan_fields.json'
file_types = 'file_type.json'
mapped_fields = 'mapped_fields.json'
field_mapping_types = 'mapping_types.json'

standard_colors = 'standard_colors.json'
standard_styles = 'standard_styles.json'
standard_data_user = 'shared_data_user.json'
shape_types = 'shape_types.json'
shapes = 'shapes.json'


def print_status(phase, message):
    """
    Temporary way of getting some status messages onto the console - will be superseded when I add proper
    logging.

    :param phase:
    :param message:
    :return:
    """
    print(f"{phase:<35} : {message}")


def json_pathname(filename):
    return os.path.join(root, json_dir, filename)


def add_plan_fields():
    """
    Add plan fields to the database.

    Note we need to save the records with the original primary key values, so that the foreign key
    references in the PlanFieldMappingType records are valid.

    :return:
    """
    print_status_partial = partial(print_status, "add_plan_field")

    with open(json_pathname('plan_fields.json'), 'r') as f:
        plan_fields = json.load(f)
    for plan_field in plan_fields:
        fields = plan_field['fields']
        fields['pk'] = plan_field['pk']

        # Check whether plan field with this name already exists
        if PlanField.objects.filter(field_name=fields['field_name']).exists():
            print_status_partial(f"Plan field with name {fields['field_name']} already exists")
        else:
            print_status_partial(f"Creating plan field with name {fields['field_name']}...")
            PlanField.objects.create(**fields)
            print_status_partial(f"Plan field with name {fields['field_name']} created")


def add_plan_field_mapping_types():
    """
    Add plan field mapping types to the database.
    """
    print_status_partial = partial(print_status, "add_plan_field_mapping_types")

    with open(json_pathname(field_mapping_types), 'r') as f:
        mapping_types = json.load(f)
    for mapping_type in mapping_types:
        fields = mapping_type['fields']
        fields['pk'] = mapping_type['pk']

        # Check whether mapping type with this name already exists
        if PlanFieldMappingType.objects.filter(name=fields['name']).exists():
            print_status_partial(f"Plan field mapping type with name {fields['name']} already exists")
        else:
            print_status_partial(f"Creating plan field mapping type with name {fields['name']}...")
            PlanFieldMappingType.objects.create(**fields)
            print_status_partial(f"Plan field mapping type with name {fields['name']} created")


def add_plan_mapped_fields():
    """
    Add plan mapped fields to the database.
    """
    print_status_partial = partial(print_status, "add_plan_mapped_fields")

    with open(json_pathname(mapped_fields), 'r') as f:
        mapped_field_records = json.load(f)
    for mapped_field in mapped_field_records:
        fields = mapped_field['fields']
        fields['pk'] = mapped_field['pk']

        # Check whether mapped field with this name and mapping type already exists
        if PlanMappedField.objects.filter(
            input_field_name=fields['input_field_name'],
            plan_field_mapping_type_id=fields['plan_field_mapping_type']
        ).exists():
            print_status_partial(f"Plan mapped field with name {fields['input_field_name']} already exists")
        else:
            # Hack to replace mapping type instance reference with primary key
            fields['plan_field_mapping_type_id'] = fields['plan_field_mapping_type']
            del fields['plan_field_mapping_type']

            # Hack to replace mapped field instance reference with primary key
            fields['mapped_field_id'] = fields['mapped_field']
            del fields['mapped_field']

            print_status_partial(f"Creating mapped field with name {fields['input_field_name']}...")
            PlanMappedField.objects.create(**fields)
            print_status_partial(f"Mapped field with name {fields['input_field_name']} created")


def add_file_type():
    print_status_partial = partial(print_status, "add_file_types")

    with open(json_pathname(file_types), 'r') as f:
        file_type_records = json.load(f)
    for file_type in file_type_records:
        fields = file_type['fields']
        fields['pk'] = file_type['pk']

        # Check whether mapped field with this name and mapping type already exists
        if FileType.objects.filter(
            file_type_name=fields['file_type_name']
        ).exists():
            print_status_partial(f"File type with name {fields['file_type_name']} already exists")
        else:
            fields['plan_field_mapping_type_id'] = fields["plan_field_mapping_type"]
            del fields["plan_field_mapping_type"]

            print_status_partial(f"Creating file type with name {fields['file_type_name']}...")
            FileType.objects.create(**fields)
            print_status_partial(f"File type with name {fields['file_type_name']} created")


def create_shared_data_user():
    print_status_partial = partial(print_status, "create_shared_data_user")

    shared_data_user_name = settings.SHARED_DATA_USER_NAME
    shared_data_user_email = settings.SHARED_DATA_USER_EMAIL

    # Check whether this user already exists
    if User.objects.filter(username=shared_data_user_name).exists():
        print_status_partial(f"Shared data user ({shared_data_user_name}) already exists")
        return User.objects.get(username=shared_data_user_name)

    user_password = os.getenv('SHARED_DATA_USER_PASSWORD', 'password987')

    print_status_partial(f"Creating shared data user ({shared_data_user_name})...")
    user = User.objects.create_user(
        username=shared_data_user_name,
        email=shared_data_user_email,
        password=user_password
    )
    print_status_partial(f"Shared data user ({shared_data_user_name}) created")
    return user


def apply_standard_colors(user: User):
    """
    Add standard colors to the database, assigned to the specified user.
    """
    print_status_partial = partial(print_status, "apply_standard_colors")

    with open(json_pathname(standard_colors), 'r') as f:
        colors = json.load(f)
    for color in colors:
        fields = color['fields']

        # Add prefix so common colours easy to spot
        fields['name'] = f"{settings.SHARED_DATA_PREFIX}-{fields['name']}"

        # Check whether color with this name for this user already exists
        if Color.objects.filter(name=fields['name'], user=user).exists():
            print_status_partial(f"Color with name {fields['name']} already exists")
        else:
            # Replace user field with supplied user
            fields['user'] = user

            print_status_partial(f"Creating color with name {fields['name']}...")
            Color.objects.create(**fields)
            print_status_partial(f"Color with name {fields['name']}created")


def add_shape_types():
    """
    Each shape has a shape type so we need to specify the primary key to ensure the right mapping
    is established for both shape_type and shape.

    :return:
    """
    print_status_partial = partial(print_status, "add_shape_types")

    with open(json_pathname(shape_types), 'r') as f:
        shape_type_data = json.load(f)
    for shape_type in shape_type_data:
        fields = shape_type['fields']
        fields['pk'] = shape_type['pk']

        if PlotableShapeType.objects.filter(name=fields['name']).exists():
            print_status_partial(f"Shape type with key {fields['name']} already exists")
        else:
            print_status_partial(f"Adding shape type {fields['name']}...")
            PlotableShapeType.objects.create(**fields)
            print_status_partial(f"shape type {fields['name']} added.")


def add_shapes():
    """
    Each shape has a shape type so we need to specify the primary key to ensure the right mapping
    is established for both shape_type and shape.

    :return:
    """
    print_status_partial = partial(print_status, "add_shapes")

    with open(json_pathname(shapes), 'r') as f:
        shape_data = json.load(f)
    for shape in shape_data:
        fields = shape['fields']
        fields['pk'] = shape['pk']

        print_status_partial(f"Getting related shape type object (id={fields['shape_type']}...")
        shape_type = PlotableShapeType.objects.get(id=fields['shape_type'])
        print_status_partial(f"Successfully read related shape type object (id={fields['shape_type']}")
        fields['shape_type'] = shape_type

        if PlotableShape.objects.filter(name=fields['name']).exists():
            print_status_partial(f"Shape {fields['name']} already exists")
        else:
            print_status_partial(f"Adding shape {fields['name']}...")
            PlotableShape.objects.create(**fields)
            print_status_partial(f"shape {fields['name']} added.")
