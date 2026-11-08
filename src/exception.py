"""Project exception types with useful source location details."""

import sys
from types import ModuleType


def error_message_detail(
    error: BaseException, error_detail: ModuleType = sys
) -> str:
    """Format an exception with the file, function, and line where it occurred."""
    _, _, traceback = error_detail.exc_info()
    if traceback is None:
        traceback = error.__traceback__
    if traceback is None:
        return f"{type(error).__name__}: {error}"

    frame = traceback.tb_frame
    location = (
        f"{frame.f_code.co_filename}:{traceback.tb_lineno} "
        f"in {frame.f_code.co_name}"
    )
    return f"{location}: {type(error).__name__}: {error}"


class CustomException(Exception):
    """Exception that includes the original error's source location."""

    def __init__(
        self, error: BaseException, error_detail: ModuleType = sys
    ) -> None:
        self.original_error = error
        self.error_message = error_message_detail(error, error_detail)
        super().__init__(self.error_message)


# Keep the original name working for code that imported it before the rename.
customException = CustomException


__all__ = ["CustomException", "customException", "error_message_detail"]
