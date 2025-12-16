# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT


class LAAError(Exception):
    """
    Base exception class for all LAA application errors.

    Attributes:
        message (str): The detailed error message describing the issue.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class LAAConnectionError(LAAError):
    """
    Exception class for connection errors with the LAA (like wrong IP address or device offline).

    Attributes:
        message (str): The detailed error message describing the issue.
    """

    def __init__(self):
        super().__init__(
            "Connection Error: please check if the LAA is online or that the IP address in the identity is correct"
        )


class LAAApiError(LAAError):
    """
    Exception class for all HTTP API errors from the LAA.

    Attributes:
        message (str): The detailed error message describing the issue.
        http_code (int): The relevant HTTP status code (e.g., 400, 500).
    """

    def __init__(self, message, httpexc):
        message = f"Unable to call the appliance API\nError: {message}"
        self.http_code = None
        if httpexc.response != None:
            self.http_code = httpexc.response.status_code
            message = f"{message}\nCode: {self.http_code}"
        super().__init__(message)


class LAACliError(LAAError):
    """
    Exception class for all errors when running commands of the LAA itself.

    Attributes:
        message (str): The detailed error message describing the issue.
        ret_json (dict): The error object returned from the LAA with 'stdout','sterr', and 'code'
    """

    def __init__(self, ret_json):
        self.ret_json = ret_json
        message = f"Error running the command: result {ret_json}"
        super().__init__(message)
