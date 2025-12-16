import types
import typing
import unittest

import pyquoks.data
import pyquoks.utils


class TestCase(unittest.TestCase, pyquoks.utils._HasRequiredAttributes):
    """
    Class for performing unit testing

    **Required attributes**::

        _MODULE_NAME = __name__

    Attributes:
        _MODULE_NAME: Name of the testing module
    """

    _REQUIRED_ATTRIBUTES = {
        "_MODULE_NAME"
    }

    _MODULE_NAME: str

    def __init__(self, *args, **kwargs) -> None:
        self._check_attributes()

        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls) -> None:
        cls._logger = pyquoks.data.LoggerService(
            filename=__name__,
        )

    def _get_func_name(self, func_name: str) -> str:
        return f"{self._MODULE_NAME}.{func_name}"

    def assert_equal(
            self,
            func_name: str,
            test_data: object,
            test_expected: object,
            message: str = None,
    ) -> None:
        self._logger.info(
            msg=(
                f"{self._get_func_name(func_name)}:\n"
                f"{f"Message: {message}\n" if message else ""}"
                f"Data: {test_data}\n"
                f"Expected: {test_expected}\n"
            ),
        )

        try:
            self.assertEqual(
                first=test_data,
                second=test_expected,
                msg=message,
            )
        except Exception as exception:
            self._logger.log_error(
                exception=exception,
                raise_again=True,
            )

    def assert_raises(
            self,
            func_name: str,
            test_func: typing.Callable,
            test_exception: type[BaseException],
            message: str = None,
            *args,
            **kwargs,
    ) -> None:
        self._logger.info(
            msg=(
                f"{self._get_func_name(func_name)}:\n"
                f"{f"Message: {message}\n" if message else ""}"
                f"Function: {test_func.__name__}()\n"
                f"Exception: {test_exception.__name__}\n"
            ),
        )

        try:
            self.assertRaises(
                test_exception,
                test_func,
                *args,
                **kwargs,
            )
        except Exception as exception:
            self._logger.log_error(
                exception=exception,
                raise_again=True,
            )

    def assert_type(
            self,
            func_name: str,
            test_data: object,
            test_type: type | types.UnionType,
            message: str = None,
    ) -> None:
        self._logger.info(
            msg=(
                f"{self._get_func_name(func_name)}:\n"
                f"{f"Message: {message}\n" if message else ""}"
                f"Type: {type(test_data).__name__}\n"
                f"Expected: {test_type.__name__}\n"
            ),
        )

        try:
            self.assertIsInstance(
                obj=test_data,
                cls=test_type,
                msg=message,
            )
        except Exception as exception:
            self._logger.log_error(
                exception=exception,
                raise_again=True,
            )
