import json
import os.path
from functools import partial

from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.crypto import get_random_string

from plan_visual_django.models import Color, PlotableStyle, PlanFieldMappingType, PlanMappedField, PlanField, \
    PlotableShapeType, PlotableShape, FileType, Font

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

# Note - in the following data structures, order matters as records that are referenced as foreign keys must be added
#        before the record which references them.
initial_data_driver = [
    {
        "dumpdata_filename": 'plan_fields.json',
        "model": PlanField,
        "field_name_for_messages": "field_name"
    },
    {
        "dumpdata_filename": 'mapping_types.json',
        "model": PlanFieldMappingType,
        "field_name_for_messages": "name"
    },
    {
        "dumpdata_filename": 'mapped_fields.json',
        "model": PlanMappedField,
        "field_name_for_messages": "input_field_name",
        "foreign_keys": [
            "plan_field_mapping_type",
            "mapped_field"
        ]
    },
    {
        "dumpdata_filename": 'file_type.json',
        "model": FileType,
        "field_name_for_messages": "file_type_name",
        "foreign_keys": [
            "plan_field_mapping_type",
        ]
    },
    {
        "dumpdata_filename": 'standard_colors.json',
        "model": Color,
        "field_name_for_messages": "name",
        "foreign_keys": [
            "user",
        ]
    },
    {
        "dumpdata_filename": 'fonts.json',
        "model": Font,
        "field_name_for_messages": "font_name",
    },
    {
        "dumpdata_filename": 'shape_types.json',
        "model": PlotableShapeType,
        "field_name_for_messages": "name"
    },
    {
        "dumpdata_filename": 'shapes.json',
        "model": PlotableShape,
        "field_name_for_messages": "name",
        "foreign_keys": [
            "shape_type",
        ]
    },
    {
        "dumpdata_filename": 'standard_styles.json',
        "model": PlotableStyle,
        "field_name_for_messages": "style_name",
        "foreign_keys": [
            "user",
            "fill_color",
            "line_color",
            "font_color",
            "font"
        ]
    }
]


def add_initial_data(shared_data_user, delete_flag=False):
    """
    Orchestrates addition of common/initial data.

    If delete_flag is set, deletes data rather than adds it (used carefully!). In this case the tables are processed in
    opposite order so that child records are deleted before parent records (to avoid constraint errors)

    :param shared_data_user: Passed in to function to create records, used when there is a foreign key to a user.
    :param delete_flag:
    :return:
    """
    # Reverse order if we are deleting as we need to delete child records first
    data_driver = reversed(initial_data_driver) if delete_flag else initial_data_driver
    for initial_model_data in data_driver:
        add_initial_data_for_model(shared_data_user, initial_model_data, delete_flag)


def add_initial_data_for_model(shared_user: User, data_driver: dict, delete_flag):
    """
    Sets up data in an empty database to 'bootstrap' the app so that required data records are in place when creating
    a new environment.

    Can also be run in an existing environment to ensure that key records are present.

    If delete flag is set the data will be deleted instead of added.

    The data to be added is created using the dumpdata command and will include primary keys, so if trying to add
    retrospectively there may be unique conflicts, and for now the logic doesn't attempt to get round that.

    :return:
    """
    model = data_driver['model']
    file = data_driver['dumpdata_filename']
    field_name_for_messages = data_driver['field_name_for_messages']
    foreign_keys = [] if 'foreign_keys' not in data_driver else data_driver['foreign_keys']

    print_status_partial = partial(print_status, f"Add {model.__name__} records", delete_flag=delete_flag)

    with open(json_pathname(file), 'r') as f:
        records = json.load(f)
    for record in records:
        # If delete flag is set, simply delete the record.  Any child records should have already been deleted.
        if delete_flag:
            print_status_partial(f"Attempting to delete record with pk={record['pk']}...")
            try:
                record_for_deletion = model.objects.get(pk=record['pk'])
            except model.DoesNotExist as e:
                print_status_partial(f"No record found pk={record['pk']}")
            else:
                print_status_partial(f"Record found, deleting.")
                record_for_deletion.delete()
                print_status_partial(f"Record Record deleted.")
        else:
            fields = record['fields']
            fields['pk'] = record['pk']

            # For any foreign keys in the record, replace the instance with the id in the field kwargs
            for key in foreign_keys:
                # In most cases we replace the reference to an object with a reference to the primary key id, because
                # that is what is captured by the dumpdata command.
                #
                # But if the foreign key is "user" then we just assign the passed in user to that object.
                if key == "user":
                    fields[key] = shared_user
                else:
                    fields[key + "_id"] = fields[key]
                    del fields[key]

            print_status_partial(f"Adding record {fields[field_name_for_messages]}...")
            try:
                model.objects.create(**fields)
            except IntegrityError as e:
                print_status_partial(f"Couldn't add record {e.args[0]}")
            else:
                print_status_partial(f"Record {fields[field_name_for_messages]} added.")


def print_status(phase, message, delete_flag=False):
    """
    Temporary way of getting some status messages onto the console - will be superseded when I add proper
    logging.

    :param delete:
    :param phase:
    :param message:
    :return:
    """
    action = "delete" if delete_flag else "add"
    print(f"{(action + '_' + phase):<35} : {message}")


def json_pathname(filename):
    return os.path.join(root, json_dir, filename)


def create_shared_data_user(delete=False):
    """
    Creates the user which is to be used as the owner of standard data which requires a user, such as colours
    and styles.

    If delete flag is set, delete user, rather than add it (for resetting - use carefully)

    :param delete:
    :return:
    """
    prompt_string = "shared_data_user"
    print_status_partial = partial(print_status, "shared_data_user", delete_flag=delete)

    shared_data_user_name = settings.SHARED_DATA_USER_NAME
    shared_data_user_email = settings.SHARED_DATA_USER_EMAIL

    # Check whether this user exists
    try:
        shared_user = User.objects.get(username=shared_data_user_name)
    except User.DoesNotExist:
        if delete:
            # Nothing to do delete and that's fine.
            print_status_partial(f"Shared data user ({shared_data_user_name}) does not exist, no need to delete")
            return
        else:
            # No record so let's create one
            user_password = os.getenv('SHARED_DATA_USER_PASSWORD', 'dummy987')

            print_status_partial(f"Creating shared data user ({shared_data_user_name})...")
            # Password can be random, we don't need to login (can use admin to examine database)
            password = get_random_string(10)
            user = User.objects.create_user(
                id=1,
                username=shared_data_user_name,
                email=shared_data_user_email,
                password=password
            )
            print_status_partial(f"Shared data user ({shared_data_user_name}) created")
            return user
    else:
        # User exists, so either delete or leave
        if delete:
            print_status_partial(f"Shared data user ({shared_data_user_name}) exists, deleting...")
            shared_user.delete()
            print_status_partial(f"Shared data user ({shared_data_user_name}) exists, deleted...")
        else:
            print_status_partial(f"Shared data user ({shared_data_user_name}) already exists")
            return User.objects.get(username=shared_data_user_name)
