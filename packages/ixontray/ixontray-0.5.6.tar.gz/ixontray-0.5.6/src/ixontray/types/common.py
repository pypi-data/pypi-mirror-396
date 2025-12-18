# ------------------------------------------------------------------
# Copyright (C) Smart Robotics - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly
# prohibited. All information contained herein is, and remains
# the property of Smart Robotics.
# ------------------------------------------------------------------
import os
from datetime import datetime
from pathlib import Path

import pydantic
from pydantic import Field

from ixontray.types.api import Agent

INSTALL_DIR = Path(os.path.abspath(os.path.dirname(__file__))).parent


class Command(pydantic.BaseModel):
    name: str
    cmd: str
    icon: str
    shortcut: str | None = None
    show_in: list[str] = Field(default_factory=list)
    force_connection: bool

    def execute(self) -> None:
        """Run this command."""
        # Run command but always detach (&),
        # otherwise it will block the application!
        os.system(f"{self.cmd} &")


class Commands(pydantic.BaseModel):
    commands: list[Command] = Field(default_factory=list)


class AgentList(pydantic.BaseModel):
    saved_at: datetime = Field(default_factory=datetime.now)
    agents_by_id: dict[str, Agent] = Field(default_factory=dict)
