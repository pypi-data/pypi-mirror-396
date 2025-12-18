import base64
import json
from http import HTTPStatus

import requests

from ixontray.types.api import (
    Agent,
    AgentsResponse,
    CompaniesResponse,
    Server,
    WebAccessResponse,
)


class IxonCloudAPI:
    VERSION = None
    BASE_URL = ""

    def __init__(self, application_id: str, token: str | None = None) -> None:
        self._application_id = application_id
        self._bearer = token

    @staticmethod
    def generate_auth(email: str, pwd: str, otp: str | None = None) -> str:
        """Generates the user specific authentication key for the ixon client.

        :return: the base64 typed string of the user credentials
        """
        if otp is None:
            otp = ""
        combined = f"{email}:{otp}:{pwd}"
        return base64.urlsafe_b64encode(combined.encode("UTF-8")).decode("ascii")

    def generate_access_token(self, auth: str) -> str | None:
        url = "https://api.ayayot.com/access-tokens?fields=secretId"

        headers = {
            "Api-Version": "2",
            "Api-Application": self._application_id,
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth}",
        }

        # 60 days expiration time
        data = {"expiresIn": 5_184_000}

        response = requests.request("POST", url, headers=headers, data=json.dumps(data))

        if response.status_code == HTTPStatus.CREATED:
            data = json.loads(response.text)["data"]
            self._bearer = data["secretId"]
            return self._bearer

        return None

    def has_valid_token(self) -> bool:
        """Check if we have a valied token."""
        return self._bearer is not None

    def send_request(  # noqa
        self,
        url: str | None = None,
        endpoint: str | None = None,
        data: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        headers: dict | None = None,
        method: str = "GET",
    ) -> dict:
        if self._bearer is None:
            raise RuntimeError("Request token token first")

        if data is None:
            data = {}

        if params is None:
            params = {}

        if url is None:
            url = self.BASE_URL + endpoint

        if headers is None:
            headers = {}

        headers |= {
            "Authorization": "Bearer " + self._bearer + "",
            "Content-Type": "application/json",
        }

        if self.VERSION == 1:
            headers |= {
                "IXapi-version": "1",
                "IXapi-Application": self._application_id,
            }
        else:
            headers |= {
                "Api-Version": "2",
                "Api-Application": self._application_id,
            }

        response = requests.request(method=method, url=url, headers=headers, params=params, data=data)
        return json.loads(response.text)

    def get_agents(self, company_id: str) -> AgentsResponse:
        result = self.send_request(
            endpoint="agents?page-size=200",
            params={
                "fields": (
                    "servers.*,name,publicId,description,activeVpnSession.vpnAddress,networkReportedOn,company_id"
                ),
            },
            headers={"Api-Company": company_id},
        )
        if result is not None:
            agents_reponse = AgentsResponse.model_validate(result)
            for a in agents_reponse.data:
                a.company_id = company_id
            return agents_reponse
        return None

    def get_companies(self) -> CompaniesResponse:
        result = self.send_request(
            endpoint="companies",
            data={"fields": "city,country,links,name,parentLevel,publicId,starred"},
        )
        if result is not None:
            return CompaniesResponse.model_validate(result)
        return None


class IxonCloudAPIv1(IxonCloudAPI):
    VERSION = 1
    BASE_URL = "https://api.ixon.net/"

    def get_webaccess_url_from_server(self, agent: Agent, server: Server) -> str:
        full_url = "webaccess"

        if server.type == "vnc":
            return f"https://portal.ixon.cloud/portal/devices/{agent.publicId}/web-access/vnc/{server.publicId}"

        data = {"method": "http", "server": {"publicId": server.publicId}}
        headers = {"IXapi-Company": agent.company_id}

        result = self.send_request(method="POST", data=json.dumps(data), endpoint=full_url, headers=headers)

        if result is not None:
            return WebAccessResponse.model_validate(result).data.url

        return ""


class IxonCloudAPIv2(IxonCloudAPI):
    VERSION = 2
    BASE_URL = "https://api.ayayot.com:443/"

    def get_webaccess_url_from_server(self, agent: Agent, server: Server) -> str:
        full_url = "https://portal.ixon.cloud:443/api/web-access"

        # This only works if you are connected to the right comapany in ixon
        if server.type == "vnc":
            return f"https://portal.ixon.cloud/portal/devices/{agent.publicId}/web-access/vnc/{server.publicId}"

        data = {"server": {"publicId": server.publicId}}
        result = self.send_request(
            method="POST",
            data=json.dumps(data),
            url=full_url,
            headers={"Api-Company": agent.company_id},
        )

        if result is not None:
            return WebAccessResponse.model_validate(result).data.url

        return ""
