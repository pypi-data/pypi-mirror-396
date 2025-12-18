import os
import pathlib

from PyQt6.QtCore import QSettings, QStandardPaths

ORGANIZATION = "martrobotics"

qsettings = QSettings(ORGANIZATION, "ixontray")

CONFIG_DIR = (
    pathlib.Path(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.ConfigLocation)[0]) / ORGANIZATION
)

CACHE_DIR = CONFIG_DIR / "cache"
AGENTS_FILE_NAME = pathlib.Path("agents.yaml")
AGENTS_FILE_PATH = CACHE_DIR / AGENTS_FILE_NAME
COMMAND_FILE_NAME = pathlib.Path("commands.yaml")
COMMAND_FILE_PATH = CONFIG_DIR / COMMAND_FILE_NAME
INSTALL_DIR = os.path.abspath(os.path.dirname(__file__))
