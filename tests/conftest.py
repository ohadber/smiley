"""
Configuration for pytest's tests.
"""
import os
from pathlib import Path

import pytest

from tests.data_population import Generator


@pytest.fixture
def tests_dir():
    """
    Get the path of the tests directory.

    :return: The path of the tests directory.
    :rtype: Path
    """
    return Path(os.path.realpath(__file__)).parent


@pytest.fixture
def image_dir(tests_dir):
    """
    Get the path of the image dir.

    :return: The image directory.
    :rtype: Path
    """
    return tests_dir / "images"


@pytest.fixture
def generator(mocker):
    """
    Create a generator object which will assist the tests object creation.

    :type mocker: pytest_mock.MockFixture
    :return: an instance of the Generator helper-class.
    """
    return Generator(mocker)
