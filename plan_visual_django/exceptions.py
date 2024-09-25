class DuplicateSwimlaneException(Exception):
    pass


class NoActivitiesInVisualException(Exception):
    pass


class PlanParseError(Exception):
    pass


class PlanMappingIncompleteError(Exception):
    pass


class SuppliedPlanIncompleteError(Exception):
    pass

class ExcelPlanSheetNotFound(Exception):
    pass


class AddPlanError(Exception):
    pass


class MissingPlotableIdError(Exception):
    pass