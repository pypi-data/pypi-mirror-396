import datetime
import http
import logging
import time
import traceback
from collections.abc import Callable
from typing import Any
from uuid import uuid4

import pydantic
import requests

import ixontray
from ixontray.base_model_store import BaseModelStore
from ixontray.config import CACHE_DIR, qsettings

DEFAULT_DURATION = 0.0

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("TELEMETRY")
logger.setLevel(logging.DEBUG)

TELEMETRY_CACHE_DIR = CACHE_DIR / "telemetry"


instance_id = qsettings.value("instance_id", None)
if instance_id is None:
    instance_id = str(uuid4())
    qsettings.setValue("instance_id", instance_id)


class FunctionCall(pydantic.BaseModel):
    name: str
    call_count: int = 1
    duration: float = 0.0
    max_duration: float = DEFAULT_DURATION
    min_duration: float = DEFAULT_DURATION

    @pydantic.model_validator(mode="after")
    def validate_min_duration(self) -> "FunctionCall":
        """Set the min max duration to duration if not set."""
        if self.min_duration == DEFAULT_DURATION:
            self.min_duration = self.duration
        if self.max_duration == DEFAULT_DURATION:
            self.max_duration = self.duration
        return self

    def __add__(self, other: "FunctionCall") -> "FunctionCall":
        """Add the call count of the one to the other."""
        self.max_duration = max(self.max_duration, other.duration)
        self.min_duration = min(self.min_duration, other.duration)
        self.duration = (self.duration * self.call_count + other.duration) / (self.call_count + other.call_count)
        self.call_count += other.call_count
        return self


class Report(pydantic.BaseModel):
    application: str
    instance_id: str
    run_id: str = pydantic.Field(default_factory=lambda: str(uuid4()))
    last_update: datetime.datetime
    call_count: dict[str, FunctionCall] = pydantic.Field(default_factory=dict)
    crash_report: str = ""
    version: str = ixontray.__version__


def log_telemetry(func: Callable) -> Callable:
    def logged_function(*args: Any, **kwargs: Any) -> Callable:
        start_time = time.time()
        res = func(*args, **kwargs)
        duration = time.time() - start_time
        telemetry.log(function_call=FunctionCall(name=func.__name__, duration=duration))
        return res

    return logged_function


class Telemetry:
    def __init__(self, url: str, instance_id: str, token: str) -> None:
        self._timeout = 1
        self._url = url
        self._token = token
        self._instance_id = instance_id
        self._report = Report(application="ixontray", instance_id=instance_id, last_update=datetime.datetime.now())

    def log(self, function_call: FunctionCall) -> None:
        """Log function call."""
        self._report.last_update = datetime.datetime.now()
        if function_call.name not in self._report.call_count:
            self._report.call_count[function_call.name] = function_call
        else:
            self._report.call_count[function_call.name] += function_call

    def log_crash_report(self) -> None:
        """Add crash report."""
        self._report.crash_report = str(traceback.format_exc())

    def send(self) -> bool:
        """Send data to remote."""
        logging.debug(f"Sending update to: {self._url}")

        try:
            res = requests.post(
                url=f"{self._url}/{self._instance_id}",
                verify=False,
                data=self._report.model_dump_json(),
                timeout=self._timeout,
            )

            if res.status_code == http.HTTPStatus.OK:
                return True
            # If sending fails store a report to disk
            BaseModelStore[Report](TELEMETRY_CACHE_DIR / ("telemetry_report_" + self._report.run_id + ".yaml")).save(
                data=self._report,
            )
            return False

        except Exception:
            # If sending fails
            return False

    def print(self, report_num: int | None = None) -> None:
        """Print report to console."""
        reports = list(TELEMETRY_CACHE_DIR.glob("*.yaml"))
        print("#" * 100)
        print("All reports. * == holds crash info" if report_num is None else f"Report {reports[report_num]}:")
        print("#" * 100)

        for idx, report in enumerate(reports):
            if report_num is None:
                print(f"{idx}:{report}", end="")
                try:
                    r = BaseModelStore[Report](report).load()
                    if r.crash_report:
                        print("*")
                    else:
                        print("")
                except Exception:
                    print("")

            elif idx == report_num:
                r = BaseModelStore[Report](report).load()
                print(r.model_dump_json(indent=True))
                print("#" * 100)
                print(r.crash_report)
                print("#" * 100)


# telemetry = Telemetry(url="https://telemetry.mmoerdijk.nl", instance_id="mart_app", token="test_token")
telemetry = Telemetry(
    url="https://telemetry.mmoerdijk.nl",
    instance_id=str(instance_id),
    token="ea0dc150-1d13-4d8d-b139-62a5bfde2839",
)
