# ------------------------------------------------------------------
# Copyright (C) Smart Robotics - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly
# prohibited. All information contained herein is, and remains
# the property of Smart Robotics.
# ------------------------------------------------------------------
import pytest

from ixontray.ixon_vpn_client_api import CONNECTION_STATUS, IxonVpnClient
from ixontray.types.api import Agent


def agent_v1() -> Agent:
    return Agent(name="Captain", publicId="GiUEgrFrKmfi", company_id="3628-4232-8730-0182-3804", api_version=1)


def agent_v2() -> Agent:
    return Agent(name="Coolblue", publicId="4rByxRSYb2B7", company_id="4369-1743-0786-2435-3453", api_version=2)


@pytest.mark.parametrize(
    "agent",
    [
        agent_v1(),
        # agent_v2(),
    ],
)
def test_connect_to_host(token: str, agent: Agent) -> None:
    print(f"Connecting to : {agent}")
    ixon_vpn_client = IxonVpnClient(token=token)
    print(ixon_vpn_client.disconnect())

    print("wait for connect idle")
    print(ixon_vpn_client.status())
    ixon_vpn_client.wait_for_status(wanted_status=CONNECTION_STATUS.IDLE)

    ixon_vpn_client.connect(agent=agent)

    print("wait for connect")
    ixon_vpn_client.wait_for_status(wanted_status=CONNECTION_STATUS.CONNECTED)
    print(ixon_vpn_client.status())


def test_disconnect() -> None:
    ixon_vpn_client = IxonVpnClient(token=None)
    ixon_vpn_client.disconnect()


def test_status() -> None:
    ixon_vpn_client = IxonVpnClient(token=None)
    status = ixon_vpn_client.status()
    print(status)
