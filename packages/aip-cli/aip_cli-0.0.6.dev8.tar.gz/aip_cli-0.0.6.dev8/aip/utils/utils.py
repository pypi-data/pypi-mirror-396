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
* File Name    : utils.py
* Version      : 1.03
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Utils for CLI
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  16.10.2025  TRa     Initial revision
* 1.01  18.11.2025  PKa     Typo fix in suppress browser env variable
* 1.02  27.11.2025  PKa     Standard env variables
* 1.03  03.12.2025  PKa     Introduction of settings
***********************************************************************************************************************
"""
import platform
import shutil
import subprocess
import webbrowser
from pathlib import Path
from typing import Any

from aip.settings import get_settings

settings = get_settings()
if settings.cache_dir:
    CACHE_DIR = Path(settings.cache_dir).expanduser()
else:
    CACHE_DIR = Path("~/.aip/cache").expanduser()
SUPPRESS_BROWSER = settings.suppress_browser


def _get_platform_info() -> tuple[str, str]:
    """
    Retrieves the platform in which CLI is being used.
    Return:
    - tuple[str, str]: (system, release) both in lowercase.
    """
    uname = platform.uname()
    return uname.system.lower(), uname.release.lower()


def can_launch_browser() -> bool:
    """
    Determines if a web browser can be launched on the current platform.
    Return:
    - bool: True if a browser can be launched, False otherwise.
    """
    _, _ = _get_platform_info()

    # If user prefers to suppress the browser
    if SUPPRESS_BROWSER:
        return False

    # Using webbrowser to launch a browser is the preferred way.
    try:
        webbrowser.get()
    except webbrowser.Error:
        # Don't worry. We may still try powershell.exe.
        return False
    return True


def is_windows():
    """
    Return True if the platform is Windows
    Return:
    - bool: True if the platform is Windows else False
    """
    platform_name, _ = _get_platform_info()
    return platform_name == "windows"


def is_wsl():
    """
    Return True if the platform is WSL
    Return:
    - bool: True if the platform is WSL else False
    """
    platform_name, release = _get_platform_info()
    # "Official" way of detecting WSL: https://github.com/Microsoft/WSL/issues/423#issuecomment-221627364
    # Run `uname -a` to get 'release' without python
    #   - WSL 1: '4.4.0-19041-Microsoft'
    #   - WSL 2: '4.19.128-microsoft-standard'
    return platform_name == "linux" and "microsoft" in release


def open_page_in_browser(url: str) -> Any:
    """
    Opens the specified URL in the default web browser for the current platform.
    Parameters:
    - url: str :  The URL to open.
    Return:
    - Any: The result of the browser launch operation, which may be a subprocess.Popen object (on WSL or macOS)
             or a boolean indicating success (from webbrowser.open).
    Notes:
    - On WSL, attempts to use powershell.exe to launch the browser.
    - On macOS, uses the 'open' command.
    - On other platforms, uses Python's webbrowser module.
    - webbrowser.open returns True if the browser is successfully opened, False otherwise.
    - 2 means: open in a new tab, if possible.
    """
    platform_name, _ = _get_platform_info()
    if is_wsl():  # windows 10 linux subsystem
        try:
            # https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe
            # Ampersand (&) should be quoted
            powershell_path = shutil.which("powershell.exe")
            if powershell_path:
                return subprocess.Popen(  # noqa: S603
                    [
                        powershell_path,
                        "-NoProfile",
                        "-Command",
                        f'Start-Process "{url}"',
                    ]
                ).wait()
        except OSError:  # WSL might be too old  # FileNotFoundError introduced in Python 3
            pass
    elif platform_name == "darwin":
        # handle 2 things:
        # a. On OSX sierra, 'python -m webbrowser -t <url>' emits out "execution error: <url> doesn't
        #    understand the "open location" message"
        # b. Python 2.x can't sniff out the default browser
        open_path = shutil.which("open")
        if open_path:
            return subprocess.Popen([open_path, url])  # noqa: S603
        raise FileNotFoundError("'open' executable not found in PATH")
    try:
        return webbrowser.open(url, new=2)  # 2 means: open in a new tab, if possible
    except TypeError:  # See https://bugs.python.org/msg322439
        return webbrowser.open(url, new=2)
