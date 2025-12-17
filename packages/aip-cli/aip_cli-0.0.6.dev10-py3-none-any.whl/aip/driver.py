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
* File Name    : driver.py
* Version      : 1.02
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : AIP Cli entry point.
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  16.10.2025  TRa     Initial revision
* 1.01  03.12.2025  PKa     Introduction of settings
* 1.02  04.12.2025  MSh     Added error handling
***********************************************************************************************************************
"""

import logging
import sys
import traceback

from aip.cli import cli_group
from aip.settings import get_settings
from aip.utils.console import console

import click
from rich.logging import RichHandler


def _extract_flags(argv: list[str]) -> tuple[int, list[str]]:
    """
    Count and strip -v/--verbose flags anywhere in argv.
    Parameters:
    - argv: (list[str]): The list of command-line arguments.
    Return:
    - tuple[int, list[str]]: A tuple containing the verbosity count and the remaining arguments.
    """
    count = 0
    rest: list[str] = []
    for tok in argv:
        if tok in ("-v", "--verbose"):
            count += 1
            continue
        rest.append(tok)
        if tok == "--debug":
            count += 2
            continue
    return count, rest


def driver() -> None:
    """
    Entry point for AIP CLI.
    Sets up logging based on verbosity flags and invokes the CLI group.
    """
    # Pre-parse verbosity flags so users can put them anywhere (before/after subcommands)
    vcount, remaining = _extract_flags(sys.argv[1:])
    sys.argv = [sys.argv[0], *remaining]
    # if vcount == 2 then debug, if vcount == 1 then verbose, else default to warning
    level = logging.WARNING
    settings = get_settings()
    if vcount >= 2 or settings.debug:
        level = logging.DEBUG
    elif vcount == 1 or settings.verbose:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, show_path=False)],
    )

    try:
        cli_group(standalone_mode=False)
    except click.exceptions.Exit:
        pass
    except click.ClickException as e:
        e.show()
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Aborted![/yellow]", style="bold")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red bold]Error:[/red bold] {e}")

        if level == logging.DEBUG:
            console.print("\n[dim]Traceback:[/dim]")
            traceback.print_exc()

        sys.exit(1)
