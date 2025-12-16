import datetime
import os
import sys

import psutil


class _HasRequiredAttributes:
    """
    Assistive class for checking required attributes

    **Required attributes**::

        _REQUIRED_ATTRIBUTES = {"_ATTRIBUTES", "_OBJECTS"}

    Attributes:
        _REQUIRED_ATTRIBUTES: Set of required attributes in the class
    """

    _REQUIRED_ATTRIBUTES: set[str]

    def _check_attributes(self) -> None:
        if hasattr(self, "_REQUIRED_ATTRIBUTES"):
            for attribute in self._REQUIRED_ATTRIBUTES:
                if not hasattr(self, attribute):
                    raise AttributeError(f"The required class attribute is not set! ({attribute})")


def get_path(relative_path: str, use_meipass: bool = False) -> str:
    """
    :param relative_path: Relative path of the file
    :param use_meipass: Whether or not ``sys._MEIPASS`` should be used
    :return: Absolute path for provided relative path
    """

    if use_meipass and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_process_created_datetime(pid: int = os.getpid()) -> datetime.datetime:
    """
    :param pid: ID of the process
    :return: Datetime when the process was created
    """

    process = psutil.Process(pid)

    return datetime.datetime.fromtimestamp(
        timestamp=process.create_time(),
    )
