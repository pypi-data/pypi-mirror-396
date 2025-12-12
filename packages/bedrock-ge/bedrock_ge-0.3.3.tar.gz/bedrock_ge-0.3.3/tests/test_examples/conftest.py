from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def examples_dir():
    return Path(__file__).parent.parent.parent / "examples"
