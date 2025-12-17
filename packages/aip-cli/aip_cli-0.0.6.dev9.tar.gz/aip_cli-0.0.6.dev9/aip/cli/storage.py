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
* File Name    : storage.py
* Version      : 1.05
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Storage command and sub commands
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  14.11.2025  PKa     Initial revision
* 1.01  28.11.2025  PKa     Fixing integration problems
* 1.02  28.11.2025  PKa     Fixing integration problems with result
* 1.03  02.12.2025  AKu     Commands Modified
* 1.04  03.12.2025  PKa     Format entries into a table
* 1.05  04.12.2025  MSh     Added error handling
***********************************************************************************************************************
"""
import logging
from typing import cast

from aip.cli.cli import CLIGroup
from aip.core import Client, Storage
from aip.utils.error_handler import handle_errors

import click

logger = logging.getLogger(__name__)


@click.group(cls=CLIGroup, help="Cloud storage access commands")
@click.pass_obj
def storage(client: Client) -> None:
    """
    Storage management commands
    Parameters:
    - client: AI Platform Client instance
    """


@storage.command(help="List available datasets for training")
@click.pass_obj
@click.option("-o", "--output", type=str, default="text", help="Output format One of: (json, text)")
@handle_errors
def dataset_list(client: Client, output: str) -> None:
    """
    Dataset management commands
    Parameters:
    - client: AI Platform Client instance
    - output : str: Type of the output
    Return:
        None
    """
    cast(Storage, client.model("storage", output=output)).get_dataset_list()


@storage.command(help="Shows the media available for inference")
@click.pass_obj
@click.option("-o", "--output", type=str, default="text", help="Output format One of: (json, text)")
@handle_errors
def media_list(client: Client, output: str) -> None:
    """
    List available media

    Parameters:
    - client : AI Platform Client instance
    - output : str: Type of the output
    """
    cast(Storage, client.model("storage", output=output)).get_dataset_list(user_specific=True)


@storage.command(help="Upload data/model/media (Data and model are not available in this release)")
@click.pass_obj
@click.option("--path", type=str, required=True, help="Path of the file to be uploaded")
@click.option("--data-type", type=click.Choice(["data", "model", "media"]), required=True, help="Type of the file to be uploaded")
@click.option("-o", "--output", type=str, default="json", help="Output format One of: (json, text)")
@handle_errors
def upload(client: Client, path, data_type: str, output: str) -> None:
    """
    Upload data/model/media to storage
    Parameters:
    - client : AI Platform Client instance
    - path : str: Path of the file to be uploaded
    - data_type : str: Type of the file to be uploaded
    - output : str: Type of the output
    """
    cast(Storage, client.model("storage", output=output)).upload(path, data_type)


