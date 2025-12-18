import json
import logging
import threading
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel
from ruamel.yaml import YAML

T = TypeVar("T", bound=BaseModel)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BASE_MODEL_STORE")
logger.setLevel(logging.INFO)


class BaseModelStore(Generic[T]):
    def __init__(self, file_path: Path, default_path: Path | None = None, empty_if_not_valid: bool = False) -> None:
        super().__init__()
        self._filepath = file_path
        self._default_path = default_path
        self._empty_if_not_valid = empty_if_not_valid
        self._lock = threading.Lock()
        self._data: T | None = None

    @property
    def data(self) -> T:
        if self._data is None:
            self._data = self.load()
        return self._data

    def _valid_file_ensured(self) -> bool:
        """Check if load file exist else copy over a default one."""

        if self._filepath.exists():
            return True

        if self._default_path is None or not self._default_path.exists():
            return False

        # Create containing directory
        self._filepath.parent.mkdir(parents=True, exist_ok=True)

        # copy over file content
        logging.info(f"No load file found copying {self._default_path} to {self._filepath}")
        self._filepath.write_text(self._default_path.read_text())

        return True

    def _determine_model(self) -> type[T]:
        """Determine the model based on the template argument.

        NOTE: Only works after __init__ is called
        """
        return self.__orig_class__.__args__[0]

    def load(self) -> T:
        """Loads command from disk returns an empty."""
        with self._lock:
            logger.debug(f"Loading {self._determine_model()} from: {self._filepath}")

            if not self._valid_file_ensured():
                if self._empty_if_not_valid:
                    self._data = self._determine_model()()
                else:
                    raise RuntimeError(
                        f"{self._filepath} does not exist and supplied default file {self._default_path} is not valid",
                    )
            else:
                raw = self._filepath.read_text()
                parsed = YAML().load(raw)
                self._data = self._determine_model().model_validate(parsed)

            return self._data

    def save(self, data: T) -> None:
        """Save data to disk."""
        with self._lock:
            self._filepath.parent.mkdir(parents=True, exist_ok=True)
            with self._filepath.open("w+") as stream:
                logging.debug(f"Saving to: {self._filepath}")
                model_dict = json.loads(data.model_dump_json())
                yaml = YAML()
                yaml.default_flow_style = False
                yaml.dump(model_dict, stream)
