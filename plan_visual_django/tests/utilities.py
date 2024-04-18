from datetime import datetime


def date_from_string(date_string: str):
    """

    :param date_string: Date string of form "YYYY-MM-DD"
    :return:
    """
    return datetime.strptime(date_string, "%Y-%m-%d")


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
