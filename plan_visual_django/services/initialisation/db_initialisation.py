import json
import os.path
from functools import partial
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from plan_visual_django.models import Color, PlotableStyle, Font, StaticContent
import logging

logger = logging.getLogger(__name__)

root = settings.BASE_DIR
json_dir = 'plan_visual_django/fixtures'
file_types = 'file_type.json'
mapped_fields = 'mapped_fields.json'
field_mapping_types = 'mapping_types.json'
standard_colors = 'standard_colors.json'
standard_styles = 'standard_styles.json'
standard_data_user = 'shared_data_user.json'
shape_types = 'shape_types.json'
shapes = 'shapes.json'

UserModel = get_user_model()

# Note - in the following data structures, order matters as records that are referenced as foreign keys must be added
#        before the record which references them.
initial_data_driver = [
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
    },
    {
        "dumpdata_filename": 'static_content.json',
        "model": StaticContent,
        "field_name_for_messages": "title",
    }
]

# The data for each initial user is stored in a set of environment variables, the names of which follow a set schema:
initial_users_config = [
    # Name of env variable, superuser flag, user index
    {"SHARED_USER", False, 1},
    {"ADMIN", True, 2},
    {"APP_USER_1", False, 3},
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


def add_initial_data_for_model(shared_user: UserModel, data_driver: dict, delete_flag):
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
    logger.info(f"{(action.capitalize() + ' ' + phase):<35} : {message}")


def json_pathname(filename):
    return os.path.join(root, json_dir, filename)

def set_initial_user_data(initial_users_config_data):
    """
    Reads environment variables for initial users based on environment prefix.
    Returns list of user data dictionaries containing username, email, and password.
    """

    # Work out names of environment variables to read.
    user_data = []
    for user, superuser_flag, user_index in initial_users_config_data:
        username_env_name = f"{user}_NAME"
        password_env_name = f"{user}_PASSWORD"
        email_domain_env_name = "INITIAL_USER_EMAIL_DOMAIN"

        username = os.environ.get(username_env_name)
        password = os.environ.get(password_env_name)
        email_domain = os.environ.get(email_domain_env_name)

        print_status("Set initial user data", f"Environment variables...")
        print_status("Set initial user data", f"Environment {username_env_name}:{username}")
        print_status("Set initial user data", f"Environment {password_env_name}:{password}")
        print_status("Set initial user data", f"Environment {email_domain_env_name}:{email_domain}")

        user_record = {}

        user_record['username'] = username
        user_record['password'] = password
        user_record['email'] = f"{username}@{email_domain}"
        user_record['superuser_flag'] = superuser_flag
        user_record['id'] = user_index

        user_data.append(user_record)

    return user_data


def create_initial_users(user_data, delete=False):
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

    for user in user_data:
        print_status_partial(f"Setting up user {user['username']}...")

        # Check whether this user exists
        try:
            existing_user = UserModel.objects.get(username=user["username"])
        except UserModel.DoesNotExist:
            if delete:
                # Nothing to do delete and that's fine.
                print_status_partial(f"User ({[user['username']]}) does not exist, no need to delete")
            else:
                # No record so let's create one
                print_status_partial(f"About to create  user ({user['username']})...")

                # ToDo: Remove the logging of password once setting of password from env variable working as expected
                print_status_partial(f"Password for user {user['username']} is {user['password']}")

                # Choose function to use for creating user depending upon whether superuser is required or not
                if user['superuser_flag'] is True:
                    function = UserModel.objects.create_superuser
                else:
                    function = UserModel.objects.create_user

                # Remove superuser flag and return flag from user_data as it's not a recognised keyword and we are using it as kwargs.
                del user['superuser_flag']

                print_status_partial(f"Calling {function.__name__}: {user}")

                # Need to provide the SECRET_KEY for the project to be used when hashing the password
                # (will also be used when authenticating)
                new_user = function(**user)
                print_status_partial(f"User ({new_user}) created")
                user_to_return = new_user
        else:
            # User exists, so we want to check whether the password is set to the configured value, an if not
            # change it to that value.
            if delete:
                print_status_partial(f"User ({existing_user.username}) exists, deleting...")
                existing_user.delete()
            else:
                # Check whether new password is same as current password set for the user
                print_status_partial(f"User ({existing_user}) already exists")
                password_works = existing_user.check_password(user['password'])
                if password_works:
                    print_status_partial(f"Passwords match, no need to update")
                else:
                    print_status_partial(f"Passwords do not match for existing user {existing_user.username}, updating...")
                    existing_user.set_password(user['password'])
                    existing_user.save()
                    print_status_partial(f"Password updated")
                print_status_partial(f"Setting user to return {user}")
                user_to_return = existing_user

    if not delete:
        return user_to_return
    else:
        return None
