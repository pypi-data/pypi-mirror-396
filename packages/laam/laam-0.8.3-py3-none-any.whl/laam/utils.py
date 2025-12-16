# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import asyncio
import contextlib
import enum
import io
import os
import queue
import sys
import termios
import threading
import time
import tty
from contextlib import contextmanager

import pexpect
import requests
import websocket

import laam.exceptions

#############
# Constants #
#############


class Color(enum.Enum):
    green = "\033[1;32m"
    grey = "\033[0;90m"
    red = "\033[1;31m"
    yellow = "\033[1;33m"
    end = "\033[0m"


PRIORITIES = {
    3: Color.red.value,
    4: Color.red.value,
    5: Color.yellow.value,
    7: Color.grey.value,
}

###########
# Helpers #
###########


def get_color(priority):
    return PRIORITIES.get(priority, "")


def print_error(ret, expected=200) -> bool:
    if ret.status_code == expected:
        return False

    print("Unable to call the appliance API", file=sys.stderr)
    print(f"Code: {ret.status_code}", file=sys.stderr)
    with contextlib.suppress(Exception):
        print(f"Error: {ret.json()['detail']}", file=sys.stderr)
    return True


def basic_request(session, method, url, not_found_message=None, **kwargs):
    try:
        ret = session.request(method, url, **kwargs)
        ret.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        message = "HTTP request error"
        if (
            not_found_message != None
            and exc.response != None
            and exc.response.status_code == 404
        ):
            message = not_found_message
        raise laam.exceptions.LAAApiError(message, exc) from exc
    except requests.exceptions.ConnectionError as exc:
        raise laam.exceptions.LAAConnectionError() from exc
    return ret


class ConnectPexpect(pexpect.spawn):
    def __init__(
        self, laa_serial, port: int, readonly: bool = False, force_str: bool = False
    ):

        # LAA  <->  ws  <->  msg_queue  <->  pexpect  <->  User/Developer

        self.ws_url = f"{laa_serial.ws_url}?port={port}"
        if readonly:
            self.ws_url += "&readonly=True"
        self.ws_headers = laa_serial.ws_headers
        self.force_str = force_str

        self.msg_queue = queue.Queue()
        self.connected = False
        self.wsocket = self._setup_ws()

        self.ws_thread = threading.Thread(
            target=self.wsocket.run_forever,
            daemon=True,
            kwargs={"ping_interval": 30, "ping_timeout": 10},
        )
        self.ws_thread.start()

        # Making sure that the websocket gets connected before running read_nonblocking
        while not self.connected:
            time.sleep(0.01)

        # Setting the maxread size to 1 will turn off buffering
        super().__init__(None, maxread=1, encoding="utf-8")

    def _setup_ws(self):
        def _on_message(ws, message):
            self.msg_queue.put(message)

        def _on_error(ws, error):
            print(f"[WS] Error: {error}")

        def _on_open(ws):
            self.connected = True
            print("[WS] connected")

        def _on_close(ws, close_status_code, close_msg):
            self.connected = False
            print(f"[WS] disconnected")

        ws = websocket.WebSocketApp(
            self.ws_url,
            header=self.ws_headers,
            on_message=_on_message,
            on_error=_on_error,
            on_close=_on_close,
            on_open=_on_open,
        )
        websocket.setdefaulttimeout(5)
        return ws

    def read_nonblocking(self, size=1, timeout=0.1):
        if not self.connected:
            raise Exception("Read operation on closed WS connection.")

        if timeout == -1:
            timeout = self.timeout

        try:
            # Ingore the 'size' and return any and all available data.
            # An internal buffer can be added for returning the exact size.
            data = self.msg_queue.get(timeout=timeout)
            if isinstance(data, bytes):
                data = data.decode("utf-8", errors="replace")
            return data
        except queue.Empty:
            raise pexpect.TIMEOUT("Timeout exceeded.")

    def send(self, data):
        if not self.connected:
            raise Exception("Send operation on closed WS connection.")

        if self.force_str:
            self.wsocket.send(data)
        else:
            self.wsocket.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
        return len(data)

    def isalive(self):
        return self.connected

    def close(self, force=True):
        if self.wsocket:
            self.connected = False
            self.wsocket.close()
            self.wsocket = None

        if self.ws_thread:
            self.ws_thread.join()
            self.ws_thread = None

    def wait(self):
        while self.isalive():
            time.sleep(0.1)

    def kill(self, sig=None):
        self.close()

    def terminate(self, force=False):
        self.close()

    def __del__(self):
        self.close()
        if hasattr(super(), "__del__"):
            super().__del__()


async def stdin_reader(ws, istream: io.TextIOBase, force_str=False):
    try:
        with stream_as_raw(istream) as withpipe:
            if withpipe:
                reader = asyncio.StreamReader()
                protocol = asyncio.StreamReaderProtocol(reader)
                loop = asyncio.get_event_loop()
                await loop.connect_read_pipe(lambda: protocol, istream)
            else:
                reader = istream

            while True:
                try:
                    if ws.closed:
                        return
                    if withpipe:
                        c = await reader.read(1)
                    else:
                        c = await asyncio.to_thread(reader.read)

                    if isinstance(c, bytes) and c == b"":
                        await asyncio.sleep(0.1)
                        continue
                    if isinstance(c, str) and c == "":
                        await asyncio.sleep(0.1)
                        continue

                    # Use str for backward compatibility but default
                    # to bytes that are safer.
                    if force_str:
                        if isinstance(c, bytes):
                            c = c.decode("utf-8")
                        await ws.send_str(c)
                    else:
                        if isinstance(c, str):
                            c = c.encode("utf-8")
                        await ws.send_bytes(c)
                except Exception as exc:
                    print(f"Error reading {exc}")
    except NameError:
        raise
    except asyncio.exceptions.CancelledError:
        raise
    except io.UnsupportedOperation:
        raise
    except Exception as exc:
        print(f"Error in reader {exc}")
        return


@contextmanager
def stream_as_raw(stream):

    try:
        fd = stream.fileno()
        is_tty = os.isatty(fd)
        has_fileno = True
    except (AttributeError, io.UnsupportedOperation):
        is_tty = False
        has_fileno = False

    if is_tty:
        original_stty = termios.tcgetattr(stream)
        try:
            tty.setcbreak(stream)
            yield True
        finally:
            termios.tcsetattr(stream, termios.TCSANOW, original_stty)
    else:
        yield has_fileno
