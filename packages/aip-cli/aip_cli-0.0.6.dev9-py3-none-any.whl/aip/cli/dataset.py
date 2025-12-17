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
* Copyright (C) 2024-2025 Renesas Electronics Corporation. All rights reserved.
***********************************************************************************************************************
***********************************************************************************************************************
* File Name    : aip/cli/dataset.py
* Version      : 1.04
* Product Name : AIP-CLI
* Device(s)    : NA
* Description  : AIP CLI Dataset subcommands.
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author   Description
* 1.00  17.11.2025  MSh      Initial revision.
* 1.01  17.11.2025  PKa      Casted the service model.
* 1.02  27.11.2025  PKa      Minor improvements.
* 1.03  03.12.2025  AKu      Removed Punctuation Marks.
* 1.04  04.12.2025  MSh      Added error handler.
***********************************************************************************************************************
"""

import logging
from typing import cast

from aip.cli.cli import CLIGroup
from aip.core import Client, DatasetModel
from aip.utils.error_handler import handle_errors

import click

logger = logging.getLogger(__name__)


@click.group(cls=CLIGroup, help="AIP CLI Dataset subcommand")
@click.pass_obj
def dataset(client: Client):
    """
    Dataset management commands
    Parameters:
    - client: AI Platform Client instance
    Return:
        None
    """


@dataset.command(name="list", help="List available datasets")
@click.pass_obj
@handle_errors
def list_datasets(client: Client):
    """
    Dataset management commands
    Parameters:
    - client: AI Platform Client instance
    Return:
        None
    """
    datasets = cast(DatasetModel, client.model("dataset_loader")).get_dataset_list(prefix="")
    for dataset in datasets:
        click.echo(dataset)
