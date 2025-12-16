import configparser
import datetime
import io
import json
import logging
import os
import sqlite3
import sys
import typing

import PIL.Image
import pydantic
import requests

import pyquoks.utils


# region Providers

class AssetsProvider(pyquoks.utils._HasRequiredAttributes):
    """
    Class for providing various assets data

    **Required attributes**::

        _OBJECTS = {"images": ImagesDirectory, "example": ExampleNetwork}

        # Predefined:

        _PATH = pyquoks.utils.get_path("assets/")

    Attributes:
        _OBJECTS: Dictionary with names of attributes and child objects
        _PATH: Path to the directory with assets folders
    """

    class Directory(pyquoks.utils._HasRequiredAttributes):
        """
        Class that represents a directory with various assets

        **Required attributes**::

            _ATTRIBUTES = {"picture1", "picture2"}

            _PATH = "images/"

            _FILENAME = "{0}.png"

        Attributes:
            _ATTRIBUTES: Names of files in the directory
            _PATH: Path to the directory with assets files
            _FILENAME: Filename of assets files
            _parent: Parent object
        """

        _REQUIRED_ATTRIBUTES = {
            "_ATTRIBUTES",
            "_PATH",
            "_FILENAME",
        }

        _ATTRIBUTES: set[str]

        _PATH: str

        _FILENAME: str

        _parent: AssetsProvider | None

        def __init__(self, parent: AssetsProvider = None) -> None:
            self._check_attributes()

            if parent:
                self._parent = parent
            elif not hasattr(self, "_parent") or not self._parent:
                raise AttributeError("This class cannot be initialized without a parent object!")

            self._PATH = self._parent._PATH + self._PATH

            for attribute in self._ATTRIBUTES:
                try:
                    setattr(self, attribute, self._parent.file_image(
                        path=self._PATH + self._FILENAME.format(attribute),
                    ))
                except Exception:
                    setattr(self, attribute, None)

    class Network(pyquoks.utils._HasRequiredAttributes):
        """
        Class that represents a set of images obtained from a network

        **Required attributes**::

            _URLS = {"example": "https://example.com/image.png"}

        Attributes:
            _URLS: Dictionary with names of attributes and URLs
            _parent: Parent object
        """

        _REQUIRED_ATTRIBUTES = {
            "_URLS",
        }

        _URLS: dict[str, str]

        _parent: AssetsProvider | None

        def __init__(self, parent: AssetsProvider = None) -> None:
            self._check_attributes()

            if parent:
                self._parent = parent
            elif not hasattr(self, "_parent") or not self._parent:
                raise AttributeError("This class cannot be initialized without a parent object!")

            for attribute, url in self._URLS.items():
                try:
                    setattr(self, attribute, self._parent.network_image(
                        url=url,
                    ))
                except Exception:
                    setattr(self, attribute, None)

    _REQUIRED_ATTRIBUTES = {
        "_OBJECTS",
        "_PATH",
    }

    _OBJECTS: dict[str, type]

    _PATH: str = pyquoks.utils.get_path("assets/")

    def __init__(self) -> None:
        self._check_attributes()

        for attribute, child_class in self._OBJECTS.items():
            setattr(self, attribute, child_class(self))

    @staticmethod
    def file_image(path: str) -> PIL.Image.Image:
        """
        :param path: Absolute path of the image file
        :return: Image object from a file
        """

        with open(path, "rb") as file:
            return PIL.Image.open(
                fp=io.BytesIO(file.read()),
            )

    @staticmethod
    def network_image(url: str) -> PIL.Image.Image:
        """
        :param url: URL of the image file
        :return: Image object from a URL
        """

        return PIL.Image.open(
            fp=io.BytesIO(requests.get(url).content),
        )


class StringsProvider(pyquoks.utils._HasRequiredAttributes):
    """
    Class for providing various strings data

    **Required attributes**::

        _OBJECTS = {"menu": MenuStrings}

    Attributes:
        _OBJECTS: Dictionary with names of attributes and child objects
    """

    class Strings:
        """
        Class that represents a container for strings
        """

        # noinspection PyUnusedLocal
        def __init__(self, parent: StringsProvider) -> None:
            ...  # TODO

    _REQUIRED_ATTRIBUTES = {
        "_OBJECTS",
    }

    _OBJECTS: dict[str, type]

    def __init__(self) -> None:
        self._check_attributes()

        for attribute, child_class in self._OBJECTS.items():
            setattr(self, attribute, child_class(self))


# endregion

# region Managers

class ConfigManager(pyquoks.utils._HasRequiredAttributes):
    """
    Class for managing data in configuration file

    **Required attributes**::

        _OBJECTS = {"settings": SettingsConfig}

        # Predefined

        _PATH = pyquoks.utils.get_path("config.ini")

    Attributes:
        _OBJECTS: Dictionary with names of attributes and child objects
        _PATH: Path to the configuration file
    """

    class Config(pyquoks.utils._HasRequiredAttributes):
        """
        Class that represents a section in configuration file

        **Required attributes**::

            _SECTION = "Settings"

            _VALUES = {"version": str, "beta": bool}

        Attributes:
            _SECTION: Name of the section in configuration file
            _VALUES: Dictionary with settings and their types
            _parent: Parent object
        """

        _REQUIRED_ATTRIBUTES = {
            "_SECTION",
            "_VALUES",
        }

        _SECTION: str

        _VALUES: dict[str, type]

        _incorrect_content_exception = configparser.ParsingError(
            source="configuration file is filled incorrectly",
        )

        _parent: ConfigManager

        def __init__(self, parent: ConfigManager = None) -> None:
            self._check_attributes()

            if parent:
                self._parent = parent
            elif not hasattr(self, "_parent") or not self._parent:
                raise AttributeError("This class cannot be initialized without a parent object!")

            self._config = configparser.ConfigParser()
            self._config.read(self._parent._PATH)

            if not self._config.has_section(self._SECTION):
                self._config.add_section(self._SECTION)

            for attribute, object_type in self._VALUES.items():
                try:
                    setattr(self, attribute, self._config.get(self._SECTION, attribute))
                except Exception:
                    self._config.set(self._SECTION, attribute, object_type.__name__)
                    with open(self._parent._PATH, "w", encoding="utf-8") as file:
                        self._config.write(file)

            for attribute, object_type in self._VALUES.items():
                try:
                    match object_type():
                        case bool():
                            if getattr(self, attribute) not in [str(True), str(False)]:
                                setattr(self, attribute, None)
                                raise self._incorrect_content_exception
                            else:
                                setattr(self, attribute, getattr(self, attribute) == str(True))
                        case int():
                            setattr(self, attribute, int(getattr(self, attribute)))
                        case float():
                            setattr(self, attribute, float(getattr(self, attribute)))
                        case str():
                            pass
                        case dict() | list():
                            setattr(self, attribute, json.loads(getattr(self, attribute)))
                        case _:
                            raise ValueError(f"{object_type.__name__} type is not supported!")
                except Exception:
                    setattr(self, attribute, None)

                    raise self._incorrect_content_exception

        @property
        def _values(self) -> dict | None:
            """
            :return: Values stored in this section
            """

            try:
                return {
                    attribute: getattr(self, attribute) for attribute in self._VALUES.keys()
                }
            except Exception:
                return None

        def update(self, **kwargs) -> None:
            """
            Updates provided attributes in object
            """

            for attribute, value in kwargs.items():

                if attribute not in self._VALUES.keys():
                    raise AttributeError(f"{attribute} is not specified!")

                object_type = self._VALUES.get(attribute)

                if not isinstance(
                        value,
                        typing.get_origin(object_type) if typing.get_origin(object_type) else object_type,
                ):
                    raise AttributeError(
                        f"{attribute} has incorrect type! (must be {object_type.__name__})",
                    )

                setattr(self, attribute, value)

                self._config.set(self._SECTION, attribute, value)
                with open(self._parent._PATH, "w", encoding="utf-8") as file:
                    self._config.write(file)

    _REQUIRED_ATTRIBUTES = {
        "_OBJECTS",
        "_PATH",
    }

    _OBJECTS: dict[str, type]

    _PATH: str = pyquoks.utils.get_path("config.ini")

    def __init__(self) -> None:
        self._check_attributes()

        for attribute, child_class in self._OBJECTS.items():
            setattr(self, attribute, child_class(self))


class DataManager(pyquoks.utils._HasRequiredAttributes):
    """
    Class for managing data from JSON-like files

    **Required attributes**::

        _OBJECTS = {"users": list[UserModel]}

        # Predefined:

        _PATH = pyquoks.utils.get_path("data/")

        _FILENAME = "{0}.json"

    Attributes:
        _OBJECTS: Dictionary with filenames and types of models
        _PATH: Path to the directory with JSON-like files
        _FILENAME: Filename of JSON-like files
    """

    _REQUIRED_ATTRIBUTES = {
        "_OBJECTS",
        "_PATH",
        "_FILENAME",
    }

    _OBJECTS: dict[str, type[pydantic.BaseModel] | list[type[pydantic.BaseModel]]]

    _PATH: str = pyquoks.utils.get_path("data/")

    _FILENAME: str = "{0}.json"

    def __init__(self) -> None:
        self._check_attributes()

        for attribute, object_type in self._OBJECTS.items():
            try:
                with open(self._PATH + self._FILENAME.format(attribute), "rb") as file:
                    data = json.loads(file.read())

                    if typing.get_origin(object_type) == list:
                        setattr(self, attribute, [typing.get_args(object_type)[0](**model) for model in data])
                    else:
                        setattr(self, attribute, object_type(**data))
            except Exception:
                setattr(self, attribute, None)

    def update(self, **kwargs) -> None:
        """
        Updates provided attributes in object
        """

        for attribute, value in kwargs.items():
            value: pydantic.BaseModel | list[pydantic.BaseModel]

            if attribute not in self._OBJECTS.keys():
                raise AttributeError(f"{attribute} is not specified!")

            object_type = self._OBJECTS.get(attribute)

            if not isinstance(
                    value,
                    typing.get_origin(object_type) if typing.get_origin(object_type) else object_type,
            ):
                raise AttributeError(
                    f"{attribute} has incorrect type! (must be {object_type.__name__})",
                )

            setattr(self, attribute, value)

            os.makedirs(
                name=self._PATH,
                exist_ok=True,
            )

            with open(self._PATH + self._FILENAME.format(attribute), "w", encoding="utf-8") as file:
                json.dump(
                    [model.model_dump() for model in value] if typing.get_origin(
                        object_type,
                    ) == list else value.model_dump(),
                    fp=file,
                    ensure_ascii=False,
                    indent=2,
                )


class DatabaseManager(pyquoks.utils._HasRequiredAttributes):
    """
    Class for managing database connections

    **Required attributes**::

        _OBJECTS = {"users": UsersDatabase}

        # Predefined

        _PATH = pyquoks.utils.get_path("db/")

    Attributes:
        _OBJECTS: Dictionary with names of attributes and child objects
        _PATH: Path to the directory with databases
    """

    class Database(sqlite3.Connection, pyquoks.utils._HasRequiredAttributes):
        """
        Class that represents a database connection

        **Required attributes**::

            _NAME = "users"

            _SQL = f\"""CREATE TABLE IF NOT EXISTS {_NAME} (user_id INTEGER PRIMARY KEY NOT NULL)\"""

            # Predefined

            _FILENAME = "{0}.db"

        Attributes:
            _NAME: Name of the database
            _SQL: SQL expression for creating a table
            _FILENAME: Filename of the database
            _parent: Parent object
        """

        _REQUIRED_ATTRIBUTES = {
            "_NAME",
            "_SQL",
            "_FILENAME",
        }

        _NAME: str

        _SQL: str

        _FILENAME: str = "{0}.db"

        _parent: DatabaseManager

        def __init__(self, parent: DatabaseManager = None) -> None:
            self._check_attributes()

            if parent:
                self._parent = parent
            elif not hasattr(self, "_parent") or not self._parent:
                raise AttributeError("This class cannot be initialized without a parent object!")

            self._FILENAME = self._FILENAME.format(self._NAME)

            super().__init__(
                database=self._parent._PATH + self._FILENAME,
                check_same_thread=False,
            )
            self.row_factory = sqlite3.Row

            cursor = self.cursor()

            cursor.execute(
                self._SQL,
            )

            self.commit()

    _REQUIRED_ATTRIBUTES = {
        "_OBJECTS",
        "_PATH",
    }

    _OBJECTS: dict[str, type]

    _PATH: str = pyquoks.utils.get_path("db/")

    def __init__(self) -> None:
        self._check_attributes()

        os.makedirs(
            name=self._PATH,
            exist_ok=True,
        )

        for attribute, child_class in self._OBJECTS.items():
            setattr(self, attribute, child_class(self))

    def close_all(self) -> None:
        """
        Closes all database connections
        """

        for attribute in self._OBJECTS.keys():
            getattr(self, attribute).close()


# endregion

# region Services

class LoggerService(logging.Logger):
    """
    Class that provides methods for parallel logging

    Attributes:
        _LOG_PATH: Path to the logs file
    """

    _LOG_PATH: str | None

    def __init__(
            self,
            filename: str,
            level: int = logging.NOTSET,
            file_handling: bool = True,
            path: str = pyquoks.utils.get_path("logs/"),
    ) -> None:
        super().__init__(filename, level)

        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.stream_handler.setFormatter(
            logging.Formatter(
                fmt="$levelname $asctime $name - $message",
                datefmt="%d-%m-%y %H:%M:%S",
                style="$",
            )
        )
        self.addHandler(self.stream_handler)

        if file_handling:
            os.makedirs(
                name=path,
                exist_ok=True
            )
            self._LOG_PATH = path + f"{int(datetime.datetime.now().timestamp())}.{filename}.log"

            self.file_handler = logging.FileHandler(
                filename=self._LOG_PATH,
                encoding="utf-8",
            )
            self.file_handler.setFormatter(
                logging.Formatter(
                    fmt="$levelname $asctime - $message",
                    datefmt="%d-%m-%y %H:%M:%S",
                    style="$",
                ),
            )
            self.addHandler(self.file_handler)
        else:
            self._LOG_PATH = None

    @property
    def file(self) -> typing.IO | None:
        """
        :return: Opened file-like object of current logs
        """

        if self._LOG_PATH:
            return open(self._LOG_PATH, "rb")
        else:
            return None

    def log_error(self, exception: Exception, raise_again: bool = False) -> None:
        """
        Logs an exception with detailed traceback

        :param exception: Exception to be logged
        :param raise_again: Whether or not exception should be raised again
        """

        self.error(
            msg=exception,
            exc_info=True,
        )

        if raise_again:
            raise exception

# endregion
