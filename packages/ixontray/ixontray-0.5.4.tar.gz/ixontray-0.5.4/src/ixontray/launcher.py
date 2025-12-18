import logging
import sys
from typing import Optional

import keyring
from PyQt6 import QtCore
from PyQt6.QtCore import QSettings, QRect, QRectF, QPoint
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor, QPalette, QKeyEvent
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QWidget,
)
from PyQt6.QtGui import QScreen

from ixontray.ixon_cloud_api import IxonCloudAPIv1
from ixontray.ixon_vpn_client_api import CONNECTION_STATUS, IxonVpnClient
from ixontray.settings_window import ClientsTab
from ixontray.telemetry import log_telemetry
from ixontray.types.api import IXapiApplicationID, Agent
from ixontray.types.common import AgentList, Command, Commands

PPI_SIZE_MARGIN = 10


class CommandItem(QListWidgetItem):
    def __init__(self, command: Command) -> None:
        super().__init__(QIcon.fromTheme(command.icon), command.name)
        self._command = command

    def get_command(self) -> Command:
        return self._command

    def set_command(self, command: Command) -> None:
        self._command = command


class CommandOptions(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QGridLayout()
        self._commands = Commands()
        self.options = QListWidget()
        self._layout.addWidget(self.options)
        self.setLayout(self._layout)

    def set_commands(self, commands: Commands) -> None:
        self._commands = commands
        for idx, cmd in enumerate([c for c in self._commands.commands[::-1] if "item" in c.show_in]):
            cmd.name = f"{idx}. {cmd.name}"
            self.options.addItem(CommandItem(cmd))
        self.options.addItem(QListWidgetItem("No action"))
        self.options.setCurrentRow(0)

    def get_current_command(self) -> Command | None:
        """Return the current selected command."""
        command_item = self.options.currentItem()
        if isinstance(command_item, CommandItem):
            return command_item.get_command()
        return None

    @log_telemetry
    def execute(self) -> None:
        command_item = self.options.currentItem()
        if isinstance(command_item, CommandItem):
            command = command_item.get_command()
            logging.info(f"Running {command.name}")
            command.execute()


class Launcher(QWidget):
    def __init__(self, settings: QSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("launcher")
        self.setWindowTitle("Ixontray Launcher")
        # Set window to be transparent for rounded corners
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # Get the device pixel ratio for DPI scaling
        device_pixel_ratio: float = self.screen().devicePixelRatio()

        # Calculate scaled values based on DPI scaling
        base_font_size: int = 30
        scaled_font_size: int = int(base_font_size / device_pixel_ratio)

        # Scale UI element sizes
        base_border_radius: int = 15
        scaled_border_radius: int = int(base_border_radius / device_pixel_ratio)

        base_padding: int = 30
        scaled_padding: int = int(base_padding / device_pixel_ratio)

        base_margin: int = 10
        scaled_margin: int = int(base_margin / device_pixel_ratio)

        # Set the stylesheet with DPI-adjusted sizes
        self.setStyleSheet(f"""
        font-size: {scaled_font_size}pt;
        QWidget#launcher {{
            background-color: palette(window);
            border-radius: {scaled_border_radius}px;
            border: none;
        }}
        QLineEdit {{ 
            background: #333; 
            border: none; 
            color: #FFF;
            padding: {scaled_padding}px; 
            margin: {scaled_margin}px; 
        }}
        QListWidget {{ 
            font-size: {scaled_font_size}pt; 
            margin: {scaled_margin}px;
            border: none;
        }}
        """)

        self._agents = AgentList(agents_by_id={})
        self._settings = settings
        self._layout = QHBoxLayout(self)
        self.setLayout(self._layout)

        # Search box
        self.clients_tab = ClientsTab()
        self.clients_tab.lw_all_clients.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.clients_tab.lw_all_clients.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.clients_tab.lw_selected_clients.hide()
        self.clients_tab.btn_move_left.hide()
        self.clients_tab.btn_move_right.hide()
        self.clients_tab.lbl_fav_clients.hide()
        self.clients_tab.lbl_all_clients.hide()
        self._layout.addWidget(self.clients_tab)

        # Add commands options
        self.command_options = CommandOptions(parent=self)
        self._layout.addWidget(self.command_options)

        # self.clients_tab.lw_all_clients.setMinimumWidth(1000)
        # set window hint to make the window frameless and stay on top
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
        )
        # Set focus on search bar
        self.clients_tab.le_search_clients.setFocus()
        # Set the tab order so tab directly goes to the command selection
        self.setTabOrder(self.clients_tab.le_search_clients, self.command_options.options)

    def paintEvent(self, event: QtCore.QEvent) -> None:  # noqa
        """Override paintEvent to draw rounded corners for the window.
        Takes into account the device pixel ratio (DPI scaling).
        """
        painter: QPainter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get the device pixel ratio for DPI scaling
        device_pixel_ratio: float = self.screen().devicePixelRatio()

        # Calculate the scaled border radius
        base_border_radius: int = 15
        scaled_border_radius: int = int(base_border_radius / device_pixel_ratio)

        # Create a path for the rounded rectangle
        path: QPainterPath = QPainterPath()
        rect: QRectF = QRectF(0, 0, self.width(), self.height())
        path.addRoundedRect(rect, scaled_border_radius, scaled_border_radius)

        # Fill the path with system background color
        background_color: QColor = self.palette().color(QPalette.ColorRole.Window)
        painter.fillPath(path, background_color)

        # Call the parent class's paintEvent to handle any other painting
        super().paintEvent(event)

    def set_commands(self, commands: Commands) -> None:
        self.command_options.set_commands(commands)
        width: int = self.command_options.options.sizeHintForColumn(0)
        self.command_options.options.setMinimumWidth(int(width * 1.1))

    def set_agents(self, agents: AgentList) -> None:
        self._agents = agents
        self.clients_tab.set_all_clients(clients=agents.agents_by_id, favourites={})
        width: int = self.clients_tab.lw_all_clients.sizeHintForColumn(0)
        self.clients_tab.lw_all_clients.setMinimumWidth(int(width * 1.1))
        # Select the current agent
        agent_id: Optional[str] = self.get_current_agent_id()
        if agent_id:
            self.clients_tab.set_selected_client(agent_id=agent_id)

    def center(self, screen: QScreen = None) -> None:
        """Center the window on the screen and ensure it fits within the screen boundaries.
        Takes into account the device pixel ratio (DPI scaling).

        Args:
            screen: The screen to center the window on. If None, uses the current screen.
        """
        # Get the screen and its properties
        if screen is None:
            screen = self.screen()
        screen_geometry: QRect = screen.availableGeometry()
        device_pixel_ratio: float = screen.devicePixelRatio()

        # Get the window geometry
        window_geometry: QRect = self.frameGeometry()

        # Adjust window size based on DPI scaling
        # For high DPI screens, we need to make the window larger
        if device_pixel_ratio > 1.0:
            # Scale the window size based on the device pixel ratio
            dpi_adjusted_width: int = int(window_geometry.width() * device_pixel_ratio)
            dpi_adjusted_height: int = int(window_geometry.height() * device_pixel_ratio)

            # Only resize if the window is not already adjusted for DPI
            if (
                abs(window_geometry.width() - dpi_adjusted_width) > PPI_SIZE_MARGIN
            ):  # Threshold to avoid minor adjustments
                self.resize(dpi_adjusted_width, dpi_adjusted_height)
                window_geometry = self.frameGeometry()  # Update geometry after resize

        # Check if the window is larger than the screen
        if window_geometry.width() > screen_geometry.width() or window_geometry.height() > screen_geometry.height():
            # Calculate the scaling factor
            width_ratio: float = screen_geometry.width() / window_geometry.width()
            height_ratio: float = screen_geometry.height() / window_geometry.height()
            scale_factor: float = min(width_ratio, height_ratio) * 0.9  # Use 90% of the available space

            # Resize the window
            new_width: int = int(window_geometry.width() * scale_factor)
            new_height: int = int(window_geometry.height() * scale_factor)
            self.resize(new_width, new_height)

            # Update the window geometry after resizing
            window_geometry = self.frameGeometry()

        # Center the window on the screen
        cp: QPoint = screen_geometry.center()
        window_geometry.moveCenter(cp)
        self.move(window_geometry.topLeft())

    def get_current_agent_id(self) -> str | None:
        """Get the agent id for the current connected client.

        Returns the id or None if not connected
        """
        ixon_vpn_client: IxonVpnClient = IxonVpnClient(token="")
        return ixon_vpn_client.status().get("agentId", "")

    def keyPressEvent(self, qKeyEvent: QKeyEvent) -> None:  # noqa
        if qKeyEvent.key() == QtCore.Qt.Key.Key_Return:
            item: QListWidgetItem = self.clients_tab.lw_all_clients.currentItem()
            if item.isHidden():
                self.close()
                return
            agent: str = item.text()
            agent_id: str = self.clients_tab.inverted_mapping[agent]
            logging.info(f"Selected agent: {agent} with id {agent_id}")
            self.setEnabled(False)
            self.close()
            cmd: Optional[Command] = self.command_options.get_current_command()
            if cmd and cmd.force_connection:
                self.connect_to_host(agent_id=agent_id)
            self.command_options.execute()

        if qKeyEvent.key() in [QtCore.Qt.Key.Key_Down, QtCore.Qt.Key.Key_Up]:
            self.clients_tab.lw_all_clients.keyPressEvent(qKeyEvent)

        if qKeyEvent.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(qKeyEvent)

    def connect_to_host(self, agent_id: str) -> None:
        """Connect to the specified agent."""
        username: str = self._settings.value("email", "")
        password: Optional[str] = keyring.get_password("Ixontray", username)
        auth_string: str = IxonCloudAPIv1.generate_auth(email=username, pwd=password)
        token: str = IxonCloudAPIv1(application_id=IXapiApplicationID).generate_access_token(auth=auth_string)
        ixon_vpn_client: IxonVpnClient = IxonVpnClient(token=token)

        connect: bool = True
        if ixon_vpn_client.connected():
            if agent_id in ixon_vpn_client.status().get("agentId", ""):
                logging.info("Already connected to right client not connecting again.")
                connect = False
            else:
                ixon_vpn_client.disconnect()
                logging.info("Wait for disconnect")
                ixon_vpn_client.wait_for_status(wanted_status=CONNECTION_STATUS.IDLE)

        if connect:
            agent: Agent = self._agents.agents_by_id[agent_id]
            ixon_vpn_client.connect(agent=agent)
            if not ixon_vpn_client.wait_for_status(wanted_status=CONNECTION_STATUS.CONNECTED):
                logging.info("Failed to connect. exiting")
                sys.exit(0)
