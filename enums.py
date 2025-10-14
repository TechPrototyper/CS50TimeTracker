import enum 

class ActionType(enum.Enum):
    WORKDAY_START = "Workday Start"
    WORKDAY_END = "Workday End"
    PROJECT_START = "Project Start"
    PROJECT_END = "Project End"
    PROJECT_RESUME = "Project Resume"
    BREAK_START = "Break Start"
    BREAK_END = "Break End"


class ProjectState(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
