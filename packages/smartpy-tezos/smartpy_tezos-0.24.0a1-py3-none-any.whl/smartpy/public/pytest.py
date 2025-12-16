import pytest

from .scenario import test_scenario


@pytest.fixture
def scenario():
    """Pytest fixture that provides a scenario context"""
    return test_scenario()
