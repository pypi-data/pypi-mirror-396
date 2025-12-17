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
* File Name    : token.py
* Version      : 1.04
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Token hanlding for CLI authentication
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  16.10.2025  TRa     Initial revision
* 1.01  27.11.2025  PKa     Standard env variables
* 1.02  28.11.2025  PKa     Integration problems
* 1.03  28.11.2025  PKa     cleanup
* 1.04  03.12.2025  PKa     Introduction of settings
***********************************************************************************************************************
"""
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

from aip.utils import CACHE_DIR, can_launch_browser, open_page_in_browser
from aip.utils.console import console, err_console

from dateutil.tz import tzutc

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    """
    Returns UTC time
    Return:
    - datetime of now for UTC timezone
    """
    return datetime.now(tzutc())


class AIPTokenProvider:
    METHOD = "AIP"

    def __init__(self, client, time_fetcher=_utc_now):
        """
        Initializing AIP Token Provider

        Parameters:
        - client : Client to make requests to backend
        - time_fetcher : Get the time if provided. Defaults to _utc_now.
        """
        self._client = client
        self._now = time_fetcher
        self._cache_dir = CACHE_DIR
        self._oidc_url = self._client.settings.aiwb_url.strip('\"')
        self._client.oidc_url = self._oidc_url

    @property
    def _client_id(self):
        """
        Provide Client ID from environment variable or default

        Return:
        - client id: str
        """
        return self._client.settings.oidc_client_id

    @property
    def _cache_key(self):
        """
        Provide the cache key path

        Return:
        - cache key path: Path
        """
        return Path(self._cache_dir) / self._client.settings.token_file

    def _save_token(self, res: dict) -> None:
        """
        Saves the token locally
        Parameters:
        - res : response when token is requested from backend
        """
        try:
            file_content = json.dumps(res)
        except (TypeError, ValueError):
            logger.exception("Value cannot be cached, must be JSON serializable: %s", res)
            raise

        if not Path(self._cache_dir).is_dir():
            Path(self._cache_dir).mkdir(parents=True)

        with os.fdopen(os.open(self._cache_key, os.O_WRONLY | os.O_CREAT, 0o600), "w") as f:
            f.truncate()
            f.write(file_content)

    def _wait_for_token(self, device_code: str) -> None:
        """
        Process waits for token and exits on token or error or timeout

        Parameters:
        - device_code : Token provided to the device
        """
        now = _utc_now()
        while True:
            if now < _utc_now() - timedelta(seconds=180):
                logger.error("timeout for waiting device token...")
                return

            logger.debug("waiting for device token...")
            data = {
                "client_id": self._client_id,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            }

            res, err = self._client.request(f"{self._oidc_url}/api/auth/token", "POST", json=data, timeout=300)
            if not err:
                self._save_token(res)
                console.out("Successfully retrieved device token.")
                sys.exit(0)
            logger.debug("Error in retrieve token {}".format(res.get("message")))
            time.sleep(3)

    def _revoke_id_token(self) -> bool:
        """
        Requesting the backend to revoke ID token

        Return:
        - bool: Boolean value if id token is revoked
        """
        id_token = self.load_token().get("id_token")
        _, err = self._client.request(f"{self._oidc_url}/api/auth/logout", "GET", headers={"Authorization": f"Bearer {id_token}"}, timeout=300)
        return bool(not err)

    def revoke_token(self, token: str | None = None, *, revoke_id_token: bool = False) -> None:
        """
        Revoke the existing token
        Parameters:
        - token : Token if exists. Defaults to None.
        - revoke_id_token : If ID token to be revoked. Defaults to False.
        """
        if token is None:
            token = self.load_token().get("access_token")

        if revoke_id_token and not self._revoke_id_token():
            logger.error("Fail to revoke id token.")

        data = {"client_id": self._client_id, "token": token}
        res, err = self._client.request(f"{self._oidc_url}/api/auth/revoke_token", "POST", json=data, timeout=300)
        if not err:
            with os.fdopen(os.open(self._cache_key, os.O_WRONLY | os.O_CREAT, 0o600), "w") as f:
                f.truncate()
            console.out("Successfully revoked device token.")
            sys.exit(0)
        err_console.out(res.get("message", ""))
        sys.exit(1)

    def get_user_info(self) -> tuple[dict, bool]:
        """
        Fetch the user info from backend
        Return:
        - res: response from the backend
        - err: boolean value if it is an error
        """
        token = self._client.load_auth_token()
        res, err = self._client.request(f"{self._oidc_url}/api/auth/userinfo", headers={"Authorization": f"Bearer {token.get('access_token')}"}, timeout=300)
        return res, err

    def user_info(self) -> None:
        """
        Print the user info
        """
        res, err = self.get_user_info()
        if not err:
            console.print_json(json.dumps(res))
            sys.exit(0)
        err_console.out(res.get("message"))
        sys.exit(1)

    def generate_token(self) -> None:
        """
        Generates the token by launching the browser
        """
        data = {"client_id": self._client_id, "scopes": "openid profile"}
        res, err = self._client.request(f"{self._oidc_url}/api/auth/device/code", "POST", json=data, timeout=300)
        if not err:
            device_code = res.get("device_code")
            user_code = res.get("user_code")
            q = urlencode({"user_code": user_code})
            url = f"{self._oidc_url}/api/auth/cli-login?{q}"
            console.out("Attempting to automatically open the workbench authorization page in your default browser.")
            console.out(f"If the browser does not popup, you can open the following URL: {url}")
            if can_launch_browser():
                open_page_in_browser(url)
            self._wait_for_token(device_code)
        err_console.out(res.get("message", ""))
        sys.exit(1)

    def load_token(self) -> dict:
        """
        Loads token from local cache file.
        Return:
        - dict: Token dictionary if exists else empty dict
        """
        if Path(self._cache_dir).is_dir() and Path(self._cache_key).is_file():
            try:
                with open(self._cache_key, encoding="utf-8") as f:
                    token = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                return {}
            if token:
                return token

        return {}

    def validate_token(self) -> tuple[dict, bool]:
        """
        Validate the JWT token
        Return:
        - res: response from the backend
        - err: boolean value if it is an error
        """
        token = self._client.load_auth_token()
        res, err = self._client.request(f"{self._oidc_url}/api/auth/validate-token",
                                        headers={"Authorization": f"Bearer {token.get('id_token')}"}, timeout=300)
        return res, err
