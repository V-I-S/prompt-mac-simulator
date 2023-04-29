from typing import Type


class SanityCheckError(Exception):
    def __init__(self, message: str, reason: str):
        super().__init__(message)
        self.reason = reason
