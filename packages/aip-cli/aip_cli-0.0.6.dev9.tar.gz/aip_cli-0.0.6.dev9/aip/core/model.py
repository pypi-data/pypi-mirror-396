"""
***********************************************************************************************************************
* DISCLAIMER
* This software is supplied by Renesas Electronics Corporation and is only intended for use with Renesas products. No
* other uses are authorized. This software is owned by Renesas Electronics Corporation and is protected under all
* applicable laws, including copyright laws.
* THIS SOFTWARE IS PROVIDED "AS IS" AND RENESAS MAKES NO WARRANTIES REGARDING
* THIS SOFTWARE, WHETHER EXPRESS, IMPLIED OR STATUTORY, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. ALL SUCH WARRANTIES ARE EXPRESSLY DISCLAIMED. TO THE MAXIMUM
* EXTENT PERMITTED NOT PROHIBITED BY LAW, NEITHER RENESAS ELECTRONICS CORPORATION NOR ANY OF ITS AFFILIATED COMPANIES
* SHALL BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES FOR ANY REASON RELATED TO THIS
* SOFTWARE, EVEN IF RENESAS OR ITS AFFILIATES HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
* Renesas reserves the right, without notice, to make changes to this software and to discontinue the availability of
* this software. By using this software, you agree to the additional terms and conditions found by accessing the
* following link:
* http://www.renesas.com/disclaimer
*
* Copyright (C) 2025 Renesas Electronics Corporation. All rights reserved.
***********************************************************************************************************************
***********************************************************************************************************************
* File Name    : model.py
* Version      : 1.02
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Base service model
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  16.10.2025  TRa     Initial revision
* 1.01  27.11.2025  PKa     Modified urls
* 1.02  03.12.2025  PKa     Introduction of settings
***********************************************************************************************************************
"""
import json
import sys
from abc import ABCMeta
from typing import Any

from aip.utils.console import console, err_console

from rich.pretty import Pretty


class ServiceModel(metaclass=ABCMeta):  # noqa: B024
    service_name = None

    def __init__(self, client, output):
        """
        Base Service Model Initialization

        Parameters:
        - client : Client to make requests to backend
        - output : Output format (text/json)
        """
        self._client = client
        self._url = self._client.settings.url
        self._aiwb_url = self._client.settings.aiwb_url
        # self._env = self._derive_env_from_url(self._url)  # noqa: ERA001
        self.output = output

    def get_organization_name(self) -> Any:
        """
        Fetches the organization name
        Return:
        - user_schema: Any = Schema of the Organization
        """
        user_schema = self._client.get_user_schema()
        if not user_schema:
            self.stderr("Unable to retrieve user's organization name")

        return user_schema

    def get_current_user_sub(self) -> Any:
        """
        Fetches the Organization name of the current User
        Return:
        - user_schema: Any = Schema of the Organization
        """
        user_sub = self._client.get_user_sub()
        if not user_sub:
            self.stderr("Unable to retrieve user's organization name")

        return user_sub


    @staticmethod
    def _derive_env_from_url(url) -> str:
        """
        Derive the environment from the URL.
        Parameters:
        - url : URL string to derive environment from
        Return:
        - str: environment name
        """
        url_lower = url.lower()
        if "ai-d." in url_lower or "localhost" in url_lower:
            return "dev"
        if "ai-t." in url_lower:
            return "test"
        if "ai-s." in url_lower:
            return "stag"
        if "ai." in url_lower:
            return "prod"
        raise ValueError("Environment not specified in URL")

    @staticmethod
    def _console(data, output="text", *, stderr=False, pretty=True) -> None:
        """
        Prints the messages onto the user window
        Parameters:
        - data : Data to be dumped
        - output : Existing data that is to be printed. Defaults to "text".
        - stderr : Boolean to specify if the output is error. Defaults to False.
        - pretty : Boolean to specify if the print should be pretty. Defaults to True.
        """
        _console = console
        if stderr:
            _console = err_console
            pretty = False
            if isinstance(data, dict) and output != "json":
                data = data.get("message")
        if output == "json":
            try:
                data = json.dumps(data)
            except (TypeError, ValueError):
                _console = _console.print
                data = Pretty(data, indent_guides=False, expand_all=True)
            else:
                _console = _console.print_json
        elif output == "text":
            _console = _console.out
            pretty = False
        else:
            _console = _console.print
            if pretty:
                data = Pretty(data, indent_guides=False, expand_all=True)
        _console(data)  # type: ignore

    def stdout(self, data) -> None:
        """
        To print as standard response
        Parameters:
        - data : Data that is supposed to be printed
        """
        self._console(data, self.output)
        sys.exit(0)

    def stderr(self, data) -> None:
        """
        To print Error response
        Parameters:
        - data : Data that is supposed to be printed
        """
        self._console(data, self.output, stderr=True)
        sys.exit(1)

    def process(self, path, method="GET", **kwargs) -> None:
        """
        To send an API request to backend and print the response
        Parameters:
        - path : endpoint to be called.
        - method : Method of API request. Defaults to "GET".
        """
        res, err = self._client.request(f"{self._url}/{path}", method, **kwargs)
        if err:
            self.stderr(res)
        self.stdout(res)

    @classmethod
    def is_service(cls, service_name) -> bool:
        """
        Check if the given service name matches the service model's name.
        Parameters:
        - cls: Class reference
        - service_name : Name of the service to be checked
        Return:
        - bool: True if the service names match, False otherwise.
        """
        if not cls.service_name:
            raise TypeError(
                "Subclass of ServiceModel needs to have the `service_name` class attribute."
            )
        return service_name == cls.service_name
