# ------------------------------------------------------------------
# Copyright (C) Smart Robotics - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly
# prohibited. All information contained herein is, and remains
# the property of Smart Robotics.
# ------------------------------------------------------------------
from packaging import version
from pypi_json import PyPIJSON

import ixontray


def update_available() -> tuple[bool, str]:
    try:
        with PyPIJSON() as client:
            requests_metadata = client.get_metadata("ixontray")
            latest_version = requests_metadata[0]["version"]
            return version.parse(latest_version) > version.parse(ixontray.__version__), latest_version
    except Exception:
        pass
    return False, ""


if __name__ == "__main__":
    print(update_available())
