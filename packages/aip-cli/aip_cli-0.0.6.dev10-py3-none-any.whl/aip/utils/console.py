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
* File Name    : console.py
* Version      : 1.00
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Console theme for CLI
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  16.10.2025  TRa     Initial revision
***********************************************************************************************************************
"""
from contextlib import contextmanager

from rich.console import Console
from rich.theme import Theme

theme = Theme({"repr.str": "none", "repr.number": "none"})

console = Console(theme=theme)
err_console = Console(stderr=True, style="bold red")


@contextmanager
def show_loading_status(message: str = "Processing... Please wait...", spinner: str = "line"):
    """
    Context manager to show a loading status with a spinner in the console.
    Parameters:
    - message: (str): The message to display alongside the spinner.
    - spinner: (str): The type of spinner to use.
    Yields:
    - None
    """
    with console.status(f"[blue]{message}[/blue]", spinner=spinner):
        yield
