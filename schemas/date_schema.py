import re

from enum import Enum
from pydantic import BaseModel


class DateUnit(str, Enum):
    YEAR = "year"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"

    @classmethod
    def from_string(cls, string: str) -> 'DateUnit':
        unit = string.lower().strip()
        if unit.endswith('s'):
            unit = unit[:-1]
        try:
            return cls(unit)
        except ValueError:
            raise ValueError(f"Invalid date unit: '{unit}'")


class Date(BaseModel):
    value: int
    unit: DateUnit

    @classmethod
    def from_string(cls, string: str) -> 'Date':
        if "decade" in string:
            match = re.search(r"(\d+)\s*decade", string)
            if match:
                value = int(match.group(1)) * 10
                return cls(value=value, unit=DateUnit.YEAR)
            else:
                raise ValueError(f"Could not parse the decade format: '{string}'")

        match = re.search(r"(\d+)\s*(year|month|week|day|hour|minute)s?\s*(ago)?", string, re.IGNORECASE)

        if not match:
            raise ValueError(f"Could not parse the date from string: '{string}'")

        value = int(match.group(1))
        unit = DateUnit.from_string(match.group(2))

        return cls(value=value, unit=unit)
