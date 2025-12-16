# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import argparse
import asyncio
import base64
import fnmatch
import io
import os
import pathlib
import sys
from typing import Optional

import aiohttp
import requests
import yarl
from requests_toolbelt.multipart.encoder import MultipartEncoder

import laam.exceptions
import laam.utils
from laam.commands import (
    dut,
    files,
    identities,
    laacli,
    network,
    serials,
    services,
    system,
    usbs,
    workers,
)

#############
# Constants #
#############
__version__ = "0.8.3"


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="laam", description="Linaro Automation Appliance Manager"
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s, v{__version__}"
    )

    # identity or url
    url = parser.add_argument_group("identity")
    url.add_argument("--uri", type=str, default=None, help="URI of the LAA API")
    url.add_argument(
        "--token",
        metavar="TOKEN",
        type=str,
        default=None,
        help="Token for the LAA API",
    )
    url.add_argument(
        "--identity",
        "-i",
        metavar="ID",
        type=str,
        default=None,
        help="Identity stored in the configuration",
    )

    sub = parser.add_subparsers(
        dest="cmd", help="Command", title="Command", required=True
    )
    COMMANDS = {
        "identities": identities,
        "dut": dut,
        "files": files,
        "laacli": laacli,
        "network": network,
        "serials": serials,
        "services": services,
        "system": system,
        "usbs": usbs,
        "workers": workers,
    }
    for name, cls in COMMANDS.items():
        cmd_parser = sub.add_parser(name, help=cls.help_string())
        cls.configure_parser(cmd_parser)

    return parser


##############
# Entrypoint #
##############
def main() -> int:
    # Parse arguments
    parser = setup_parser()
    options = parser.parse_args()

    # Skip when sub_command is "identities"
    # Skip when command is "identities" or "dut new|check"
    if not (
        options.cmd == "identities"
        or (options.cmd == "dut" and options.sub_cmd in ["new", "check"])
    ):
        if options.identity and (options.uri or options.token):
            parser.error("Either define --identity or --uri/--token but not both")
        if options.identity is None:
            if options.uri is None and options.token is None:
                options.identity = "default"
            elif options.uri is None or options.token is None:
                parser.error("--uri and --token should be defined both")

        if options.identity:
            configs = identities._load_configuration()
            if options.identity not in configs:
                print("Unknown identity '%s'" % options.identity, file=sys.stderr)
                return 1
            config = configs[options.identity]
            token = config.get("token")
            if token is None:
                print("Token is missing from identity config file", file=sys.stderr)
                return 1
            options.uri = config["uri"]
            options.token = token

        if not options.uri.startswith(("http://", "https://")):
            print(
                f"Error: Invalid URI '{options.uri}'. Must start with http:// or https://",
            )
            print(
                "Please check your configuration file or --uri argument",
            )
            return 1

        options.ws_url = (
            options.uri.replace("http://", "ws://").replace("https://", "wss://")
            + "/ws/"
        )
        options.uri = options.uri + "/api/v1"

    session = requests.Session()
    session.headers.update(
        {
            "Accept-Encoding": "",
            "Authorization": f"Bearer {options.token}",
            "User-Agent": f"laam v{__version__}",
        }
    )

    laa = None
    if options.identity != None:
        laa = LAA(options.identity)

    return options.func(options, laa)


##################
# LAA SuperClass #
##################
class LAA:
    """
    Main Abstraction class to interact with a Linaro Automation Appliance.

    This class provides the core object model and methods required to remotely
    interact with an LAA from the host machine using LAAM. It abstracts the
    underlying communication protocols (e.g., REST, WebSockets) necessary to control
    the Appliance's primary functions to control the Device Under Test mounted
    on the LAA itself.
    The functions include power cycling, logs, usb control, serial interaction, etc...
    """

    def __init__(self, laa_identity="default"):
        """
        Initializes the interface object for the target LAA.

        This method prepares the interface object using the provided identity.
        The identity is critical for addressing and authenticating a specific LAA.

        --- Authentication Note ---
        To authenticate and enable control, you must:
        1. Create an API token on the LAA: (See: https://docs.lavacloud.io/software/api.html#authentication).
        2. Manually configure the LAAM environment to use the token: (See: https://docs.lavacloud.io/software/laam.html#configuration).

        Args:
            laa_identity (str): A required unique string identifier the target LAA.
        """
        self.laa_info = identities._load_configuration()[laa_identity]
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept-Encoding": "",
                "Authorization": f"Bearer {self.laa_info['token']}",
                "User-Agent": f"laam v{__version__}",
            }
        )
        self.base_uri = yarl.URL(self.laa_info["uri"] + "/api/v1")

        # Lazy initialization
        self._files = None
        self._laacli = None
        self._network = None
        self._serials = None
        self._services = None
        self._system = None
        self._usbs = None
        self._workers = None

    class Files:
        """
        Class for file management and transfer on the LAA.

        NOTE:
        This class should NOT be instantiated directly by the user.
        Access to these functions is available only via the main LAA object..
        """

        def __init__(self, laa):
            self.session = laa.session
            self.base_uri = yarl.URL(laa.base_uri)

        def list(self) -> list:
            """
            Lists all the files in the working folder.

            Returns:
                A list of file names.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """
            ret = laam.utils.basic_request(self.session, "GET", self.base_uri / "files")
            return ret.json()["items"]

        def pull(self, name: str, file: pathlib.Path, force: bool = False) -> bool:
            """
            Downloads a file from the LAA the working folder to the local machine.

            Args:
                name (str): The name of the file on the LAA to be downloaded.
                file (pathlib.Path): The file path to save the file downloaded from the LAA.

            Returns:
                bool: True if the file was downloaded successfully, False otherwise.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            if file == None:
                print("File is None", file=sys.stderr)
                return False

            if os.path.exists(file) and not force:
                print(
                    "The file already exists on this machine, please use the force flag",
                    file=sys.stderr,
                )
                return False

            ret = laam.utils.basic_request(
                self.session,
                "GET",
                self.base_uri / "files" / name,
                "File not found",
                stream=True,
            )

            with file.open("wb") as fileobj:
                for data in ret.iter_content(32768):
                    print(".", end="")
                    fileobj.write(data)

            return True

        def push(self, name: str, file) -> bool:
            """
            Uploads a file from local machine to the LAA the working folder.

            Args:
                name (str): The name of the file to be saved on the LAA as.
                file (str, pathlib.Path, os.PathLike, io.BufferedReader):
                    The file on the local machine to be uploaded.
                    It can be a path to the object file itself.

            Returns:
                bool: True if the file was uploaded successfully, False otherwise.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            if file == None:
                print("File is None", file=sys.stderr)
                return False

            if isinstance(file, (str, os.PathLike, pathlib.Path)):
                with open(file, "rb") as fileobj:
                    me = MultipartEncoder(fields={"file": (name, fileobj)})
                    laam.utils.basic_request(
                        self.session,
                        "POST",
                        self.base_uri / "files" / name,
                        None,
                        data=me,
                        headers={"Content-Type": me.content_type},
                    )
            elif isinstance(file, io.BufferedReader):
                me = MultipartEncoder(fields={"file": (name, file)})
                laam.utils.basic_request(
                    self.session,
                    "POST",
                    self.base_uri / "files" / name,
                    None,
                    data=me,
                    headers={"Content-Type": me.content_type},
                )
            else:
                print(
                    f"File is not a any of these data types {(str, os.PathLike, pathlib.Path, io.BufferedReader)}",
                    file=sys.stderr,
                )
                return False

            return True

        def remove(self, name: str) -> bool:
            """
            Removes a file in the LAA the working folder.

            Args:
                name (str): The name of the file to be removed.

            Returns:
                bool: True if the file was removed successfully, False otherwise.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """
            laam.utils.basic_request(
                self.session, "DELETE", self.base_uri / "files" / name, "File not found"
            )
            return True

    class LAACli:
        """
        Class for executing laacli commands on the LAA.

        NOTE:
        This class should NOT be instantiated directly by the user.
        Access to these functions is available only via the main LAA object.
        """

        def __init__(self, laa):
            self.session = laa.session
            self.base_uri = yarl.URL(laa.base_uri)

        def button(self, button: str, state: str) -> dict:
            """
            Controls the virtual buttons on the LAA.

            Args:
                button (str): The virtual button to control. Available choices are: "1", "2", "power", "reset".
                state (str): State to set on the button. Available choices are: "on", "off", "status".

            Returns:
                dict: Returned command execution object.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """
            ret = laam.utils.basic_request(
                self.session,
                "POST",
                self.base_uri / "laacli" / "button",
                None,
                json={"button": button, "state": state},
            )
            ret_json = ret.json()
            if ret_json["code"] != 0:
                raise laam.exceptions.LAACliError(ret_json)
            return ret_json

        def led(self, state: str) -> dict:
            """
            Controls the status LED on the LAA.

            Args:
                state (str): The state of the LED. Available choices are: "on", "off".

            Returns:
                dict: Returned command execution object

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            if state not in ("on", "off"):
                raise laam.exceptions.LAAError(f"Invalid state {state}")

            try:
                ret = laam.utils.basic_request(
                    self.session,
                    "POST",
                    self.base_uri / "laacli" / "led",
                    None,
                    json={"state": state},
                )

            except laam.exceptions.LAAApiError as exc:
                if exc.http_code == 422:
                    # led fix introduced after LAA OS release (>v1.6.1)
                    message = "Not available in this version, please check available LAA updates"
                    raise laam.exceptions.LAAError(message) from exc
                else:
                    raise exc

            ret_json = ret.json()
            if ret_json["code"] != 0:
                raise laam.exceptions.LAACliError(ret_json)
            return ret.json()

        def power(self, vbus: str, state: str) -> dict:
            """
            Controls the power rails on the LAA.

            Args:
                vbus (str): Power rail to control. Available choices are: "1v8", "3v3", "5v", "12v".
                state (str): State to set the rail. Available choices are: "on", "off", "reset", "status".

            Returns:
                dict: Returned command execution object.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """
            ret = laam.utils.basic_request(
                self.session,
                "POST",
                self.base_uri / "laacli" / "power",
                None,
                json={"vbus": vbus, "state": state},
            )
            ret_json = ret.json()
            if ret_json["code"] != 0:
                raise laam.exceptions.LAACliError(ret_json)
            return ret.json()

        def rev(self) -> dict:
            """
            Returns the hardware revision of the LAA.

            Returns:
                dict: Returned revision object.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "POST", self.base_uri / "laacli" / "rev"
            )
            ret_json = ret.json()
            if ret_json["code"] != 0:
                raise laam.exceptions.LAACliError(ret_json)
            return ret.json()

        def screenshot(self, filename) -> dict:
            """
            Screenshots the current OLED and downloads it as a file on the local machine.

            Args:
                filename (str, os.PathLike, pathlib.Path, io.BufferedWriter):
                    It can be the file path to save the file downloaded from the LAA, or
                    the opened file object itself.

            Returns:
                dict: Returned command execution object.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "POST", self.base_uri / "laacli" / "screenshot"
            )

            ret_json = ret.json()
            ret_info = {
                "stdout": ret_json["stdout"],
                "stderr": ret_json["stderr"],
                "code": ret_json["code"],
            }
            if ret_json["code"] != 0:
                raise laam.exceptions.LAACliError(ret_info)

            data = base64.b64decode(ret_json["screenshot"])
            if isinstance(filename, (str, os.PathLike, pathlib.Path)):
                with open(filename, "wb") as file:
                    file.write(data)
            elif isinstance(filename, io.BufferedWriter):
                filename.write(data)

            return ret_info

        def temp(self, probe: str) -> dict:
            """
            Returns temperature information from the LAA.

            Args:
                probe (str): Temperature probe to check. Available choices are: "amb", "dut", "sys".

            Returns:
                dict: Temperature information.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session,
                "POST",
                self.base_uri / "laacli" / "temp",
                None,
                json={"probe": probe},
            )
            ret_json = ret.json()
            if ret_json["code"] != 0:
                raise laam.exceptions.LAACliError(ret_json)
            return ret.json()

        def usb(self, port: int, state: str) -> dict:
            """
            Controls the four USB ports on the LAA (the ones pointing upwards).

            Args:
                port (int): USB port to control. Available choices are: 0, 1, 2, 3, 4.
                            Where 0 is the USB Hub controlling USB ports 1, 2, 3, 4.
                state (str): State to set the port or just check the status. Available choices are: "on", "off", "reset", "start", "status".

            Returns:
                dict: Returned command execution object.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session,
                "POST",
                self.base_uri / "laacli" / "usb",
                None,
                json={"port": port, "state": state},
            )
            ret_json = ret.json()
            if ret_json["code"] != 0:
                raise laam.exceptions.LAACliError(ret_json)
            return ret.json()

        def usbg_ms(self, state: str, filename: str = "") -> dict:
            """
            Controls the USBG-MS port on the LAA (the ones at the front marked as USB-OTG).

            Args:
                state (str): State to set the port or just check the status. Available choices are: "on", "off", "status".
                filename (str): File name of the image to be used, It is assumed to be located in the working LAA folder.
                                Parameter needed only if the status is set to "on".

            Returns:
                dict: Returned command execution object.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session,
                "POST",
                self.base_uri / "laacli" / "usbg-ms",
                None,
                json={"state": state, "filename": filename},
            )
            ret_json = ret.json()
            if ret_json["code"] != 0:
                raise laam.exceptions.LAACliError(ret_json)
            return ret.json()

        def watt(self, vbus: str) -> dict:
            """
            Returns power usage information from the LAA.

            Args:
                vbus (str): Power rail to check. Available choices are: "1v8", "3v3", "5v", "12v".

            Returns:
                dict: Power usage information.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session,
                "POST",
                self.base_uri / "laacli" / "watt",
                None,
                json={"vbus": vbus},
            )
            ret_json = ret.json()
            if ret_json["code"] != 0:
                raise laam.exceptions.LAACliError(ret_json)
            return ret.json()

    class Network:
        """
        Class for monitoring the LAA's network interfaces.

        NOTE:
        This class should NOT be instantiated directly by the user.
        Access to these functions is available only via the main LAA object.
        """

        def __init__(self, laa):
            self.session = laa.session
            self.base_uri = yarl.URL(laa.base_uri)

        def addresses(self) -> dict:
            """
            Returns the addresses of the LAA.

            Returns:
                dict: Addresses information.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "network" / "addresses"
            )
            return ret.json()

        def hostname(self) -> dict:
            """
            Returns the hostname of the LAA.

            Returns:
                dict: Returns the hostname.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "network" / "hostname"
            )
            return ret.json()

        def interfaces(self) -> list:
            """
            Returns the interfaces of the LAA.

            Returns:
                list: Returns the interfaces.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "network" / "interfaces"
            )
            return ret.json()["items"]

        def routes(self) -> dict:
            """
            Returns the network routes of the LAA.

            Returns:
                dict: Returns the routes.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "network" / "routes"
            )
            return ret.json()

        def settings(self) -> str:
            """
            Returns the network settings of the LAA.

            Returns:
                str: Returns the settings.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "network" / "settings"
            )
            return ret.text

    class Serials:
        """
        Class for managing and interacting with the LAA's serial consoles with the DUT.

        NOTE:
        This class should NOT be instantiated directly by the user.
        Access to these functions is available only via the main LAA object.
        """

        def __init__(self, laa):
            self.laa = laa
            self.session = laa.session
            self.ws_headers = {
                "Authorization": self.session.headers["Authorization"],
                "User-Agent": self.session.headers["User-Agent"],
            }

            self.base_uri = yarl.URL(laa.base_uri)
            self.ws_url = (
                yarl.URL(laa.laa_info["uri"]).with_scheme(
                    "wss" if self.base_uri.scheme == "https" else "ws"
                )
                / "ws"
                / ""
            )

        def list(self, ser_filter=None) -> list:
            """
            Lists all the serials accessible via the LAA.

            Args:
                ser_filter: Filter value to log out specific serials.

            Returns:
                list: Returns a list of serials.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "devices" / "serials"
            )

            if ser_filter:
                return [
                    k
                    for k in ret.json()["items"]
                    if fnmatch.fnmatch(k["path"], ser_filter)
                ]
            else:
                return [k for k in ret.json()["items"]]

        def get(self, name: str) -> dict:
            """
            Returns the details of a specific serial console.

            Args:
                name (str): Name of the serial console, example "ttyUSB0".

            Returns:
                dict: Returns serial information.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session,
                "GET",
                self.base_uri / "devices" / "serials" / name,
                "Serial not found",
            )
            return ret.json()

        async def connect_async_fun(
            self,
            name: str,
            readonly: bool = False,
            istream: io.TextIOBase = sys.stdin,
            ostream: io.TextIOBase = sys.stdout,
            force_str: Optional[bool] = None,
        ) -> int:
            """
            Connects to a serial console with the DUT in an async function.

            Args:
                name (str): Name of the serial console, example "ttyUSB0".
                readonly (bool): True to start a readonly serial connection.
                                 (Default) False for an interactive connection
                istream (io.TextIOBase): Input stream used to send data to the DUT on the LAA.
                                         Defaults to sys.stdin.
                ostream (io.TextIOBase): Output stream used to receive data from the DUT on the LAA.
                                         Defaults to sys.stdout.
                force_str (Optional[bool]):
                                    True to exchange data as string.
                                    False to exchange data as bytes.
                                    (Default) None to automatically use the best option.
                                    Exposed mostly for testing purposes.

            Returns:
                int: 0 if the serial connection completed by itself without errors.
                     1 if it failed or got interrupted.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            serial = self.get(name)
            if force_str == None:
                force_str = bool(self.laa.system.version() < "1.6")
            try:
                params = {"port": int(serial["port"])}
                if readonly:
                    params["readonly"] = str(readonly)

                async with aiohttp.ClientSession() as wssession:
                    async with wssession.ws_connect(
                        self.ws_url, params=params, heartbeat=5, headers=self.ws_headers
                    ) as ws:
                        stdin_reader_task = asyncio.create_task(
                            laam.utils.stdin_reader(ws, istream, force_str)
                        )
                        async for msg in ws:
                            # Allow for both binary (new) and text (old) for
                            # backward compatibility
                            if msg.type == aiohttp.WSMsgType.BINARY:
                                ostream.buffer.write(msg.data)
                                ostream.buffer.flush()
                            elif msg.type == aiohttp.WSMsgType.TEXT:
                                ostream.buffer.write(
                                    msg.data.encode("utf-8", errors="replace")
                                )
                                ostream.buffer.flush()
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                await ws.close()
                                stdin_reader_task.cancel()
                                break
                            if stdin_reader_task.done():
                                exc = stdin_reader_task.exception()
                                if exc:
                                    raise exc
            except asyncio.exceptions.CancelledError:
                return 1
            except io.UnsupportedOperation:
                print(f"io.UnsupportedOperation: {exc}")
                return 1
            except OSError as exc:
                print(f"Async connection exception: {exc}")
                return 1

            return 0

        def connect_async(
            self,
            name: str,
            readonly: bool = False,
            istream: io.TextIOBase = sys.stdin,
            ostream: io.TextIOBase = sys.stdout,
            force_str: Optional[bool] = None,
        ) -> asyncio.Task:
            """
            Connects to a serial console with the DUT in an async task.
            Basically a wrapper for connect_async_fun that returns the task.

            Args:
                name (str): Name of the serial console, example "ttyUSB0".
                readonly (bool): True to start a readonly serial connection.
                                 (Default) False for an interactive connection.
                istream (io.TextIOBase): Input stream used to send data to the DUT on the LAA.
                                         Defaults to sys.stdin.
                ostream (io.TextIOBase): Output stream used to receive data from the DUT on the LAA.
                                         Defaults to sys.stdout.
                force_str (Optional[bool]):
                                    True to exchange data as string.
                                    False to exchange data as bytes.
                                    (Default) None to automatically use the best option.
                                    Exposed mostly for testing purposes.

            Returns:
                asyncio.Task: Returns an async tasks that can be easily managed.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            loop = asyncio.get_running_loop()
            task = loop.create_task(
                self.connect_async_fun(name, readonly, istream, ostream, force_str)
            )
            return task

        def connect_pexpect(
            self,
            name: str,
            readonly: bool = False,
        ) -> laam.utils.ConnectPexpect:
            """
            Connects to a serial console with the DUT in an Pexpect object.

            Args:
                name (str): Name of the serial console, example "ttyUSB0".
                readonly (bool): True to start a readonly serial connection.
                                 (Default) False for an interactive connection.

            Returns:
                laam.utils.ConnectPexpect: Custom Pexpect object.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            serial = self.get(name)
            force_str = bool(self.laa.system.version() < "1.6")
            return laam.utils.ConnectPexpect(
                self, int(serial["port"]), readonly, force_str
            )

    class Services:
        """
        Class for monitoring system services on the LAA.

        NOTE:
        This class should NOT be instantiated directly by the user.
        Access to these functions is available only via the main LAA object.
        """

        def __init__(self, laa):
            self.session = laa.session
            self.base_uri = yarl.URL(laa.base_uri)

        def list(self) -> list:
            """
            Lists all the services on the LAA.

            Returns:
                list: Returns a list of services.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "services"
            )
            return ret.json()["items"]

        def logs(self, name: str) -> list:
            """
            Returns the logs of a specific service.

            Args:
                name (str): Name of the service.

            Returns:
                list: Returns logs information.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "services" / name / "logs"
            )
            return ret.json()

    class System:
        """
        Class for general system-level monitoring.

        NOTE:
        This class should NOT be instantiated directly by the user.
        Access to these functions is available only via the main LAA object.
        """

        def __init__(self, laa):
            self.session = laa.session
            self.base_uri = yarl.URL(laa.base_uri)

        def version(self) -> str:
            """
            Returns the OS software version on the LAA.

            Returns:
                str: Returns the version.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "system" / "version"
            )
            return ret.json()["version"]

        def fleet(self) -> dict:
            """
            Returns information of the fleet that the LAA is registered with.

            Returns:
                dict: Returns fleet information.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "system" / "fleet"
            )
            return ret.json()

        def logs(self) -> list:
            """
            Returns system logs from the LAA.

            Returns:
                list: Returns logs.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session,
                "GET",
                self.base_uri / "services" / "appliance" / "logs",
            )
            return ret.json()

    class USBs:
        """
        Class for monitoring the LAA's USB sub-system.

        NOTE:
        This class should NOT be instantiated directly by the user.
        Access to these functions is available only via the main LAA object.
        """

        def __init__(self, laa):
            self.session = laa.session
            self.base_uri = yarl.URL(laa.base_uri)

        def list(self) -> list:
            """
            Lists all the active usb connections seen by the operating system.

            Returns:
                list: Returns a list of active usb connections with bus and device details.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "devices" / "usbs"
            )
            return ret.json()["items"]

        def get(self, bus: str, device: str) -> str:
            """
            Get details of a USB device on a particular bus.

            Args:
                bus (str): Name of the bus to look into.
                device (str): Name of the device to get details of.

            Returns:
                str: Returns the details of the device.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session,
                "GET",
                self.base_uri / "devices" / "usbs" / bus / device,
                "USB not found",
            )
            return ret.text

    class Workers:
        """
        Class for monitoring workers on the LAA.

        NOTE:
        This class should NOT be instantiated directly by the user.
        Access to these functions is available only via the main LAA object.
        """

        def __init__(self, laa):
            self.session = laa.session
            self.base_uri = yarl.URL(laa.base_uri)

        def dockerfile(self, worker_id: int) -> str:
            """
            Returns the dockerfile of the specified worker.

            Args:
                worker_id (int): identifier of the worker.

            Returns:
                str: Returns a dockerfile content.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session,
                "GET",
                self.base_uri / "workers" / str(worker_id) / "dockerfile",
            )
            return ret.text

        def list(self) -> list:
            """
            Lists all the workers active on the LAA.

            Returns:
                str: Returns a list of workers with main information.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "workers"
            )
            return ret.json()["items"]

        def logs(self, worker_id: int) -> list:
            """
            Returns the logs of the specified worker.

            Args:
                worker_id (int): identifier of the worker.

            Returns:
                str: Returns logs.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "workers" / str(worker_id) / "logs"
            )
            return ret.json()

        def get(self, worker_id: int) -> dict:
            """
            Returns details of the specified worker.

            Args:
                worker_id (int): identifier of the worker.

            Returns:
                str: Returns worker details.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "workers" / str(worker_id)
            )
            return ret.json()

        def test(self, worker_id: int) -> dict:
            """
            Returns the connection status of the worker with its LAVA instance.

            Args:
                worker_id (int): identifier of the worker.

            Returns:
                str: Returns connection status.

            Raises:
                LAAError: If the LAA is offline or the request fails.
            """

            ret = laam.utils.basic_request(
                self.session, "GET", self.base_uri / "workers" / str(worker_id) / "test"
            )
            return ret.json()

    @property
    def files(self) -> Files:
        """
        Interface for remote file management on the LAA. Based on the class `Files`.
        help(laam.LAA.Files) for more info.
        """
        if self._files is None:
            self._files = self.Files(self)
        return self._files

    @property
    def laacli(self) -> LAACli:
        """
        Interface for executing laacli commands. Based on the class `LAACli`.
        help(laam.LAA.LAACli) for more info.
        """
        if self._laacli is None:
            self._laacli = self.LAACli(self)
        return self._laacli

    @property
    def network(self) -> Network:
        """
        Interface for monitoring the LAA's network interfaces. Based on the class `Network`.
        help(laam.LAA.Network) for more info.
        """
        if self._network is None:
            self._network = self.Network(self)
        return self._network

    @property
    def serials(self) -> Serials:
        """
        Interface for managing and interacting with the LAA's serial consoles. Based on the class `Serials`.
        help(laam.LAA.Serials) for more info.
        """
        if self._serials is None:
            self._serials = self.Serials(self)
        return self._serials

    @property
    def services(self) -> Services:
        """
        Interface for monitoring system services on the LAA. Based on the class `Services`.
        help(laam.LAA.Services) for more info.
        """
        if self._services is None:
            self._services = self.Services(self)
        return self._services

    @property
    def system(self) -> System:
        """
        Interface for general system-level monitoring. Based on the class `System`.
        help(laam.LAA.System) for more info.
        """
        if self._system is None:
            self._system = self.System(self)
        return self._system

    @property
    def usbs(self) -> USBs:
        """
        Interface for monitoring the LAA's USB sub-system. Based on the class `USBs`.
        help(laam.LAA.USBs) for more info.
        """
        if self._usbs is None:
            self._usbs = self.USBs(self)
        return self._usbs

    @property
    def workers(self) -> Workers:
        """
        Interface for monitoring workers on the LAA. Based on the class `Workers`.
        help(laam.LAA.Workers) for more info.
        """
        if self._workers is None:
            self._workers = self.Workers(self)
        return self._workers
