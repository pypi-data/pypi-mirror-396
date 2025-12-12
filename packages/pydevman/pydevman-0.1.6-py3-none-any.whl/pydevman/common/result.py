import enum
from dataclasses import dataclass


class ResultCode(int, enum.Enum):
    SUCCESS = 0
    FAIL = 1
    ERROR = -1


@dataclass
class CommonResult:
    code: ResultCode = 0
    message: str = None
    data: object = None
