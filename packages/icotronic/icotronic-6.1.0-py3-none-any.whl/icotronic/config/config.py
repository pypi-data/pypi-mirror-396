"""Support for changing configuration values

Currently the configuration is mainly used in the hardware (production tests).
"""

# -- Import -------------------------------------------------------------------

from datetime import datetime
from importlib.resources import as_file, files
from os import makedirs
from pathlib import Path
from platform import system
from sys import exit as sys_exit, stderr

from dynaconf import (  # type: ignore[attr-defined]
    Dynaconf,
    ValidationError,
    Validator,
)
from dynaconf.vendor.ruamel.yaml.parser import ParserError
from dynaconf.vendor.ruamel.yaml.scanner import ScannerError
from platformdirs import site_config_dir, user_config_dir
from startfile import startfile

# -- Functions ----------------------------------------------------------------


def handle_incorrect_settings(error_message: str) -> None:
    """Handle incorrect configuration

    Args:

        error_message:

            A text that describes the configuration error

    """

    print(error_message, file=stderr)
    print(
        "\n"
        "• Most likely this problem is caused by an incorrect user "
        "configuration.\n"
        "• Please fix the problem and try again afterwards.\n\n"
        "Opening your user config file in your text editor now",
        file=stderr,
    )
    ConfigurationUtility.open_user_config()
    sys_exit(1)


# -- Classes ------------------------------------------------------------------


class ConfigurationUtility:
    """Access configuration data"""

    app_name = "ICOtronic"
    app_author = "MyTooliT"
    config_filename = "config.yaml"
    site_config_filepath = (
        Path(site_config_dir(app_name, appauthor=app_author)) / config_filename
    )
    user_config_filepath = (
        Path(user_config_dir(app_name, appauthor=app_author)) / config_filename
    )

    @staticmethod
    def open_config_file(filepath: Path):
        """Open configuration file

        Args:

            filepath:
                Path to configuration file

        """

        # Create file, if it does not exist already
        if not filepath.exists():
            filepath.parent.mkdir(
                exist_ok=True,
                parents=True,
            )

            default_user_config = (
                files("icotronic.config")
                .joinpath("user.yaml")
                .read_text(encoding="utf-8")
            )

            with filepath.open("w", encoding="utf8") as config_file:
                config_file.write(default_user_config)

        startfile(filepath)

    @classmethod
    def open_user_config(cls):
        """Open the current users configuration file"""

        try:
            cls.open_config_file(cls.user_config_filepath)
        except FileNotFoundError as error:
            print(
                f"Unable to open user configuration: {error}"
                "\nTo work around this problem please open "
                f"“{cls.user_config_filepath}” in your favorite text "
                "editor",
                file=stderr,
            )


class SettingsIncorrectError(Exception):
    """Raised when the configuration is incorrect"""


class Settings(Dynaconf):
    """Small extension of the settings object for our purposes

    Args:

        default_settings_filepath:
            Filepath to default settings file

        setting_files:
            A list containing setting files in ascending order according to
            importance (most important last).

        arguments:
            All positional arguments

        keyword_arguments:
            All keyword arguments

    """

    def __init__(
        self,
        default_settings_filepath,
        *arguments,
        settings_files: list[str] | None = None,
        **keyword_arguments,
    ) -> None:

        if settings_files is None:
            settings_files = []

        # If we use PyInstaller to create an installer for the package, then
        # loading the default config from the package data (`config.yaml`) does
        # not seem to work. As a workaround we also load data from
        # `default.yaml` inside the user configuration directory. This way you
        # can copy the content of `config.yaml` to this location before
        # executing any code and they ICOtronic library should still work,
        # even when loading the default config from the package data fails.
        user_default_filepath = (
            Path(ConfigurationUtility.user_config_filepath).parent
            / "default.yaml"
        )
        settings_files = [
            default_settings_filepath,
            ConfigurationUtility.site_config_filepath,
            user_default_filepath,
            ConfigurationUtility.user_config_filepath,
        ] + settings_files

        super().__init__(
            settings_files=settings_files,
            *arguments,
            **keyword_arguments,
        )
        self.validate_settings()

    # pylint: disable=too-many-locals

    def validate_settings(self) -> None:
        """Check settings for errors"""

        def must_exist(*arguments, **keyword_arguments):
            """Return Validator which requires setting to exist"""

            return Validator(*arguments, must_exist=True, **keyword_arguments)

        config_system = "mac" if system() == "Darwin" else system().lower()
        can_validators = [
            must_exist(f"can.{config_system}.bitrate", is_type_of=int),
            must_exist(
                f"can.{config_system}.channel",
                f"can.{config_system}.interface",
                is_type_of=str,
            ),
        ]
        logger_validators = [
            must_exist(
                "logger.can.level",
                is_type_of=str,
                is_in=(
                    "CRITICAL",
                    "ERROR",
                    "WARNING",
                    "INFO",
                    "DEBUG",
                    "NOTSET",
                ),
            )
        ]
        measurement_validators = [
            must_exist(
                "measurement.output.directory",
                "measurement.output.filename",
                is_type_of=str,
            ),
        ]
        self.validators.register(
            *can_validators, *logger_validators, *measurement_validators
        )

        try:
            self.validators.validate()
        except ValidationError as error:
            config_files_text = "\n".join((
                f"  • {ConfigurationUtility.site_config_filepath}",
                f"  • {ConfigurationUtility.user_config_filepath}",
            ))
            raise SettingsIncorrectError(
                f"Incorrect configuration: {error}\n\n"
                "Please make sure that the configuration files:\n\n"
                f"{config_files_text}\n\n"
                "contain the correct configuration values"
            ) from error

    # pylint: enable=too-many-locals

    def output_directory(self) -> Path:
        """Get the HDF output directory

        Returns:

            The HDF output directory as path object

        """

        directory = Path(settings.measurement.output.directory)
        return directory if directory.is_absolute() else directory.expanduser()

    def get_output_filepath(self) -> Path:
        """Get filepath of HDF measurement file

        The filepath returned by this method will always include a current
        timestamp to make sure that there are no conflicts with old output
        files.

        Returns:

            The path to the current HDF file

        """

        directory = self.output_directory()
        filename = Path(settings.measurement.output.filename)

        if not filename.suffix:
            filename = filename.with_suffix(".hdf5")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = directory.joinpath(
            f"{filename.stem}_{timestamp}{filename.suffix}"
        )

        return filepath

    def check_output_directory(self) -> None:
        """Check the output directory

        If the directory does not already exist, then this function will
        try to create it.

        """

        directory = self.output_directory()

        if directory.exists() and not directory.is_dir():
            raise NotADirectoryError(
                f"The output directory “{directory}” points to an "
                "existing file not a directory"
            )

        if not directory.is_dir():
            try:
                makedirs(str(directory))
            except OSError as error:
                raise OSError(
                    "Unable to create the output directory "
                    f"“{directory}”: {error}"
                ) from error


# -- Attributes ---------------------------------------------------------------


with as_file(
    files("icotronic.config").joinpath(ConfigurationUtility.config_filename)
) as repo_settings_filepath:
    try:
        settings = Settings(default_settings_filepath=repo_settings_filepath)
    except SettingsIncorrectError as settings_incorrect_error:
        handle_incorrect_settings(f"{settings_incorrect_error}")
    except (ParserError, ScannerError) as parsing_error:
        handle_incorrect_settings(
            f"Unable to parse configuration: {parsing_error}"
        )
