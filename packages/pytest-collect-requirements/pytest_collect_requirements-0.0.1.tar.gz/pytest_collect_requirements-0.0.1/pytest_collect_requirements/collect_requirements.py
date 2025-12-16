import pytest
from _pytest.config import Config, Parser
from _pytest.main import Session
from _pytest.python import Function
from custom_python_logger import get_logger, json_pretty_format

from pytest_collect_requirements.helper import write_text

logger = get_logger(__name__)


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--collect-requirements",
        action="store_true",
        help="Collect infrastructure requirements only",
    )
    parser.addoption(
        "--save-to",
        action="store",
        default="logs/test_requirements.json",
        help="Path to save collected requirements",
    )


def pytest_configure(config: Config) -> None:
    if not config.getoption("--collect-requirements"):
        return


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: Config, items: list[Function]) -> None:
    if not config.getoption("--collect-requirements"):
        return

    selected_requirements = {}

    for item in items:
        if not (marker := item.get_closest_marker("requirements")):
            continue

        selected_requirements[item.nodeid] = {
            "nodeid": item.nodeid,
            **marker.kwargs,
        }

    config._all_requirements = selected_requirements  # pylint: disable=W0212


def pytest_collection_finish(session: Session) -> None:
    if not session.config.getoption("--collect-requirements"):
        return

    if not (_all_requirements := getattr(session.config, "_all_requirements", None)):
        return

    _selected_requirements = {}
    for item in session.items:
        _selected_requirements[item.nodeid] = _all_requirements[item.nodeid]
    session.config._selected_requirements = _selected_requirements  # pylint: disable=W0212
    logger.debug(f"Collected requirements: {json_pretty_format(_selected_requirements)}")

    write_text(
        text=json_pretty_format(_selected_requirements),
        filename=session.config.getoption("--save-to")
    )
