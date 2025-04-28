from datetime import datetime

from plan_visual_django.models import PlotableStyle, Font


def date_from_string(date_string: str, datetime_flag=False):
    """
    Returns a date object or a datetime object from a string of allowed form.

    Note: The app works with dates but when reading a file (e.g. Excel), the data type may come
    in as a datetime so tests which check raw file read need to be able to generate a datetime object.

    :param datetime_flag: If set then leave object as datetime, otherwise convert to date.
    :param date_string: Date string of form "YYYY-MM-DD"
    :return:
    """
    datetime_object = datetime.strptime(date_string, "%Y-%m-%d")
    if not datetime_flag:
        return datetime_object.date()
    else:
        return datetime_object


def extract_object_from_list_by_field(list, value_to_test, field_name):
    """
    Used to extract item from list of dicts or objects for which the value of a field matches a given unique id.

    Mostly used to find records in the plan or visual which match a given unique id but is written to allow any
    field to be checked.

    :param list:
    :param value_to_test:
    :param field_name:
    :return:
    """
    should_be_one_in_list = [activity for activity in list if get_field_from_object(activity, field_name) == value_to_test]
    if len(should_be_one_in_list) != 1:
        return None
    else:
        return should_be_one_in_list[0]


def get_field_from_object(obj, field_name):
    if isinstance(obj, dict):  # if the object is a dictionary
        return obj.get(field_name)
    else:  # if the object is not a dictionary (usual Python object)
        return getattr(obj, field_name, None)

"""
Utilitiy functions to support testing.  Includes

- functions to help in generating test data

"""


def generate_test_data_field_stream(field_names:[str], test_data:[tuple]):
    """
    Takes a list of tuples and an associated list of field names and generates
    a stream of input parameters which includes the test data and the name of the field to be tested.

    This will enable tests to be run so that if a test fails the remaining tests will still continue.
    :param test_data:
    :return:
    """
    for test_case in test_data:
        test_value = test_case[0]
        field_names_and_expected_values = zip(field_names, test_case[1:])
        for names_and_expected_value in field_names_and_expected_values:
            name, expected_value = names_and_expected_value
            yield test_value, name, expected_value


def generate_test_data_field_stream_multiple_inputs(test_data, expected_value_field_names):
    """
    General purpose generator for use in unit tests.

    Will carry out the same test a number of times but each time checking the value of a different field.  This is
    to ensure that a failure of one test doesn't prevent the checking of other test values.

    A list of tuples is passed in, each one of which contains 1 or more input fields used in the test, and the
    remaining values are the expected values for a number of expected value fields.  The field names for the expected
    value fields are passed in as the second paramter.

    The function works out how how many of the values in the input tuples are input paramters (based on the number of
    expected value field names) and yields the input values multiple times, each time with a different field name and
    expected value.

    :param test_data:
    :param expected_value_field_names:
    :return:
    """
    # Work out which fields are input fields and which are expected value fields by checking one of the test_data
    # tuples.
    field_start = len(test_data[0])-len(expected_value_field_names)
    for case in test_data:
        input_values = case[:field_start]
        expected_values = case[field_start:]
        for field, value in zip(expected_value_field_names, expected_values):
            yield *input_values, field, value

def create_default_styles_for_tests(color_to_use, user_to_use):
    styles = {
        "default_activity_plotable_style": "theme-01-001-activities-01",
        "default_milestone_plotable_style": "theme-01-004-milestones-01",
        "default_swimlane_plotable_style": "theme-01-006-swimlanes-01",
        "default_timeline_plotable_style_odd": "theme-01-008-timelines-01",
        "default_timeline_plotable_style_even": "theme-01-009-timelines-02",
    }
    for style_name, style_value in styles.items():
        PlotableStyle.objects.create(
            fill_color=color_to_use,
            line_color=color_to_use,
            font_color=color_to_use,
            line_thickness=10,
            font=Font.objects.get(pk=1),
            font_size=10,
            user=user_to_use,
            style_name=style_value
        )


