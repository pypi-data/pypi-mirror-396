import json
import logging
import time
import uuid
from enum import Enum
from http import HTTPStatus

import requests

from ixontray.types.api import Agent

logger = logging.getLogger("IXON_VPN_CLIENT")


class CONNECTION_STATUS(str, Enum):
    CONNECTING = "connecting"
    IDLE = "idle"
    CONNECTED = "connected"


class IxonVpnClient:
    TIMEOUT = 1
    BASE_URL = "https://localhost:9250"

    def __init__(self, token: str) -> None:
        self._auth = token

    def connect(self, agent: Agent) -> bool:
        data = {"companyId": agent.company_id, "agentId": agent.publicId}

        headers = {
            "Content-Type": "application/json",
            "IXplatform-Access-Token": self._auth,
            "IXclient-Controller-Identifier": str(uuid.uuid4()),
        }

        if agent.api_version == 1:
            headers |= {
                "IXapi-version": "1",
            }
        else:
            headers |= {
                "Api-Version": "2",
            }

        success, resp = self.post_request(endpoint="connect", data=data, headers=headers)
        return success

    def status(self) -> dict[str, str]:
        url = f"{self.BASE_URL}/status"
        r = requests.get(url=url, verify=False)
        if r.status_code == HTTPStatus.OK:
            json_string = "".join(c for c in r.text if c != "\\")
            json_string = json.loads(json_string)

            agent_id = ""
            if "activeRequest" in json_string:
                if "agentId" in json_string["activeRequest"]:
                    agent_id = json_string["activeRequest"]["agentId"]

            return {"status": "success", "data": json_string["status"], "agentId": agent_id}

        msg = (
            "It looks like your local IXON client is not running"
            " please make sure your local client runs and try again"
            " or download it from the IXON website"
        )
        logger.error(msg)

        return {"status": "error", "data": str(r)}

    def connected(self) -> bool:
        try:
            status = self.status()
            return status.get("data", "") == CONNECTION_STATUS.CONNECTED
        except requests.exceptions.ConnectionError:
            return False

    def wait_for_status(self, wanted_status: CONNECTION_STATUS, timeout: int = 30) -> bool:
        """Blocks until status has the correct value."""
        start_time = time.time()
        status = self.status()
        logger.info(f"Waiting for connection status {wanted_status}")
        while not status.get("data", "") == wanted_status:
            status = self.status()
            if start_time + timeout < time.time():
                logger.error(f"Timeout while waiting for connection status: {wanted_status}")
                return False
            time.sleep(0.1)

        logger.info(f"Waiting for connection status {wanted_status} DONE")

        return True

    def disconnect(self) -> bool:
        resp, _ = self.post_request("disconnect", headers={})
        return resp

    def post_request(
        self,
        endpoint: str,
        data: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> (bool, dict):
        if data is None:
            data = {}

        url = f"{self.BASE_URL}/{endpoint}"
        if headers is None:
            headers = {}
        r = requests.post(url=url, verify=False, headers=headers, data=json.dumps(data), timeout=self.TIMEOUT)
        if r.status_code == HTTPStatus.OK:
            return True, r
        logging.error(r.text)
        return False, r
