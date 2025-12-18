# ------------------------------------------------------------------
# Copyright (C) Smart Robotics - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly
# prohibited. All information contained herein is, and remains
# the property of Smart Robotics.
# ------------------------------------------------------------------

from ixontray.ixon_cloud_api import IxonCloudAPIv2
from ixontray.types.api import IXapiApplicationID


def test_get_agents(token: str) -> None:
    ixon_cloud = IxonCloudAPIv2(application_id=IXapiApplicationID, token=token)

    companies = ixon_cloud.get_companies()
    for company in companies.data:
        if "Smart Robotics Test systems" not in company.name:
            continue
        # print("=" * 120)
        print(company.name)
        print("=" * 120)
        agents = ixon_cloud.get_agents(company_id=company.publicId)
        assert agents
        for agent in agents.data:
            print("#" * 120)
            print(f"{agent.name} ")
            print("#" * 120)

            for server in agent.servers:
                print(server.name)
                a = ixon_cloud.get_webaccess_url_from_server(agent=agent, server=server)
                print(a)


def test_get_companies(token: str) -> None:
    ixon_cloud = IxonCloudAPIv2(application_id=IXapiApplicationID, token=token)
    companies = ixon_cloud.get_companies()
    assert companies
    # print(companies)
