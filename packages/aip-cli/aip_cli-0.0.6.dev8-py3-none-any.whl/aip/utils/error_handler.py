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
* File Name    : error_handler.py
* Version      : 1.00
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Console theme for CLI
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  04.12.2025  MSh     Initial revision
******
"""
import functools
import logging
import sys
import traceback
from collections.abc import Callable

from aip.utils.console import console

import click

logger = logging.getLogger(__name__)


def handle_errors(func: Callable) -> Callable:
    """
    Decorator to handle errors in Click commands.
    Shows clean error messages by default, full tracebacks in debug mode.
    Parameters:
    - func: Callable: The function to wrap.
    Return:
    - Callable: The wrapped function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function to handle errors.
        Parameters:
        - args: tuple: Positional arguments for the wrapped function.
        - kwargs: dict: Keyword arguments for the wrapped function.
        Return:
        - Any: The return value of the wrapped function.
        """
        console.print("[dim]╭─ 🛡️  Error handler active ─╮[/dim]")
        try:
            return func(*args, **kwargs)
        except click.ClickException:
            raise
        except KeyboardInterrupt:
            console.print("\n[yellow]Aborted![/yellow]", style="bold")
            sys.exit(130)
        except Exception as e:
            console.print(f"[red bold]Error:[/red bold] {e}")

            if logger.isEnabledFor(logging.DEBUG):
                console.print("\n[dim]Traceback:[/dim]")
                traceback.print_exc()
            else:
                console.print("[dim]Run with --debug for full traceback[/dim]")

            sys.exit(1)

    return wrapper  # type: ignore
