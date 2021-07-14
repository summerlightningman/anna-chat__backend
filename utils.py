from datetime import datetime

from config import DB_DATETIME_PATTERN, RU_DATETIME_PATTERN


def datetime_from_str(datetime_: str) -> [datetime, None]:
    return datetime.strptime(datetime_, DB_DATETIME_PATTERN) if datetime_ else None


def str_from_datetime(datetime_) -> [datetime, None]:
    return datetime_.strftime(RU_DATETIME_PATTERN)
