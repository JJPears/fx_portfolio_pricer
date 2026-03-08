from enum import Enum


class OptionType(str, Enum):
    CALL = "Call"
    PUT = "Put"

    @classmethod
    def _missing_(cls, value: object) -> "OptionType | None":
        """Case insensitive lookup — 'call', 'CALL', 'Call' all resolve to OptionType.CALL"""
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None
