from enum import Enum


class EnumChoices(Enum):

    @classmethod
    def choices(cls):
        return [(item.value, item.name.replace('_', ' ').title()) for item in cls]

    @classmethod
    def from_string(cls, value: str):
        normalized = value.strip().capitalize()
        try:
            return cls[normalized]
        except KeyError:
            raise ValueError(f"'{value}' is not a valid value of {cls.__name__}")