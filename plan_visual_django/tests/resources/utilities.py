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

