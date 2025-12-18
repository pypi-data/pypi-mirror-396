"""Misc functions related to testing"""

# -- Imports ------------------------------------------------------------------

try:
    from pytest import MarkDecorator
except ModuleNotFoundError:
    from types import NoneType as MarkDecorator  # type: ignore[assignment]

# -- Functions ----------------------------------------------------------------

# pylint: disable=import-outside-toplevel


def skip_hardware_tests_ci() -> MarkDecorator | None:
    """Skip hardware dependent test on CI system

    Returns:

        - ``None`` if pytest is not installed or
        - a decorator that skips tests if the environment variable ``CI`` is
          defined

    """

    try:
        from pytest import mark
        from os import environ

        return mark.skipif(
            "CI" in environ and environ["CI"] == "true",
            reason="requires ICOtronic hardware",
        )
    except ModuleNotFoundError:
        return None


# pylint: enable=import-outside-toplevel
