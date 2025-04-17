import re
from enum import Enum
from pydantic import BaseModel


class SizeUnit(str, Enum):
    GB = "GB"
    MB = "MB"
    KB = "KB"

    @classmethod
    def from_string(cls, string: str) -> 'SizeUnit':
        unit = string.strip().upper()
        if unit.endswith('S'):
            unit = unit[:-1]
        try:
            return cls(unit)
        except ValueError:
            raise ValueError(f"Invalid size unit: '{unit}'")


class Size(BaseModel):
    value: float
    unit: SizeUnit

    @classmethod
    def from_string(cls, string: str) -> 'Size':
        match = re.search(r"(\d+(?:\.\d+)?)\s*(GB|MB|KB)s?", string, re.IGNORECASE)

        if not match:
            raise ValueError(f"Could not parse the size from string: '{string}'")

        value = float(match.group(1))
        unit = SizeUnit.from_string(match.group(2))

        return cls(value=value, unit=unit)
