from enum import Enum, IntEnum


class ContentCode(IntEnum):
    NONE_CONTENT_CODE = 0
    EMPTY = 10
    FULL = 11
    LOW_LEVEL = 20
    HIGH_LEVEL = 21
    BIG_BOX = 30
    MEDIUM_BOX = 31
    SMALL_BOX = 32
    MINI_BOX = 33
    COOLING_BOX = 3

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.name == value:
                    return member
            raise ValueError(f"{value} is not a valid {cls.__name__}")


class ContentCodeUpdateStatus(str, Enum):
    NONE_CONTENT_CODE_UPDATE = "NONE_CONTENT_CODE_UPDATE"
    FAILED_CONTENT_CODE_UPDATE = "FAILED_CONTENT_CODE_UPDATE"
    SUCCEEDED_CONTENT_CODE_UPDATE = "SUCCEEDED_CONTENT_CODE_UPDATE"




