import pytest
from _pytest.fixtures import FixtureRequest
from custom_python_logger import get_logger

logger = get_logger(__name__)


def requirements(cloud_instance: str, region: str) -> pytest.MarkDecorator:
    return pytest.mark.requirements(
        cloud_instance=cloud_instance,
        region=region,
    )


@requirements(
    cloud_instance="c5.large",
    region="eu-west-1",
)
def test_requirements_with_static_parameters(request: FixtureRequest) -> None:
    assert getattr(request.config, '_selected_requirements', {}).get(request.node.nodeid).get('region') == "eu-west-1"
