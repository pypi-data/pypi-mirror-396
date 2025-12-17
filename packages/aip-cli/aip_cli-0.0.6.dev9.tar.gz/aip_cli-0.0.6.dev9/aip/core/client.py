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
* File Name    : client.py
* Version      : 1.03
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Definition of client to store configuration
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  16.10.2025  TRa     Initial revision
* 1.01  28.11.2025  Msh     Updated urls to BE
* 1.02  28.11.2025  HRh     JWT token decode
* 1.03  03.12.2025  PKa     Introduction of settings
***********************************************************************************************************************
"""
import base64
import json
import logging
from typing import Any
from urllib.parse import urlparse

from aip.settings import Settings

import requests

from .exception import AuthException
from .model import ServiceModel
from .token import AIPTokenProvider

logger = logging.getLogger(__name__)


class Client:
    """
    A aip client stores configuration state and allows you to create service
    clients and resources.
    """

    def __init__(
        self,
        *,
        verify: bool = True,
        settings: Settings
    ) -> None:
        """
        Create a new Session Script

        Parameters:
        - log_level : Log level to be set. Defaults to "info".
        - verify : Boolean value to determine if verification is necessary. Defaults to True.
        """
        self._session = requests.Session()
        self._verify = verify
        self.settings = settings
        self._tenant = self.settings.tenant
        self._access_key = self.settings.access_key
        self._cloud = self.settings.cloud
        self._token_provider = self.settings.token_provider
        if self._access_key:
            # AIP Personal access key
            auth_token = f"{self._access_key}"
        else:
            # OIDC Device flow
            token = self.load_auth_token()
            # for AIP Service, using id token
            auth_token = f"{token.get('id_token')}"
        self._log_level = self.settings.log_level
        aiwb_url = urlparse(self.settings.aiwb_url)
        aip_url = urlparse(self.settings.url)
        self.aiwb_domain = self._get_domain(aiwb_url)
        self._aip_domain = self._get_domain(aip_url)
        self._q_domain = self._get_domain(aip_url)

        self._session.cookies.set("access-token", auth_token, domain=self.aiwb_domain)
        self._session.cookies.set("access-token", auth_token, domain=self._q_domain)

    @property
    def token_provider(self) -> AIPTokenProvider | None:
        """
        Fetches the token provider based on the attribute

        Return:
        - AIP Token Privider handler is returned
        """
        if self._token_provider == "aip":  # noqa: S105
            return AIPTokenProvider(self)
        return None

    @property
    def aiwb_url(self) -> str:
        """
        Fetches the backend URL from the environment

        Return:
        - str value of the URL
        """
        return str(self.settings.aiwb_url)

    @property
    def aip_url(self) -> str:
        """
        Fetches the AIP backend URL from the environment

        Return:
        - str value of the URL
        """
        return str(self.settings.url)

    @staticmethod
    def _get_domain(url) -> str:
        """
        Creates a domain based on url, port, scheme

        Parameters:
        - url : str value of the URL

        Return:
        - str value of the domain
        """
        if url.port:
            domain = f"{url.hostname}:{url.port}"
        elif url.scheme == "https":
            domain = f"{url.hostname}:443"
        elif url.scheme == "http":
            domain = f"{url.hostname}:80"
        else:
            domain = url.hostname

        return domain

    def generate_auth_token(self) -> Any:
        """
        Selects the token provider's generate token method

        Return:
        - Return the method to generate token from token_provider
        """
        if self.token_provider:
            return self.token_provider.generate_token()
        raise AuthException("No token provider configured to generate token.")

    def revoke_auth_token(self, token=None, *, revoke_id_token=True) -> Any:
        """
        Selects the token provider's revoke token method

        Parameters:
        - token : Token provided to revoke. Defaults to None.
        - revoke_id_token : boolean value if id token is needed to be revoked. Defaults to True.

        Return:
        - Return the method to revoke token from token_provider
        """
        if self.token_provider:
            return self.token_provider.revoke_token(token, revoke_id_token=revoke_id_token)
        raise AuthException("No token provider configured to revoke token.")

    def load_auth_token(self) -> dict:
        """
        Selects the token provider's load token method

        Return:
        - Return the method to load token from token_provider
        """
        if self.token_provider:
            return self.token_provider.load_token()
        raise AuthException("No token provider configured to load token.")


    def _error_message(self, error_response: requests.Response) -> dict:
        """
        Tries to extract an error message from an HTTP response.

        Attempts to parse the response body as JSON and extract common error fields.
        Falls back to using the raw response text if the body is not valid JSON or does not contain expected fields.

        Parameters:
        - error_response: (Response): The HTTP response object returned by the `requests` library.

        Return:
        - dict: A human-readable error message in the format: "<HTTP Status Phrase>: <Error Message>"
        """
        error_message = "Unknown error"

        try:
            error_json = error_response.json()
            logger.debug(json.dumps(error_json, indent=4))
        except json.JSONDecodeError as exc:
            logger.debug("Failed to decode JSON response. %s", exc)
            logger.debug("Error text: %s", error_response.text)
        else:
            # Since the return error response is not consistent from backend,
            # we are guessing the error message here.
            if "message" in error_json:
                error_message = error_json.get("message")
            elif "error_description" in error_json:
                error_message = error_json.get("error_description")
            elif isinstance(error_dict := error_json.get("error"), dict):
                error_message = error_dict.get("message", "Unknown error")
            elif isinstance(error_text := error_json.get("error"), str):
                error_message = error_text

        return {
            "success": False,
            "message": error_message.capitalize().rstrip("."),
            "code": error_response.status_code,
        }

    def _response(self, response: requests.Response) -> tuple[dict, bool]:
        """
        Parses the response form backend and structures the resposne

        Parameters:
        - response : Full response to be parsed

        Return:
        - error message method
        """
        if 200 <= response.status_code < 300:
            try:
                res = response.json()
            except json.JSONDecodeError:
                res = {"success": True, "message": response.text}
            return res, False
        return self._error_message(response), True

    def request(self, url, method="get", *args, **kwargs) -> tuple[dict, bool]:
        """
        Sends API request using on url, method, args, kwargs

        Parameters:
        - url : string value of the URL
        - method : Type of the API method. Defaults to "get".

        Return:
        - returns the Response
        """
        if not self._verify:
            kwargs["verify"] = False
        try:
            method = method.lower()
            if method == "post":
                res = self._session.post(url, *args, **kwargs)
            elif method == "put":
                res = self._session.put(url, *args, **kwargs)
            elif method == "delete":
                res = self._session.delete(url, *args, **kwargs)
            elif method == "patch":
                res = self._session.patch(url, *args, **kwargs)
            else:
                res = self._session.get(url, **kwargs)
            return self._response(res)
        except requests.exceptions.HTTPError as e:
            logger.debug(f"HTTP Error: {e}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.debug(f"Connection Error: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.debug(f"Timeout Error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.debug(f"Request Exception: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.debug(f"JSON Decode Exception: {e}")
            raise

    def user_info(self) -> dict | None:
        """
        Stores the user info provided the access key exists

        Return:
        - Returns empty if there is no access key
        """
        if not self.token_provider:
            raise AuthException("No token provider configured to get user info.")
        if self._access_key:
            # TODO: get user info for personal access key
            return {}
        self.token_provider.user_info()
        return None

    def get_user_schema(self) -> str | None:
        """
        Fetches the user schema of the user from token provider

        Return:
        - str value of the schema
        """
        if not self.token_provider:
            raise AuthException("No token provider configured to get user schema.")
        user_info, err = self.token_provider.get_user_info()
        if err:
            logger.exception("Unable to retrieve user info. %s", err)
            return None

        return user_info.get("schema_name")

    def get_user_sub(self) -> str | None:
        """
        Fetches the user sub from the token (decoded locally)

        Return:
        - str value of the user sub/email
        """
        token = self.load_auth_token()
        id_token = token.get('id_token', '')
        if not id_token:
            logger.exception("No id_token found in auth token")
            return None

        try:
            payload = id_token.split('.')[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            return decoded.get("sub") or decoded.get("email")
        except Exception as e:
            logger.exception(f"Failed to decode token: {e!s}")  # noqa: TRY401
            return None

    def model(self, service_name=None, *args, **kwargs) -> ServiceModel | None:
        """
        Provides the service model by loading the auth token

        Parameters:
        - service_name : str value of the service name requested by user. Defaults to None.

        Return:
        - returns an object of service model with service name
        """
        if self._access_key:
            # AIP Personal access key
            auth_token = f"{self._access_key}"
        else:
            # OIDC Device flow
            token = self.load_auth_token()
            # for AIP Service, using id token
            auth_token = f"{token.get('id_token')}"
        service_model = None
        for cls in ServiceModel.__subclasses__():
            if cls.is_service(service_name):
                service_model = cls
        self._session.cookies.set("access-token", auth_token)
        if service_model is not None:
            return service_model(*args, client=self, **kwargs)
        return None

    def require_auth(self):
        """
        Check user is authenticated or not
        """
        if not self.token_provider:
            raise AuthException("No token provider configured to validate token.")
        res, _ = self.token_provider.validate_token()
        if not res.get("valid"):
            raise AuthException("Access denied.\n"
                                "Details: The request requires valid authentication credentials. Please run 'aip login' to establish a session.")
