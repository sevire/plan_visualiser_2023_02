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
