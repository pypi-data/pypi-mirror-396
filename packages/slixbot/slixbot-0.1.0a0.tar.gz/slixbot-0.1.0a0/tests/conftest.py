import os
from typing import NamedTuple

import pytest


class Secret(NamedTuple):
    jid: str
    password: str


@pytest.fixture
def secret1(prosody) -> Secret:
    return Secret(f"test1@{prosody}", "password")


@pytest.fixture
def secret2(prosody) -> Secret:
    return Secret(f"test2@{prosody}", "password")


@pytest.fixture
def prosody() -> str:
    return "prosody" if os.getenv("CI") else "localhost"
