import keyring
import pytest
from PyQt6.QtCore import QSettings

from ixontray.ixon_cloud_api import IxonCloudAPIv2
from ixontray.types.api import IXapiApplicationID


@pytest.fixture()
def token() -> str:
    ixon_cloud = IxonCloudAPIv2(application_id=IXapiApplicationID)
    settings = QSettings("martrobotics", "ixontray")
    username = settings.value("email", "")
    password = keyring.get_password("Ixontray", username)
    auth_string = ixon_cloud.generate_auth(email=username, pwd=password)
    return ixon_cloud.generate_access_token(auth=auth_string)
