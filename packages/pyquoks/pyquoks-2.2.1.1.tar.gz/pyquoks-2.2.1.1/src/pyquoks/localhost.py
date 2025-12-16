import typing

import flask
import waitress

import pyquoks.utils


class LocalhostFlask(flask.Flask, pyquoks.utils._HasRequiredAttributes):
    """
    Class for creating a simple localhost server

    **Required attributes**::

        _RULES = {"/": self.base_redirect}

    Attributes:
        _RULES: Dictionary with rules and functions
    """

    _REQUIRED_ATTRIBUTES = {
        "_RULES",
    }

    _RULES: dict[str, typing.Callable]

    def __init__(self, import_name: str) -> None:
        self._check_attributes()

        super().__init__(
            import_name=import_name,
        )

        for rule, view_func in self._RULES.items():
            self.add_url_rule(
                rule=rule,
                view_func=view_func,
            )

    def serve(self, port: int) -> None:
        """
        Starts this Flask application

        :param port: Port number
        """

        waitress.serve(
            app=self,
            host="127.0.0.1",
            port=port,
        )
