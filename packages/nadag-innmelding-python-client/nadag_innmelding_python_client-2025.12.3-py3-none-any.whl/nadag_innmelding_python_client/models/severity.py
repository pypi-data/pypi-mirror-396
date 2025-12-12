from enum import Enum


class Severity(str, Enum):
    ERROR = "ERROR"
    FATAL = "FATAL"
    OK = "OK"
    WARNING = "WARNING"

    def __str__(self) -> str:
        return str(self.value)
