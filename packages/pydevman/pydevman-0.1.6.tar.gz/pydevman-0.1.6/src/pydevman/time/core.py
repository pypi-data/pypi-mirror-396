from datetime import datetime
import enum


class DT_FORMAT(enum.Enum):
    DEFAULT_READABLE_PATTERN = "%Y-%m-%d %H:%M:%S"
    DEFAULT_SHORT_PATTERN = "%Y%m%d_%H%M%S"


class DT_FORMAT_LIST(enum.Enum):
    Y_YM_WITH_DASH = ["%Y", "%Y-%m"]
    Y_YM_YMD_WITH_DASH = ["%Y", "%Y-%m", "%Y-%m-%d"]
    Y_YM_YMDA_WITH_DASH = ["%Y", "%Y-%m", "%Y-%m-%d-%a"]


def timestamp_to_datetime_second(timestamp):
    return datetime.fromtimestamp(timestamp)


def timestamp_to_datetime_millisecond(timestamp):
    return datetime.fromtimestamp(timestamp / 1000)


def datetime_to_str(dt: datetime, format: str = DT_FORMAT.DEFAULT_READABLE_PATTERN):
    return dt.strftime(format)


def str_to_datetime(s: str, format: str = DT_FORMAT.DEFAULT_READABLE_PATTERN):
    return datetime.strptime(s, format)
