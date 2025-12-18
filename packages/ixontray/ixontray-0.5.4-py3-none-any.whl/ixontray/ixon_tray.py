#!/usr/bin/env python3
import argparse
import functools
import logging
import os
import signal
import sys
import time
from argparse import RawTextHelpFormatter
from typing import Any

import requests
import urllib3
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QEvent, QObject, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QInputDialog,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
    QWidget,
)

import ixontray
from ixontray.base_model_store import BaseModelStore
from ixontray.config import (
    AGENTS_FILE_PATH,
    COMMAND_FILE_NAME,
    COMMAND_FILE_PATH,
    INSTALL_DIR,
    qsettings,
)
from ixontray.ixon_cloud_api import IxonCloudAPIv1, IxonCloudAPIv2
from ixontray.ixon_vpn_client_api import CONNECTION_STATUS, IxonVpnClient
from ixontray.launcher import Launcher
from ixontray.settings_window import SettingsWindow
from ixontray.telemetry import log_telemetry, telemetry
from ixontray.types.api import Agent, IXapiApplicationID, Server
from ixontray.types.common import AgentList, Command, Commands
from ixontray.update import update_available

urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IXON_TRAY")
logger.setLevel(logging.DEBUG)


class StatusWorker(QObject):
    """Worker class for fetching VPN client status in a background thread.

    This class continuously polls the IXON VPN client for status updates
    and emits signals when the status changes or when errors occur.
    """

    # Signal emitted when status is updated with the new status dictionary
    status_updated = pyqtSignal(dict)
    # Signal emitted when an error occurs with the error message
    error_occurred = pyqtSignal(str)

    def __init__(self, vpn_client: IxonVpnClient | None) -> None:
        """Initialize the StatusWorker.

        Args:
            vpn_client: The IXON VPN client instance to monitor
        """
        super().__init__()
        self._vpn_client = vpn_client
        self._running = True

    def run(self) -> None:
        """Continuously fetch status until stopped.

        This method runs in a loop, fetching the VPN client status
        and emitting signals when the status changes or when errors occur.
        It sleeps for 1 second between updates to avoid excessive CPU usage.
        """
        while self._running:
            try:
                if self._vpn_client:
                    status = self._vpn_client.status()
                    self.status_updated.emit(status)

                    # Check for errors in the status
                    if status.get("status") == "error":
                        msg = (
                            "It looks like your local IXON client is not running"
                            " please make sure your local client runs and try again"
                            " or download it from the IXON website"
                        )
                        self.error_occurred.emit(msg)
            except requests.exceptions.ConnectionError:
                msg = (
                    "Ixon client could not connect to the ixon vpn client. Please visit: "
                    "https://support.ixon.cloud/hc/en-us/articles/"
                    "360014815979-VPN-client-installation-and-uninstallation "
                    "for instructions on how to install the vpn client and restart the application."
                )
                self.error_occurred.emit(msg)

            # Sleep for a short time before next update
            time.sleep(1)

    def stop(self) -> None:
        """Stop the worker.

        Sets the running flag to False, which will cause the run method to exit
        after the current iteration completes.
        """
        self._running = False


class AgentsWorker(QObject):
    """Worker class for fetching agents in a background thread.

    This class fetches agents from both IXON Cloud API v1 and v2,
    and emits signals when the agents are updated or when errors occur.
    """

    # Signal emitted when agents are updated with the new agents dictionary
    agents_updated = pyqtSignal(dict)
    # Signal emitted when an error occurs with the error message
    error_occurred = pyqtSignal(str)

    def __init__(self, ixon_api_v1: IxonCloudAPIv1 | None, ixon_api_v2: IxonCloudAPIv2 | None) -> None:
        """Initialize the AgentsWorker.

        Args:
            ixon_api_v1: The IXON Cloud API v1 instance
            ixon_api_v2: The IXON Cloud API v2 instance
        """
        super().__init__()
        self._ixon_api_v1 = ixon_api_v1
        self._ixon_api_v2 = ixon_api_v2
        self._running = True

    def run(self) -> None:
        """Fetch agents once and emit the result.

        This method fetches agents from both IXON Cloud API v1 and v2,
        combines the results, and emits a signal with the updated agents.
        If an error occurs, it emits an error signal with the error message.
        """
        try:
            ixon_ids = {}
            # API v1
            res1 = self._ixon_api_v1.get_companies()
            if res1 is None:
                self.error_occurred.emit("Failed to connect, please check your login details")
                return

            logger.info("Loaded agent list from cloud v1.")
            companies = [(c, self._ixon_api_v1) for c in res1.data]

            res2 = self._ixon_api_v2.get_companies()
            if res2 is None:
                self.error_occurred.emit("Failed to connect, please check your login details")
                return

            logger.info("Loaded agent list from cloud v2.")
            companies += [(c, self._ixon_api_v2) for c in res2.data]

            if companies is None:
                self.error_occurred.emit("Failed to connect, please check your login details")
                return

            for company, api in companies:
                logger.info(f"Loading agents for {company.name} / {company.publicId}")
                agents = None
                agents = api.get_agents(company_id=company.publicId)
                if agents is None:
                    continue
                for a in agents.data:
                    a.company_id = company.publicId
                    a.api_version = api.VERSION
                    ixon_ids[a.publicId] = a

            self.agents_updated.emit(ixon_ids)

        except Exception as e:
            logger.error(f"Error fetching agents: {e}")
            self.error_occurred.emit(f"Error fetching agents: {e}")

    def stop(self) -> None:
        """Stop the worker.

        Sets the running flag to False, which will cause the run method to exit
        if it's in a loop (though in this implementation, run() exits after one execution).
        """
        self._running = False


class IxonTray:
    CONNECT_TIMEOUT = 60

    def __del__(self) -> None:
        """Clean up resources when the object is destroyed."""
        self.cleanup()

    def cleanup(self) -> None:
        """Stop background threads and clean up resources."""
        # Stop the workers
        if hasattr(self, "_status_worker"):
            self._status_worker.stop()
        if hasattr(self, "_agents_worker"):
            self._agents_worker.stop()

        # Quit and wait for the threads to finish
        if hasattr(self, "_status_thread"):
            self._status_thread.quit()
            self._status_thread.wait()
        if hasattr(self, "_agents_thread"):
            self._agents_thread.quit()
            self._agents_thread.wait()

    def _get_status_from_ixon_vpn_client(self) -> None:
        """Fetch status from the IXON VPN client and update the UI.

        This method is kept for compatibility but is no longer used directly.
        Status updates are now handled by the StatusWorker class.

        It fetches the current status from the IXON VPN client and updates
        the _ixon_status variable. If there's an error, it shows a message
        in the system tray or a dialog box.
        """
        if self._ixon_vpn_client:
            try:
                self._ixon_status = self._ixon_vpn_client.status()
                if self._ixon_status["status"] == "error":
                    msg = (
                        "It looks like your local IXON client is not running"
                        " please make sure your local client runs and try again"
                        " or download it from the IXON website"
                    )
                    self.tray.showMessage(
                        "IXON tray",
                        msg,
                    )
            except requests.exceptions.ConnectionError:
                msg = QMessageBox()
                msg.setText(
                    (
                        "Ixon client could not connect to the ixon vpn client. Please visit: <a"
                        ' href="https://support.ixon.cloud/hc/en-us/articles/360014815979-VPN-client-installation-and-uninstallation">Installation'
                        " instructions</a>for instructions on how to install the vpn client and restart the"
                        " application."
                    ),
                )
                msg.setWindowTitle("Ixon vpn client missing")

                msg.exec()

    # The get_agents method has been removed as it's now handled by the AgentsWorker class

    @log_telemetry
    def run_command(self, *_: Any, command: Command, ixon_id: str | None = None) -> None:
        """Run a command, optionally connecting to an IXON agent first.

        Args:
            command: The command to execute
            ixon_id: The ID of the IXON agent to connect to before executing the command.
                     If None and the command requires a connection, the currently connected
                     agent will be used.

        This method executes the given command. If the command requires a connection
        (command.force_connection is True), it will first connect to the specified IXON agent.
        If no agent is specified and a connection is required, it will use the currently
        connected agent or show a warning if not connected.
        """
        logger.info(f"Running: {command}")

        if command.force_connection:
            logger.info("This command requires a connection connecting")
            if ixon_id is None and not self._ixon_vpn_client.connected():
                logger.warning("Not connected, please connect first")
                return

            if ixon_id is None:
                ixon_id = self._ixon_status["agentId"]

            self.connect_to_ixon(ixon_id=ixon_id)
            logger.info("Connected")

        logger.info("Running actual command")
        print(ixon_id)
        if ixon_id is not None:
            command.cmd = command.cmd.replace("{ixon_id}", ixon_id)
            print(command.cmd)
        command.execute()

    @log_telemetry
    def connect_to_ixon(self, ixon_id: str) -> None:
        """Connect to an IXON agent.

        Args:
            ixon_id: The ID of the IXON agent to connect to

        This method connects to the specified IXON agent. If already connected
        to a different agent, it will first disconnect from that agent.
        It shows status messages in the system tray and logs the connection process.
        If the connection fails after multiple attempts, it shows an error message.
        """
        # Connect to IXON

        self._ixon_status = self._ixon_vpn_client.status()
        disconnected = False
        logger.info(f"Current status: {self._ixon_status}")

        # If we are here and still connected we are connected to the right system
        if self._ixon_vpn_client.connected() and ixon_id in self._ixon_status.get("agentId", ""):
            logger.info("Already connected")
            return

        if self._ixon_vpn_client.connected():
            self.tray.showMessage("IXON tray", "Disconnecting from previous host.")
            logger.info(f"Disconnecting from previous host: {self._ixon_status}")
            self._ixon_vpn_client.disconnect()
            disconnected = True
            logger.info("Wait for disconnect")
            self._ixon_vpn_client.wait_for_status(wanted_status=CONNECTION_STATUS.IDLE)
            logger.info("Disconnected")

        msg = f"Connecting to {self._agents_list.agents_by_id[ixon_id]}"
        self.tray.showMessage("IXON tray", msg)
        logger.info(msg)

        if self._ixon_status["data"] == "idle" or disconnected:
            max_tries = 3
            for i in range(max_tries):
                if self._ixon_vpn_client.connect(agent=self._agents_list.agents_by_id[ixon_id]):
                    break
                logger.info(f"You have {max_tries - i - 1} tries left.")

        self._ixon_status = self._ixon_vpn_client.status()

        if not self._ixon_vpn_client.wait_for_status(
            wanted_status=CONNECTION_STATUS.CONNECTED,
            timeout=self.CONNECT_TIMEOUT,
        ):
            msg = "Failed to connect, please check your login details"
            self.tray.showMessage("IXON tray", msg)
            logger.info(msg)
        else:
            msg = "Connected"
            logger.info(msg)
            self.tray.showMessage("IXON tray", msg)
            self.setup_menu()

    @log_telemetry
    def save_commands_cb(self, commands: Commands) -> None:
        """Save the updated commands and refresh the menu.

        Args:
            commands: The updated commands to save

        This method is called when the commands are updated in the settings window.
        It saves the commands to the command store, reloads them, and refreshes the menu.
        """
        self._command_store.save(commands)
        self._commands = self._command_store.load()
        self.setup_menu()

    def _has_login_details(self) -> bool:
        """Check if login details are available.

        Returns:
            bool: True if both email and password are set, False otherwise

        This method checks if the user has provided login credentials
        (email and password) in the settings window.
        """
        return all(self._settings_window.general_tab.get_auth())

    def get_auth_string(self, otp: str | None = None) -> str:
        """Get the authentication string for the IXON API.

        Args:
            otp: One-time password for two-factor authentication.
                If None and 2FA is enabled, a dialog will prompt for the OTP.

        Returns:
            str: The authentication string to use with the IXON API,
                 or an empty string if login details are missing

        This method retrieves the email and password from the settings window,
        prompts for an OTP if needed, and generates an authentication string
        for the IXON API. If login details are missing, it shows the login
        credentials dialog and returns an empty string.
        """
        email, password = self._settings_window.general_tab.get_auth()

        if otp is None and self._settings_window.general_tab.ch_2fa.isChecked():
            otp, ok = QInputDialog.getText(self._settings_window, "OTP required", "Enter OTP")
            if not ok:
                otp = ""

        if not email or not password:
            logger.error("No login details found please supply them")
            self.show_login_credentials()
            return ""

        return IxonCloudAPIv1.generate_auth(email=email, pwd=password, otp=otp)

    def show_login_credentials(self) -> None:
        """Show the login credentials dialog.

        This method displays the settings window and sets the current tab
        to the general tab (index 0), which contains the login credentials fields.
        It's called when login credentials are missing or invalid.
        """
        self._settings_window.show()
        self._settings_window.setCurrentIndex(0)

    def _setup_ixon_apis(self) -> None:
        """Set up the IXON APIs with authentication.

        This method initializes the IXON Cloud API v1 and v2, and the IXON VPN client.
        It gets an authentication string, generates an access token, and uses it to
        initialize the APIs and VPN client. If authentication fails or there's a
        connection error, it shows appropriate error messages and retries if needed.
        """
        logger.info("Setting up apis")
        auth_string = self.get_auth_string()
        if auth_string is None:
            logger.info("No auth string")
            return
        self._ixon_api_v1 = IxonCloudAPIv1(application_id=IXapiApplicationID)
        try:
            token = self._ixon_api_v1.generate_access_token(auth=auth_string)
            print(token)
            if token is not None:
                self._ixon_vpn_client = IxonVpnClient(token=token)
                self._ixon_api_v2 = IxonCloudAPIv2(application_id=IXapiApplicationID, token=token)
                self._no_internet = False
            else:
                self.show_login_credentials()
        except requests.exceptions.ConnectionError:
            logger.error("Could not get a connection, please check your internet connection. Retry in 2 sec")
            time.sleep(2)
            self._setup_ixon_apis()

    def __init__(self) -> None:
        self.update = None
        self.menu = QMenu()
        self._no_internet = False

        self.favourite_ixon_ids: dict[str, Agent] = {}

        self.current_item_menu = []

        self._agent_store = BaseModelStore[AgentList](file_path=AGENTS_FILE_PATH, empty_if_not_valid=True)
        self._agents_list = self._agent_store.load()

        self._command_store = BaseModelStore[Commands](
            file_path=COMMAND_FILE_PATH,
            default_path=INSTALL_DIR / COMMAND_FILE_NAME,
        )
        self._commands = self._command_store.load()

        self.connected_icon = QIcon(os.path.join(INSTALL_DIR, "icon.png"))
        self.disconnected_icon = QIcon(os.path.join(INSTALL_DIR, "icon_not_connected.png"))

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(os.path.join(INSTALL_DIR, "icon_not_connected.png")))
        self.tray.setVisible(True)

        # Setting up persistent settings
        self._settings = qsettings
        self._settings_window = SettingsWindow(settings=self._settings)

        self._ixon_api_v1: None | IxonCloudAPIv1 = None
        self._ixon_vpn_client = None
        self._setup_ixon_apis()

        self._ixon_status = {}
        # Status will be updated by the StatusWorker

        self._settings_window.closeEvent = self.update_settings
        self._settings_window.commands_tab.commands_updated.connect(self.save_commands_cb)

        self._settings_window.commands_tab.set_commands(self._commands)
        # self._settings_window.show()

        self.load_favourite_ixon_ids()
        self._settings_window.clients_tab.set_all_clients(self._agents_list.agents_by_id, self.favourite_ixon_ids)

        # Creating the options
        self.setup_menu()

        self.tray.show()

        # Create threads for background workers
        self._status_thread = QThread()
        self._agents_thread = QThread()

        # Create worker objects
        self._status_worker = StatusWorker(self._ixon_vpn_client)
        self._agents_worker = AgentsWorker(self._ixon_api_v1, self._ixon_api_v2)

        # Move workers to their threads
        self._status_worker.moveToThread(self._status_thread)
        self._agents_worker.moveToThread(self._agents_thread)

        # Connect signals and slots
        self._status_worker.status_updated.connect(self._handle_status_update)
        self._status_worker.error_occurred.connect(self._handle_status_error)
        self._agents_worker.agents_updated.connect(self._handle_agents_update)
        self._agents_worker.error_occurred.connect(self._handle_agents_error)

        # Connect thread started signals to worker run methods
        self._status_thread.started.connect(self._status_worker.run)
        self._agents_thread.started.connect(self._agents_worker.run)

        # Start the status thread immediately
        self._status_thread.start()

        # Start the agents update immediately and then periodically
        self.update_agents()

        if not self.get_auth_string(otp="Dummy"):
            logger.info("Please provide login credentials")

        logger.info("Started application, use tray icon to interact")
        telemetry.send()

    def load_favourite_ixon_ids(self) -> None:
        """Load favorite IXON agent IDs from settings.

        This method loads the favorite IXON agent IDs from the application settings
        and populates the favourite_ixon_ids dictionary. It filters out any IDs that
        are not present in the current agents_by_id dictionary.
        """
        self._settings.beginGroup("favourite_clients")
        keys = self._settings.allKeys()
        if self._agents_list.agents_by_id:
            self.favourite_ixon_ids = {
                k: self._agents_list.agents_by_id[k] for k in keys if k in self._agents_list.agents_by_id
            }
        else:
            self.favourite_ixon_ids = {}
        self._settings.endGroup()

    def save_favourite_ixon_ids(self, favourite_ixon_ids: dict[str, str]) -> None:
        """Save favorite IXON agent IDs to settings.

        Args:
            favourite_ixon_ids: Dictionary mapping client names to client IDs

        This method saves the favorite IXON agent IDs to the application settings.
        It first clears the existing favorites and then saves the new ones.
        """
        self._settings.beginGroup("favourite_clients")
        self._settings.remove("")
        for client_name, client_id in favourite_ixon_ids.items():
            logger.info(f"Saving the following clients: {client_id}:{client_name}")
            self._settings.setValue(f"{client_name}", client_id)
        self._settings.endGroup()

    def setup_menu(self) -> None:
        """Set up the system tray menu.

        This method creates and configures the system tray menu with various options:
        - Connection status
        - Menu items for the currently connected client
        - Global menu items
        - Menu items for favorite clients
        - Menu items for all clients
        - Configuration, disconnect, and quit options
        - Update notification if available

        It's called during initialization and whenever the menu needs to be refreshed,
        such as after connecting to a client or updating settings.
        """
        self.menu.clear()

        self.connection_status = self.menu.addAction("Not Connected")
        self.menu.addAction(self.connection_status)
        self.menu.addSeparator()

        # Add entries for the current connected client
        self.add_menu_items_for_connected_client(self.menu)
        self.menu.addSeparator()
        self.add_global_menu_items(self.menu)

        self.menu.addSeparator()

        self.add_menu_items_for_favourites(self.menu)

        self.menu.addSeparator()
        self.add_menu_items_for_all_clients(self.menu)

        self.menu.addSeparator()
        # To disconnect
        self.open_settings_action = QAction("Configuration")
        self.open_settings_action.setIcon(QIcon.fromTheme("application-self.menu-symbolic"))
        self.open_settings_action.triggered.connect(self.open_settings)
        self.menu.addAction(self.open_settings_action)
        # To disconnect
        self.disconnect = QAction("Disconnect VPN")
        self.disconnect.setIcon(QIcon.fromTheme("network-vpn-disconnected-symbolic"))
        self.disconnect.triggered.connect(self.disconnect_from_ixon)
        self.menu.addAction(self.disconnect)
        # To quit the app
        self.quit = QAction("Quit")
        self.quit.setIcon(QIcon.fromTheme("application-exit-symbolic"))
        self.quit.triggered.connect(app.quit)
        self.menu.addAction(self.quit)

        update, version = update_available()

        if update:
            self.menu.addSeparator()
            self.update = QAction(f"Update to {version} available. (Open pypi)")
            self.update.setIcon(QIcon.fromTheme("dialog-warning"))
            self.menu.addAction(self.update)
            self.update.triggered.connect(self.open_pypy)

        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.show_menu)
        self.tray.setToolTip("Ixontray")

    def open_pypy(self, *_args: Any, **_kwargs: Any) -> None:
        """Open the link to the PyPI website for the ixontray package.

        Args:
            *_args: Variable length argument list (ignored)
            **_kwargs: Arbitrary keyword arguments (ignored)

        This method is called when the user clicks on the update notification
        in the system tray menu. It opens the default web browser to the
        ixontray package page on PyPI, where the user can download the latest version.
        """
        url = QtCore.QUrl("https://pypi.org/project/ixontray/")
        QtGui.QDesktopServices.openUrl(url)

    def add_menu_items_for_all_clients(self, menu: QMenu) -> None:
        """Add menu items for all clients to the system tray menu.

        Args:
            menu: The menu to add items to

        This method adds a submenu with all available IXON clients (agents) to the
        system tray menu. Each client is represented by a menu item that, when clicked,
        connects to that client. The menu items are decorated with icons indicating
        whether the client is online or offline.
        """
        sub_menu = menu.addMenu("All other clients")
        for ixon_id, agent in self._agents_list.agents_by_id.items():
            connect = sub_menu.addAction(agent.full_name)
            connect.triggered.connect(lambda _, ixon_id=ixon_id: self.connect_to_ixon(ixon_id=ixon_id))
            if agent.online:
                connect.setIcon(QIcon.fromTheme("emblem-default"))
            else:
                connect.setIcon(QIcon.fromTheme("emblem-unreadable"))

    def add_menu_items_for_favourites(self, menu: QMenu) -> None:
        """Add menu items for favorite clients to the system tray menu.

        Args:
            menu: The menu to add items to

        This method adds submenus for each favorite IXON client (agent) to the
        system tray menu. Each submenu contains:
        - A "Connect VPN" option to connect to the client
        - Options to connect and run commands (if defined)
        - A submenu for IXON-defined servers (if any)

        The menu items are decorated with icons indicating whether the client
        is online or offline, and tooltips providing additional information.
        """
        for ixon_id, agent in self.favourite_ixon_ids.items():
            sub_menu = menu.addMenu(agent.full_name)

            # Add default
            connect = sub_menu.addAction("Connect VPN")
            if self._agents_list.agents_by_id[ixon_id].online:
                connect.setIcon(QIcon.fromTheme("network-vpn-symbolic"))
                connect.setToolTip("Click to connect")
            else:
                sub_menu.setIcon(QIcon.fromTheme("emblem-unreadable"))
                connect.setIcon(QIcon.fromTheme("emblem-unreadable"))
                connect.setToolTip("Client is not reachable")

            connect.triggered.connect(lambda _, ixon_id=ixon_id: self.connect_to_ixon(ixon_id=ixon_id))

            for cmd in self._commands.commands:
                if "item" in cmd.show_in:
                    menu_action = sub_menu.addAction(f"Connect and {cmd.name}")
                    menu_action.setIcon(QIcon.fromTheme(cmd.icon))
                    menu_action.triggered.connect(functools.partial(self.run_command, command=cmd, ixon_id=ixon_id))

            # Add a sub menu for all defined servers
            self.menu.addSeparator()
            self.add_server_menu(agent, ixon_id, sub_menu)

    def add_server_menu(self, agent: Agent, ixon_id: str, menu: QMenu) -> QMenu:
        """Add a submenu for IXON-defined servers.

        Args:
            agent: The IXON agent (client)
            ixon_id: The ID of the IXON agent
            menu: The menu to add the submenu to

        Returns:
            QMenu: The created submenu

        This method adds a submenu with IXON-defined servers for the specified agent.
        Each server is represented by a menu item that, when clicked, runs the
        server command for that server.
        """
        sub_menu = menu.addMenu("IXON defined servers (Beta)")
        for server in agent.servers:
            menu_action = sub_menu.addAction(server.name)
            menu_action.triggered.connect(
                functools.partial(self.run_server_command, agent=agent, ixon_id=ixon_id, server=server),
            )
        return sub_menu

    def run_server_command(self, agent: Agent, server: Server, ixon_id: str) -> None:
        """Run a command for an IXON-defined server.

        Args:
            agent: The IXON agent (client)
            server: The IXON-defined server
            ixon_id: The ID of the IXON agent

        This method gets the web access URL for the specified server from the
        appropriate IXON API (v1 or v2), creates a command to open the URL in
        the default web browser, and runs the command.
        """
        if agent.api_version == 1:
            url = self._ixon_api_v1.get_webaccess_url_from_server(agent, server)
        else:
            url = self._ixon_api_v2.get_webaccess_url_from_server(agent, server)

        if url:
            xdg_open_command = Command(
                name=f"XDG_open {server.name}",
                icon="web-browser-symbolic",
                cmd=f"xdg-open {url}",
                force_connection=False,
            )

            self.run_command(command=xdg_open_command, ixon_id=ixon_id)

    def add_global_menu_items(self, menu: QMenu) -> None:
        """Add global menu items to the system tray menu.

        Args:
            menu: The menu to add items to

        This method adds global menu items to the system tray menu. Global menu items
        are commands that are always available, regardless of the connection status.
        Each command is represented by a menu item that, when clicked, runs the command.
        The menu items are decorated with icons specified in the command definition.
        """
        for cmd in self._commands.commands:
            if "global" in cmd.show_in:
                menu_action = menu.addAction(cmd.name)
                menu_action.setIcon(QIcon.fromTheme(cmd.icon))
                menu_action.triggered.connect(functools.partial(self.run_command, command=cmd))

    def add_menu_items_for_connected_client(self, menu: QMenu) -> None:
        """Add menu items for the currently connected client to the system tray menu.

        Args:
            menu: The menu to add items to

        This method adds menu items for the currently connected IXON client (agent)
        to the system tray menu. These items include:
        - Commands that are configured to show for connected clients
        - A submenu for IXON-defined servers (if any)

        The menu items are stored in the current_item_menu list so they can be
        enabled or disabled based on the connection status.
        """
        self.current_item_menu = []
        ixon_id = self._ixon_status.get("agentId", None)

        for cmd in self._commands.commands:
            if "item" in cmd.show_in:
                self.current_item_menu.append(menu.addAction(f"{cmd.name}"))
                self.current_item_menu[-1].setIcon(QIcon.fromTheme(cmd.icon))
                self.current_item_menu[-1].triggered.connect(
                    functools.partial(self.run_command, command=cmd, ixon_id=ixon_id)
                )

        # Add a sub menu for all defined servers
        self.menu.addSeparator()
        if ixon_id:
            agent = self._agents_list.agents_by_id[ixon_id]
            self.current_item_menu.append(self.add_server_menu(agent, ixon_id, menu))

    def disconnect_from_ixon(self) -> None:
        """Disconnect from the IXON VPN.

        This method disconnects from the currently connected IXON VPN client.
        It shows a notification in the system tray and logs the disconnection.
        """
        self.tray.showMessage("IXON tray", "Disconnecting")
        logger.info("Disconnecting...")
        self._ixon_vpn_client.disconnect()

    def show_menu(self, _: QEvent) -> None:
        """Show the system tray menu.

        Args:
            _: The event that triggered this method (ignored)

        This method is called when the user clicks on the system tray icon.
        It displays the system tray menu at the current cursor position.
        """
        self.menu.show()

    def update_settings(self, _: QCloseEvent) -> None:
        """Update settings when the settings window is closed.

        Args:
            _: The close event that triggered this method (ignored)

        This method is called when the settings window is closed. It:
        1. Sets up the IXON APIs with the updated credentials
        2. Saves and loads the favorite IXON IDs
        3. Updates the commands in the settings window
        4. Refreshes the system tray menu
        5. Schedules an update of the agents list
        """
        self._setup_ixon_apis()

        if self._ixon_api_v1 is not None and self._ixon_api_v1.has_valid_token():
            fav_ixon_ids = self._settings_window.clients_tab.get_favourite_ixon_ids()
            self.save_favourite_ixon_ids(fav_ixon_ids)
            self.load_favourite_ixon_ids()
            self._settings_window.commands_tab.set_commands(self._commands)
            self.setup_menu()

        QTimer.singleShot(100, self.update_agents)

    def _handle_status_update(self, status: dict) -> None:
        """Handle status updates from the status worker.

        Args:
            status: The updated status dictionary from the IXON VPN client

        This method is called when the StatusWorker emits a status_updated signal.
        It updates the _ixon_status variable with the new status and calls
        _update_ui_status() to update the UI accordingly.
        """
        self._ixon_status = status
        self._update_ui_status()

    def _handle_status_error(self, error_msg: str) -> None:
        """Handle errors from the status worker.

        Args:
            error_msg: The error message from the StatusWorker

        This method is called when the StatusWorker emits an error_occurred signal.
        It displays the error message in the system tray.
        """
        self.tray.showMessage("IXON tray", error_msg)

    def _handle_agents_update(self, agents: dict) -> None:
        """Handle agent updates from the agents worker.

        Args:
            agents: Dictionary mapping agent IDs to Agent objects

        This method is called when the AgentsWorker emits an agents_updated signal.
        It updates the agents list, updates the clients tab in the settings window,
        saves the agents to the agent store, refreshes the system tray menu,
        and schedules the next agents update in 5 minutes.
        """
        logger.info("Received updated agent info.")
        self._agents_list.agents_by_id = agents

        self._settings_window.clients_tab.set_all_clients(
            clients=self._agents_list.agents_by_id,
            favourites=self.favourite_ixon_ids,
        )
        self._agent_store.save(self._agents_list)
        self.setup_menu()

        # Schedule next update in 5 minutes
        QTimer.singleShot(1000 * 60 * 5, self.update_agents)

    def _handle_agents_error(self, error_msg: str) -> None:
        """Handle errors from the agents worker.

        Args:
            error_msg: The error message from the AgentsWorker

        This method is called when the AgentsWorker emits an error_occurred signal.
        It displays the error message in the system tray, shows the login credentials
        dialog (since most errors are related to authentication), and schedules a retry
        in 30 seconds.
        """
        self.tray.showMessage("IXON tray", error_msg)
        self.show_login_credentials()

        # Retry in 30 seconds if there was an error
        QTimer.singleShot(1000 * 30, self.update_agents)

    def update_agents(self) -> None:
        """Start the agents update process in a background thread."""
        logger.info("Starting agent update in background thread.")
        if self._ixon_api_v1 is not None and self._ixon_api_v1.has_valid_token():
            # Refresh auth token
            self._setup_ixon_apis()

            # Update the worker's API references
            self._agents_worker._ixon_api_v1 = self._ixon_api_v1
            self._agents_worker._ixon_api_v2 = self._ixon_api_v2

            # Start the agents thread if it's not already running
            if not self._agents_thread.isRunning():
                self._agents_thread.start()
            else:
                # If thread is already running, just call run directly
                # This is safe because run() is designed to exit after one execution
                self._agents_worker.run()
        else:
            self.show_login_credentials()
            # Retry in 30 seconds
            QTimer.singleShot(1000 * 30, self.update_agents)

        telemetry.send()

    @log_telemetry
    def open_settings(self, _: bool = False) -> None:
        logger.info("Opening settings window")
        self._settings_window.show()

    def _update_ui_status(self) -> None:
        """Update the UI based on the current VPN status."""
        if self._ixon_api_v1 is not None and self._ixon_api_v1.has_valid_token():
            logging.debug(self._ixon_status)

            if self._ixon_vpn_client.connected():
                ixon_id = self._ixon_status["agentId"]

                if ixon_id in self._agents_list.agents_by_id:
                    self.connection_status.setText(f"Connected to: {self._agents_list.agents_by_id[ixon_id].full_name}")

                self.tray.setIcon(self.connected_icon)
                for i in self.current_item_menu:
                    i.setEnabled(True)
            elif self._ixon_status.get("data", "") == CONNECTION_STATUS.CONNECTING:
                if self.tray.icon() == self.disconnected_icon:
                    self.tray.setIcon(self.connected_icon)
                else:
                    self.tray.setIcon(self.disconnected_icon)
            else:
                self.connection_status.setText("Not connected")
                self.tray.setIcon(self.disconnected_icon)
                for i in self.current_item_menu:
                    i.setEnabled(False)

    @log_telemetry
    def update_status(self, _: bool = False) -> None:
        """Legacy method for compatibility. Now UI updates are handled by _update_ui_status()."""
        # This method is kept for compatibility with any existing code that might call it
        self._update_ui_status()

    def _get_company_id_for(self, ixon_id: str) -> str:
        return self._agents_list.agents_by_id[ixon_id].company_id


@log_telemetry
def create_and_open_launcher() -> Launcher:
    """Open the launcher window at the current mouse cursor position."""
    agent_list = BaseModelStore[AgentList](file_path=AGENTS_FILE_PATH, empty_if_not_valid=True).load()
    commands = BaseModelStore[Commands](
        file_path=COMMAND_FILE_PATH,
        default_path=INSTALL_DIR / COMMAND_FILE_NAME,
    ).load()
    launcher = Launcher(settings=qsettings)
    launcher.set_agents(agents=agent_list)
    launcher.set_commands(commands=commands)

    # Show the launcher to ensure it calculates its proper size
    launcher.show()

    # Get the screen where the cursor is
    cursor_pos = QtGui.QCursor.pos()
    screen = QApplication.screenAt(cursor_pos)
    if not screen:
        screen = QApplication.primaryScreen()

    # Center the launcher on the screen where the cursor is
    launcher.center(screen=screen)

    # Hide the launcher so the caller can show it when ready
    launcher.hide()

    return launcher


app = QApplication(sys.argv)


def main() -> None:
    import sentry_sdk

    print("Init sentry skd")
    sentry_sdk.init(
        dsn="https://e9bf581a98f70e612e1a8e912aee997d@o4508358154059776.ingest.de.sentry.io/4508442503610448",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        attach_stacktrace=True,
        include_source_context=True,
        include_local_variables=True,
        profiles_sample_rate=1.0,
    )

    parser = argparse.ArgumentParser(
        description="""
    This program lets you easily connect to an ixon host and optionally execute an commands.

    There are two ways to interact with the program.

      1. Through the ixontray icon, launched by running ixontray without arguments
      2. Through the ixontray --launcher ran by running ixontray --launcher.

    Trouble shooting:
        If the program crashes at startup try installing:
        ----------------------------------------------------------------------------------------------------------------
        $sudo apt-get -qq install libegl1 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0
            libxcb-render-util0 libxcb-shape0 libxkbcommon-x11-0
        ----------------------------------------------------------------------------------------------------------------

    """,
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "--launcher",
        "-l",
        action="store_true",
        default=False,
        help="Launch the launcher not the tray icon.",
    )
    parser.add_argument(
        "--auto-update",
        "-u",
        action="store_true",
        default=False,
        help="Update ixontray",
    )

    parser.add_argument(
        "--print-telemetry-report",
        "-r",
        type=int,
        nargs="?",
        const=-1,
        help="Print data collected by telemetry",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        default=False,
        help="Print version",
    )

    try:
        update, version = update_available()
        if update:
            print("#" * 60)
            print(f"Update available to {version} you are on {ixontray.__version__}, please update :-)")
            print("#" * 60)
            time.sleep(1)

        args = parser.parse_known_args()[0]

        if args.version:
            print(f"{ixontray.__version__}")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal.SIG_DFL)

        if args.print_telemetry_report is not None:
            rn = args.print_telemetry_report
            telemetry.print(report_num=rn if rn >= 0 else None)
            sys.exit(0)

        if args.auto_update:
            print(f"auto update! {__file__}")
            os.system("pip install --upgrade ixontray --dry-run")
            sys.exit(0)

        if args.launcher:
            launcher = create_and_open_launcher()
            launcher.show()
            telemetry.send()

        else:
            app.setQuitOnLastWindowClosed(False)
            IxonTray()

        code = app.exec()
        telemetry.send()
        sys.exit(code)
    except Exception as e:
        telemetry.log_crash_report()
        telemetry.send()

        raise e
