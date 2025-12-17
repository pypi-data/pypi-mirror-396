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
* File Name    : auth.py
* Version      : 1.02
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Authorization commands
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  16.10.2025  TRa     Initial revision
* 1.01  03.12.2025  AKu     Help Commands modified
* 1.02  04.12.2025  MSh     Added error handler
***********************************************************************************************************************
"""
import logging

from aip.core import Client
from aip.utils.error_handler import handle_errors

import click

logger = logging.getLogger(__name__)


@click.command(help="Log in to Renesas AI Platform")
@click.pass_obj
@handle_errors
def login(client: Client) -> None:
    """
    Login command to generate the auth token

    Parameters:
    - client : object: The client object to use for authentication
    """
    client.generate_auth_token()


@click.command(help="Log out from Renesas AI Platform")
@click.pass_obj
@handle_errors
def logout(client: Client) -> None:
    """
    Logout command to revoke the auth token

    Parameters:
    - client : object: The client object to use for authentication
    """
    client.revoke_auth_token(revoke_id_token=True)


@click.command(help="Show current authenticated user info")
@click.pass_obj
@handle_errors
def whoami(client: Client) -> None:
    """
    Whoami command to show the current authenticated user info

    Parameters:
    - client : object: The client object to use for authentication
    """
    client.user_info()
