"""
Structures and logic which support the importing and interpretation of fields for a plan from an uploaded file

"""
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Dict, Any


class PlanFieldNameEnum(Enum):
    STICKY_UID = "unique_sticky_activity_id"
    NAME = "activity_name"
    DURATION = "duration"
    MILESTONE_FLAG = "milestone_flag"
    START = "start_date"
    END = "end_date"
    LEVEL = "level"


class StoredPlanFieldTypeEnum(Enum):
    INTEGER = "INT"
    STRING = "STR"
    DATE = "DATE"
    BOOL = "BOOL"


class PlanField:
    def __init__(
            self,
            field_name: PlanFieldNameEnum,
            field_type: StoredPlanFieldTypeEnum,
            field_description: str,
            required_flag: bool,
            sort_index: int
    ):
        self.field_name = field_name
        self.field_type = field_type
        self.field_description = field_description
        self.required_flag = required_flag
        self.sort_index = sort_index

    def get_plan_field_name(self):
        return self.field_name

    def get_stored_plan_field_type(self):
        return self.field_type

    @staticmethod
    def as_choices():
        return [(field.name, field.name) for field in list(PlanFieldEnum)]


class PlanFieldInputSourceEnum(Enum):
    """
    When parsing a file, data can be represented in different ways. For example for an Excel cell has data in a cell
    which has a value (e.g. a number) but it also has other properties which may be relevant, such as indent level,
    which in some cases will be used to represent the level of an activity in the plan.

    So this Enum allows new sources to be added simply as we need them.

    At the time of creation, we only have two sources, which are the value and the indent level.

    This class goes hand in hand with PlanInputField, which will capture all required sources when reading a plan file.
    """
    VALUE = "value"
    INDENT = "indent"


class PlanInputField:
    """
    Captures information for each field in each activity when reading the input plan file.

    At the time of writing only Excel files are supported but this is a generic class and should support the needs
    of other formats when they are added.

    Information from the input file are placed within this class and then the parser will take the information it needs.

    In the case of a Smartsheet exported file, the parser will use the TASK field for two sources:
    - Firstly the Value of the field will be the Task Name
    - Secondly the Indent level of the field will be the Level
    """
    def __init__(self, **field_data_sources):
        for field_name, field_data in field_data_sources.items():
            if self.is_valid_source(field_name):
                setattr(self, field_name, field_data)

    @staticmethod
    def is_valid_source(source_name: str) -> bool:
        return source_name in (source.value for source in PlanFieldInputSourceEnum)

    def get_input_data(self, source: PlanFieldInputSourceEnum = PlanFieldInputSourceEnum.VALUE) -> Any:
        """
        Default set to minimise refactoring required for existing code which only knows about value.

        :param source:
        :return:
        """
        # If requested source hasn't been set, None will be returned. Seems right!
        data = getattr(self, source.value)

        return data


class PlanInputFieldTypeEnum(Enum): # Was RefactoredPlanFieldType
    INDENT_LEVEL = ("FLOAT", "Integer")
    INTEGER = ("INT", "Integer")
    FLOAT = ("FLOAT", "Decimal Number")
    STRING = ("STR", "String")
    STRING_OR_INT = ("STR_OR_INT", "String or integer")
    STRING_nnd = ("STR_nnd", "String of form nnd where nn is an integer value")
    STRING_nn_Days = ("STR_duration_msp", "String representing duration from MSP project in Excel")
    STRING_DATE_DMY_01 = ("STR_DATE_DMY_01", "String of form dd MMM YYYY")
    STRING_DATE_DMY_02 = ("STR_DATE_DMY_02", "String of form dd MMMMM YYYY HH:MM")
    STRING_MILESTONE_YES_NO = ("STR_MSTONE_YES_NO", "Milestone flag as string, Yes or No")
    DATE = ("DATE", "Date (without time)")

    def __init__(self, code, description):
        self.code = code
        self.description = description


class PlanFieldEnum(Enum):
    STICKY_UID = PlanField(PlanFieldNameEnum.STICKY_UID, StoredPlanFieldTypeEnum.STRING, "Unique id for activity", True, 100)
    NAME = PlanField(PlanFieldNameEnum.NAME, StoredPlanFieldTypeEnum.STRING, "Name of activity", True, 200)
    MILESTONE_FLAG = PlanField(PlanFieldNameEnum.MILESTONE_FLAG, StoredPlanFieldTypeEnum.BOOL, "Work effort for activity (not stored, used to work out whether this is a milestone)", False, 250)
    DURATION = PlanField(PlanFieldNameEnum.DURATION, StoredPlanFieldTypeEnum.INTEGER, "Is this activity a mileston", True, 300)
    START = PlanField(PlanFieldNameEnum.START, StoredPlanFieldTypeEnum.DATE, "Start date of activity", True, 400)
    END = PlanField(PlanFieldNameEnum.END, StoredPlanFieldTypeEnum.DATE, "End date of activity", True, 500)
    LEVEL = PlanField(PlanFieldNameEnum.LEVEL, StoredPlanFieldTypeEnum.INTEGER, "The level in the hierarchy of the an activity", False, 600)

    @staticmethod
    def required_fields():
        return [field for field in PlanFieldEnum if field.value.required_flag]

    @classmethod
    def get_by_field_name(cls, field_name):
        for field in cls:
            if field.name == field_name:
                return field
        raise ValueError(f"No field with name {field_name} found")


class FileType(Enum):
    EXCEL_MSP_EXPORT_DEFAULT = (
        "Excel - Default MSP Export",
        "excel-01-msp-export-default-01",
        """Represents mapping of all field names from Microsoft Project export to Excel, using default field names.
        """
    )
    SMARTSHEET_EXPORT_01 = (
        "Excel - Default Smartsheet Export (with Id)",
        "excel-02-smartsheet-export-01",
        """Represents one of several field mappings from a Smartsheet export to Excel.  Note that Smartsheet
        doesn't have build-in columns for ID or Level, so there are no default names."""
        )

    def __init__(self, title, name, description):
        self.title = title
        self.file_type_name = name
        self.description = description

    @classmethod
    def from_name(cls, file_type_name):
        for member in cls:
            if member.file_type_name == file_type_name:
                return member
        raise ValueError(f"No FileType with name '{file_type_name}' found.")

    @classmethod
    def as_choices(cls):
        """
        Returns all members of the enum in a format that can be used in a Django model choices field.
        :return:
        """
        return [(member.file_type_name, member.title) for member in cls]


@dataclass
class PlanInputFieldSpecification: # Was PlanMappedField
    """
    Stores details for a given input field captured as part of importing a file, so that it can be decoded
    during parsing.

    For most cases, the data which is used to populate the relevant plan field on import is the value of a given field
    in the input file, but there may be exceptions.  The only one currently is that for Smartsheet exports, the outline
    level for a task is represented by the indent level of the cell in the Excel file, so we need to add an additional
    attribute of an intput field which allows us to specify this.
    """
    input_field_name: str
    input_field_type: PlanInputFieldTypeEnum
    input_field_source: PlanFieldInputSourceEnum = PlanFieldInputSourceEnum.VALUE

    def get_plan_field_type(self):
        return self.input_field_type

    def __str__(self):
        return f'{self.input_field_name}:{self.input_field_type}'


class FileTypes:
    """
    This is the actual construction of all the supported file types with associated field mappings
    The FileType is what the user will select when uploading a file.

    Note this is a refactor of the original FileType model, so it has been designed to minimise impact of existing code
    for example we have maintained the abiity to access plan_field_mapping_type,
    even thought that model doesn't exist any more

    """
    file_type_data = {
        FileType.EXCEL_MSP_EXPORT_DEFAULT: {
            PlanFieldEnum.STICKY_UID: PlanInputFieldSpecification("ID", PlanInputFieldTypeEnum.STRING),
            PlanFieldEnum.NAME: PlanInputFieldSpecification("Name", PlanInputFieldTypeEnum.STRING),
            PlanFieldEnum.DURATION: PlanInputFieldSpecification("Duration", PlanInputFieldTypeEnum.STRING_nn_Days),
            PlanFieldEnum.START: PlanInputFieldSpecification("Start_Date",
                                                             PlanInputFieldTypeEnum.STRING_DATE_DMY_02),
            PlanFieldEnum.END: PlanInputFieldSpecification("Finish_Date", PlanInputFieldTypeEnum.STRING_DATE_DMY_02),
            PlanFieldEnum.LEVEL: PlanInputFieldSpecification("Outline_Level", PlanInputFieldTypeEnum.INTEGER),
        },
        FileType.SMARTSHEET_EXPORT_01: {
            PlanFieldEnum.STICKY_UID: PlanInputFieldSpecification("Id", PlanInputFieldTypeEnum.FLOAT),
            PlanFieldEnum.NAME: PlanInputFieldSpecification("Task Name", PlanInputFieldTypeEnum.STRING),
            PlanFieldEnum.DURATION: PlanInputFieldSpecification("Duration", PlanInputFieldTypeEnum.STRING_nnd),
            PlanFieldEnum.START: PlanInputFieldSpecification("Start", PlanInputFieldTypeEnum.DATE),
            PlanFieldEnum.END: PlanInputFieldSpecification("Finish", PlanInputFieldTypeEnum.DATE),
            PlanFieldEnum.LEVEL: PlanInputFieldSpecification("Task Name", PlanInputFieldTypeEnum.FLOAT, PlanFieldInputSourceEnum.INDENT)
        },
    }

    @classmethod
    def get_file_type_by_name(cls, file_type_name: str) -> Tuple[FileType, Dict[PlanFieldEnum, PlanInputFieldSpecification]]:
        for file_type, field_mappings in cls.file_type_data.items():
            if file_type.file_type_name == file_type_name:
                return file_type, field_mappings



