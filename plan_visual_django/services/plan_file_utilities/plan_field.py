"""
Structures and logic which support the importing and interpretation of fields for a plan from an uploaded file

"""
from enum import Enum


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


class RefactoredPlanField:
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


class PlanFieldEnum(Enum):
    STICKY_UID = RefactoredPlanField(PlanFieldNameEnum.STICKY_UID, StoredPlanFieldTypeEnum.STRING, "Unique id for activity", True, 100)
    NAME = RefactoredPlanField(PlanFieldNameEnum.NAME, StoredPlanFieldTypeEnum.STRING, "Name of activity", True, 200)
    MILESTONE_FLAG = RefactoredPlanField(PlanFieldNameEnum.MILESTONE_FLAG, StoredPlanFieldTypeEnum.BOOL, "Work effort for activity (not stored, used to work out whether this is a milestone)", False, 250)
    DURATION = RefactoredPlanField(PlanFieldNameEnum.DURATION, StoredPlanFieldTypeEnum.INTEGER, "Is this activity a mileston", True, 300)
    START = RefactoredPlanField(PlanFieldNameEnum.START, StoredPlanFieldTypeEnum.DATE, "Start date of activity", True, 400)
    END = RefactoredPlanField(PlanFieldNameEnum.END, StoredPlanFieldTypeEnum.DATE, "End date of activity", True, 500)
    LEVEL = RefactoredPlanField(PlanFieldNameEnum.LEVEL, StoredPlanFieldTypeEnum.INTEGER, "The level in the hierarchy of the an activity", False, 600)

    @staticmethod
    def required_fields():
        return [field for field in PlanFieldEnum if field.value.required_flag]

    @classmethod
    def get_by_field_name(cls, field_name):
        for field in cls:
            if field.name == field_name:
                return field
        raise ValueError(f"No field with name {field_name} found")
