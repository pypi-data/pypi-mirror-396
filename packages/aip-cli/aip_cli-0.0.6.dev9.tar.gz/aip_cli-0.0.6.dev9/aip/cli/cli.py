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
* File Name    : cli.py
* Version      : 1.06
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Base of CLI with basic commands
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  16.10.2025  TRa     Initial revision
* 1.01  17.11.2025  MSh     Added Dataset command
* 1.02  17.11.2025  PKa     Fixed the merge request check
* 1.03  27.11.2025  Sam     Added description to help command
* 1.04  27.11.2025  PKa     Added storage command
* 1.05  03.12.2025  AKu     Command Formats changed
* 1.06  03.12.2025  PKa     Introduction of settings
***********************************************************************************************************************
"""

import importlib
import logging

import aip
from aip.core import Client
from aip.settings import Settings, get_settings

import click
from pydantic import ValidationError


class CLIGroup(click.Group):
    """Custom Click Group to support lazy loading of subcommands"""

    def __init__(self, *args, lazy_subcommands=None, **kwargs):
        """
        Initialize the CLIGroup with lazy subcommands

        Parameters:
        - lazy_subcommands (dict): A mapping of command names to their import paths
        """
        super().__init__(*args, **kwargs)
        self.lazy_subcommands = lazy_subcommands or {}

    def list_commands(self, ctx: click.Context) -> list[str]:
        """
        Lists all commands, including lazy loaded ones

        Parameters:
        - ctx : Context

        Return:
        - list[str]: List of command names
        """
        base = super().list_commands(ctx)
        lazy = sorted(self.lazy_subcommands.keys())
        return base + lazy

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        """
        Gets a command, loading it lazily if necessary

        Parameters:
        - ctx : Context
        - cmd_name : str: Name of the command to retrieve

        Return:
        - click.Command | None: The command object or None if not found
        """
        if cmd_name in self.lazy_subcommands:
            return self._lazy_load(cmd_name)
        return super().get_command(ctx, cmd_name)

    def _lazy_load(self, cmd_name: str) -> click.Command:
        """
        Lazily loads a command by its name

        Parameters:
        - cmd_name : str: Name of the command to load
        Return:
        - click.Command: The loaded command object
        """
        # lazily loading a command, first get the module name and attribute name
        import_path = self.lazy_subcommands[cmd_name]
        modname, cmd_object_name = import_path.rsplit(".", 1)
        # do the import
        mod = importlib.import_module(modname)
        # get the Command object from that module
        cmd_object = getattr(mod, cmd_object_name)
        # check the result to make debugging easier
        if not isinstance(cmd_object, click.Command):
            raise TypeError(
                f"Lazy loading of {import_path} failed by returning a non-command object"
            )
        return cmd_object

    def format_commands(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """
        Formats the commands for help output, separating commands and subcommands
        Parameters:
        - ctx : Context
        - formatter : HelpFormatter
        """
        command_list = []
        subcommand_list = []

        commands = self.list_commands(ctx)
        if not commands:
            return

        # Find the length of the longest command name
        max_len = max(len(cmd) for cmd in commands)
        total_width = max_len + 12

        for cmd_name in commands:
            cmd = self.get_command(ctx, cmd_name)
            if cmd is None or cmd.hidden:
                continue
            help_text = cmd.get_short_help_str().strip()

            padded = cmd_name.ljust(total_width)
            if isinstance(cmd, click.Group):
                if not help_text:
                    subcommand_list.append((cmd_name, ""))
                else:
                    subcommand_list.append((f"{padded}:", f"{help_text}"))
            elif not help_text:
                command_list.append((cmd_name, ""))
            else:
                command_list.append((f"{padded}:", f"{help_text}"))

        if command_list:
            with formatter.section("Admin commands"):
                formatter.write_dl(command_list, col_spacing=1)

        if subcommand_list:
            with formatter.section("Functional commands"):
                formatter.write_dl(subcommand_list, col_spacing=1)


@click.group(
    cls=CLIGroup,
    lazy_subcommands={
        "login": "aip.cli.auth.login",
        "logout": "aip.cli.auth.logout",
        "whoami": "aip.cli.auth.whoami",
        "q": "aip.cli.q.q",
        "mlops": "aip.cli.mlops.mlops",
        "storage": "aip.cli.storage.storage",
    },
    help=(
        "Renesas AI Platform CLI\n\nThe Renesas AI Platform CLI is a command-line interface tool "
        "from Renesas that enables users to configure and execute machine learning workflows, particularly "
        "for training and deploying computer vision models"
    ),
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity for users to see more output",
)
@click.option(
    "--debug",
    count=True,
    help="Add detailed information for developers to debug issues",
)
@click.option(
    "--insecure",
    count=True,
    help="Disable SSL verification",
)
@click.pass_context
def cli_group(ctx: click.Context, verbose: int, debug: int, insecure: int) -> None:
    """
    Main CLI group function
    Parameters:
    - ctx : Context
    - verbose : int: Verbosity level
    - debug : int: Debug level
    - insecure : int: Insecure level
    """
    # Only elevate logging if -v provided here; otherwise keep level set by main()
    if verbose and verbose >= 1:
        logging.getLogger().setLevel(logging.INFO)
    if debug and debug >= 1:
        logging.getLogger().setLevel(logging.DEBUG)
    verify = True
    if insecure >= 1:
        verify = False

    try:
        settings = get_settings()
    except ValidationError as e:
        click.echo(f"Configuration error:\n{e}", err=True)
        raise click.Abort() from e
    ctx.obj = Client(
        verify=verify,
        settings=settings,
    )



@cli_group.command(help="Renesas AI Platform CLI version")
def version() -> None:
    """
    Version command to show the current version of the CLI
    """
    print(aip.__version__)  # type: ignore



# Hidden/internal command
@cli_group.command(name="print-nonprod", hidden=True)
@click.pass_obj
def print_nonprod(settings: Client) -> None:
    """
    Internal/QA: Print resolved non-prod settings in a redacted form.
    Exits if env != nonprod.
    Parameters:
    - settings: Client object
    """
    s: Settings = settings.settings
    if s.env != "nonprod":
        click.echo("This command is available only in nonprod environment.", err=True)
        raise click.Abort()

    payload = s.to_public_dict()

    click.echo("Resolved non-prod settings:")
    for k, v in payload.items():
        click.echo(f"- {k}: {v}")
