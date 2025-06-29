from django.db import connections
from django.db.utils import OperationalError

def check_database_connection():
    """
    Verifies that the database connection is operational.
    :return: A dict containing the status and a message.
    """
    try:
        # Try to establish a connection using Django's default database alias
        connection = connections['default']
        connection.cursor()
        return {"status": "PASS", "message": "Database is reachable"}
    except OperationalError as e:
        return {"status": "FAIL", "message": str(e)}