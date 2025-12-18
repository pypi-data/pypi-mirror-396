# ------------------------------------------------------------------
# Copyright (C) Smart Robotics - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly
# prohibited. All information contained herein is, and remains
# the property of Smart Robotics.
# ------------------------------------------------------------------
import threading
from pathlib import Path

import pytest
from pydantic import BaseModel

from ixontray.base_model_store import BaseModelStore
from ixontray.types.common import INSTALL_DIR, Commands

COMMAND_FILE_NAME = Path("commands.yaml")
COMMAND_FILE_PATH = INSTALL_DIR / COMMAND_FILE_NAME
BIG_NUMBER = 100


@pytest.fixture
def commands_file() -> Path:
    return INSTALL_DIR / COMMAND_FILE_NAME


def test_load_happy_flow(commands_file: Path) -> None:
    commands_store = BaseModelStore[Commands](file_path=commands_file)
    assert isinstance(commands_store.data, Commands)


def test_load_no_file(tmp_path: Path, commands_file: Path) -> None:
    tmp_file = tmp_path / "load.yaml"
    commands_store = BaseModelStore[Commands](file_path=tmp_file, default_path=commands_file)
    commands = commands_store.load()
    assert isinstance(commands, Commands)


def test_load_no_file_no_default(tmp_path: Path) -> None:
    tmp_file = tmp_path / "load.yaml"
    commands_store = BaseModelStore[Commands](file_path=tmp_file)
    with pytest.raises(RuntimeError):
        commands_store.load()


def test_load_no_file_no_default_not_allow_empty(tmp_path: Path) -> None:
    tmp_file = tmp_path / "load.yaml"
    commands_store = BaseModelStore[Commands](file_path=tmp_file, empty_if_not_valid=True)
    commands = commands_store.load()
    print(commands)
    assert isinstance(commands, Commands)


def test_save(tmp_path: Path, commands_file: Path) -> None:
    tmp_file = tmp_path / "load.yaml"
    commands_store1 = BaseModelStore[Commands](file_path=commands_file)
    commands1 = commands_store1.load()

    commands_store2 = BaseModelStore[Commands](file_path=tmp_file)
    commands_store2.save(data=commands1)
    commands2 = commands_store2.load()

    assert commands1 == commands2


def test_base_model_store_thread_safety(tmp_path: Path) -> None:
    """Test the store is thread-save  of the store."""

    class TestModel(BaseModel):
        foo: str
        bar: int

    filepath = tmp_path / "data.yaml"
    filepath.write_text("foo: default\nbar: 0\n")

    store = BaseModelStore[TestModel](file_path=filepath)

    # Define a function that loads and saves the data to the store
    bar = 1

    def load_and_save() -> None:
        nonlocal bar
        for _ in range(10):
            # Load the data from the store
            loaded_data = store.load()

            # Modify the loaded data
            loaded_data.foo = "world"
            loaded_data.bar = bar
            bar += 1

            # Save the modified data back to the store
            store.save(loaded_data)

    # Create a list of threads that will load and save the data concurrently
    threads = [threading.Thread(target=load_and_save) for _ in range(10)]

    # Start the threads
    for t in threads:
        t.start()

    # Wait for the threads to finish
    for t in threads:
        t.join()

    # Load the final data from the store and assert that it has been modified by all threads
    final_data = store.load()
    assert final_data.foo == "world"
    assert final_data.bar == BIG_NUMBER  # noqa: 10 threads x 10 iterations each = 100
