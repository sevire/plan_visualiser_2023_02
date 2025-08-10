from enum import Enum
from typing import Dict


class ServiceStatusCode(Enum):
    # Generic statuses
    SUCCESS = (1, "Operation completed successfully")
    ERROR = (2, "An unknown error occurred")
    INVALID_INPUT = (3, "Invalid input was provided")
    
    # Data-related statuses
    DATA_NOT_FOUND = (4, "The requested data was not found")
    DATA_CONFLICT = (5, "A conflict occurred with the existing data")
    DATA_INVALID = (6, "The data is invalid or corrupted")
    
    # Permission-related statuses
    PERMISSION_DENIED = (7, "You do not have permission to perform this action")
    AUTHENTICATION_FAILED = (8, "Authentication failed or is required")
    
    # Service-related statuses
    SERVICE_UNAVAILABLE = (9, "The service is temporarily unavailable")
    RESOURCE_LIMIT_REACHED = (10, "Resource limits have been reached")
    
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def as_dict(self):
        """
        Returns the Enum as a dictionary for use in JSON responses or other structured outputs.
        """
        return {
            "code": self.code,
            "message": self.message,
        }

    def __str__(self):
        """
        String representation for debugging or logging purposes.
        """
        return f"{self.code}: {self.message}"


class ServiceResponse:
    """
    Represents a response for a particular service operation.
    
    Note at time of writing I am trying to retrofit a bit more structure into the service
    layer by introducing some common approaches to returning status information from
    service methods.  Probably later will introduce a service class or similar to take this
    even further.

    This class is used to encapsulate the state of a service operation, 
    providing details on whether the operation was successful, a message
    giving more context about the operation, and any relevant data
    resulting from the operation.

    :ivar success: Indicates whether the service operation was successful.
    :type success: bool
    :ivar message: Provides additional context or description about the outcome 
        of the service operation.
    :type message: str
    :ivar data: Holds the data resulting from the service operation. Its type 
        may vary depending on the specific operation.
    :type data: Any
    """
    def __init__(self, status: ServiceStatusCode, message: str, data: Dict[str, any]={}):
        self.status: ServiceStatusCode = status
        self.message: str = message
        self.data: Dict = data