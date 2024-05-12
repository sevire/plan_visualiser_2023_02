import json
import os.path
from functools import partial
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.crypto import get_random_string
from plan_visual_django.models import Color, PlotableStyle, PlanFieldMappingType, PlanMappedField, PlanField, \
    PlotableShapeType, PlotableShape, FileType, Font
import logging

logger = logging.getLogger(__name__)

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

initial_users = [
    {
        'username': "shared_data_user",
        'email': 'shared_data_user@genonline.co.uk',
        'superuser_flag': False,
        'id': 1,  # Id needs to be fixed only for shared_data_user as used as foreign key in some shared data items.
        'return': True  # User will be returned for use in creating initial data
    },
    {
        'username': "admin",
        'email': 'admin_user@genonline.co.uk',
        'id': 2,  # Need to specify id as we haven't reset pk counts yet and db will try to give id of 1
        'superuser_flag': True
    },
    {
        'username': "app_user_01",
        'email': 'initial_app_user@genonline.co.uk',
        'id': 3,  # Need to specify id as we haven't reset pk counts yet and db will try to give id of 1
        'superuser_flag': False
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
    if delete_flag:
        logger.info("Deleting initial data from database")
    else:
        logger.info("Adding initial data to database")

    data_driver = reversed(initial_data_driver) if delete_flag else initial_data_driver
    for initial_model_data in data_driver:
        logger.info(f"Adding data for {initial_model_data}")
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

    print_status_partial = partial(print_status, f"{model.__name__} records", delete_flag=delete_flag)

    logger.info(f"Initialising {model.__name__}, json_file_name = {file}")

    with open(json_pathname(file), 'r') as f:
        records = json.load(f)
    for record in records:
        # If delete flag is set, simply delete the record.  Any child records should have already been deleted.
        if delete_flag:
            print_status_partial(f"Attempting to delete record with pk={record['pk']}...")
            try:
                record_for_deletion = model.objects.get()
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
    logger.info(f"{(action.capitalize() + ' ' + phase):<35} : {message}")


def json_pathname(filename):
    return os.path.join(root, json_dir, filename)


def create_initial_users(delete=False):
    """
    Creates users which are required when setting up a new environment.  Which are:
    - A superuser which can be used for admin related activities
    - A shared data user which is used for common data (colours etc) to be related to.
    - An initial user of the app which can be used for manual testing of the app.

    Passwords will be generated at random and printed out at creation to avoid having to store the passwords.

    If delete flag is set, delete users, rather than adding them (for resetting - use carefully)

    :param delete:
    :return:
    """
    prompt_string = "initial_users"
    print_status_partial = partial(print_status, prompt_string, delete_flag=delete)
    user_to_return = None  # Will be populated by which ever record has the return flag set

    for user_data in initial_users:
        print_status_partial(f"Setting up user {user_data['username']}...")
        return_flag = user_data.get("return", False)

        # Check whether this user exists
        try:
            user = User.objects.get()
        except User.DoesNotExist:
            if delete:
                # Nothing to do delete and that's fine.
                print_status_partial(f"User ({[user_data['username']]}) does not exist, no need to delete")
            else:
                # No record so let's create one
                print_status_partial(f"About to create  user ({user_data['username']})...")
                # Password is random but printed out on creation so user can capture and login to change password
                user_data['password'] = get_random_string(10)
                print_status_partial(f"Password for user {user_data['username']} is {user_data['password']}")

                # Choose function to use for creating user depending upon whether superuser is required or not
                if user_data['superuser_flag'] is True:
                    function = User.objects.create_superuser
                else:
                    function = User.objects.create_user

                # Remove superuser flag and return flag from user_data as it's not a recognised keyword and we are using it as kwargs.
                del user_data['superuser_flag']
                if "return" in user_data:
                    del user_data['return']

                print_status_partial(f"Calling {function.__name__}: {user_data}")
                user = function(**user_data)
                print_status_partial(f"User ({user}) created")
                if return_flag is True:
                    print_status_partial(f"Setting user to return {user}")
                    user_to_return = user
        else:
            # User exists, so either delete or leave
            if delete:
                print_status_partial(f"User ({user_data['username']}) exists, deleting...")
                user.delete()
                print_status_partial(f"User ({user_data['username']}) exists, deleted...")
            else:
                print_status_partial(f"User ({user}) already exists")
                if return_flag is True:
                    print_status_partial(f"Setting user to return {user}")
                    user_to_return = user

    if not delete:
        return user_to_return
