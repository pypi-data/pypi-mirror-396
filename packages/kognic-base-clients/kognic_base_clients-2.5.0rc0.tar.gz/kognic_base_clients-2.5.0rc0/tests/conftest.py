import json
import os
from dataclasses import dataclass
from pathlib import Path

import pytest

TEST_URL = "https://kognic-test-url.com"
TEST_URL_2 = "https://kognic-test-url-2.com"
JSON_RESULT = {"id": "9ed7dasdasd-08ff-4ae1-8952-37e3a323eb08"}
BYTES_RESULT = json.dumps(JSON_RESULT).encode("utf-8")

DIR_PATH = Path(os.path.dirname(os.path.realpath(__file__)))
RANDOM_DATA_PATH = DIR_PATH / "resources/random-data.txt"
RANDOM_DATA_2_PATH = DIR_PATH / "resources/random-data-2.txt"


@dataclass
class GetSpec:
    url: str
    result_bytes: bytes
    result_json: dict


@dataclass
class PutSpec:
    url: str
    path: Path
    content: bytes


def read_file_content(file_path):
    with open(file_path, "rb") as f:
        return f.read()


RANDOM_DATA = read_file_content(RANDOM_DATA_PATH)
RANDOM_DATA_2 = read_file_content(RANDOM_DATA_2_PATH)


@pytest.fixture
def get_spec():
    return GetSpec(url=TEST_URL, result_bytes=BYTES_RESULT, result_json=JSON_RESULT)


@pytest.fixture
def put_spec():
    return PutSpec(url=TEST_URL, path=RANDOM_DATA_PATH, content=RANDOM_DATA)


@pytest.fixture
def put_spec_2():
    return PutSpec(url=TEST_URL_2, path=RANDOM_DATA_2_PATH, content=RANDOM_DATA_2)
