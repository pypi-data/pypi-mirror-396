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
* File Name    : mlops.py
* Version      : 1.08
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : MLOps command and sub commands of MLOps
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  05.11.2025  PKa     Initial revision
* 1.01  28.11.2025  Msh     Added config commands
* 1.02  28.11.2025  PKa     Integration with backend
* 1.03  28.11.2025  PKa     Integration with backend
* 1.04  03.12.2025  AKu     Commands Modified
* 1.05  03.12.2025  PKa     Changed the name of the yolo v7 tiny model
* 1.06  03.12.2025  PKa     Format entries into a table
* 1.07  04.12.2025  MSh     Added error handling
* 1.08  05.12.2025  AEk     Added model name change
***********************************************************************************************************************
"""

import logging
import pathlib
from typing import cast

from aip.cli.cli import CLIGroup
from aip.core import Client, MLOps
from aip.core.mlops import get_mlops_config
from aip.utils.error_handler import handle_errors

import click

logger = logging.getLogger(__name__)


@click.group(cls=CLIGroup, help="Model operation commands")
@click.pass_obj
def mlops(client: Client):
    """
    MLOps management commands
    Parameters:
    - client: AI Platform Client instance
    Return:
    - None
    """


@mlops.command(help="Shows the MLOps configuration")
@click.pass_obj
@handle_errors
def config(client: Client) -> None:
    """
    Show MLOps configuration

    Parameters:
    - client : Client: The client object
    """
    config = get_mlops_config(client)
    click.echo(config)


@mlops.command(help="Shows the models available")
@click.pass_obj
@click.option("--model-type", type=click.Choice(["trainable", "reaction_common_app", "all"]), default="all", help="Type of models to list")
@click.option("-o", "--output", type=str, default="text", help="Output format One of: (json, text)")
@handle_errors
def list_models(client: Client, model_type: str, output: str) -> None:
    """
    List the available models

    Parameters:
    - client : Client: The client object
    - model_type : str: Type of the models to filter
    - output : str: Type of the output
    """
    cast(MLOps, client.model("mlops", output=output)).list_models(model_type=model_type)


@mlops.command(help="Show the list of experiments")
@click.pass_obj
@click.option("-o", "--output", type=str, default="text", help="Output format One of: (json, text)")
@handle_errors
def list_experiments(client: Client, output: str) -> None:
    """
    List the experiments of the current user
    Parameters:
    - client : Client: The client object
    - output : str: Type of the output
    """
    cast(MLOps, client.model("mlops", output=output)).list_experiments()


@mlops.command(help="Allows to start an experiment train")
@click.pass_obj
@click.option("--model-name", type=click.Choice(["HRNet", "YOLO_v7_Tiny"]), required=True, help="Model names those are available in the model registry")
@click.option("--task", type=click.Choice(["quant_pytorch"]), default="quant_pytorch", show_default=True, help="Type of the task")
@click.option("--action", type=click.Choice(["train"]), default="train", show_default=True, help="Type of action")
@click.option("--target", type=click.Choice(["v4h2"]), default="v4h2", show_default=True, help="Type of target board")
@click.option("--line", type=click.Choice(["torch"]), default="torch", show_default=True, help="Line used")
@click.option("--epochs", type=int, default=100, show_default=True, help="Number of epochs")
@click.option("--do-ptq", type=bool, default=False, show_default=True, help="Boolean value if PTQ should be performed")
@click.option("--train-batch-size", type=int, default=32, show_default=True, help="Size of batch used for training")
@click.option("--early-exit-batches-per-epoch", type=int, default=4000, show_default=True, help="Number of batches per epoch for early exit")
@click.option("--early-stopping-patience", type=int, default=8, show_default=True, help="Number of epochs for early exit")
@click.option("--job-type", default="reaction_training", help="Type of job, defaults to reaction_cmn_app")
@click.option("-o", "--output", type=str, default="json", help="Output format One of: (json, text)")
@handle_errors
def train(client: Client, output: str, **kwargs) -> None:
    """
    To start an experiment training

    Parameters:
    - client : Client: The client object
    - output : str: Type of the output
    """
    try:
        data = {key: value for key, value in kwargs.items() if value is not None}
        data["job_type"] = "reaction_training"
        cast(MLOps, client.model("mlops", output=output)).train(data)
    except Exception as e:
        print("Error type:", type(e).__name__)
        print("Error message:", e)


@mlops.command(help="To check the status of an experiment created")
@click.pass_obj
@click.option("--experiment-id", type=str, required=True, help="ID of the experiment to determine the status")
@click.option("--type", type=str, default="train", show_default=True, help="Type of the experiment One of: (train, deploy)")
@click.option("-o", "--output", type=str, default="json", help="Output format One of: (json, text)")
@handle_errors
def status(client: Client, output: str, **kwargs) -> None:
    """
    To fetch the status of an experiment

    Parameters:
    - client : Client: The client object
    - output : str: Type of the output
    """
    experiment_id = kwargs["experiment_id"]
    experiment_type = kwargs["type"]
    cast(MLOps, client.model("mlops", output=output)).status(experiment_id, experiment_type)


@mlops.command(help="To fetch the results of a completed experiment")
@click.pass_obj
@click.option("--experiment-id", type=str, required=True, help="ID of the experiment to fetch the result")
@click.option("--type", type=str, default="train", show_default=True, help="Type of the experiment One of: (train, deploy)")
@click.option("--result-path", type=str, default=".", help="Directory of the result file")
@click.option("-o", "--output", type=str, default="json", help="Output format One of: (json, text)")
@handle_errors
def result(client: Client, output: str, **kwargs) -> None:
    """
    To fetch the results of a completed experiment

    Parameters:
    - client : Client: The client object
    - output : str: Type of the output
    """
    experiment_id = kwargs["experiment_id"]
    experiment_type = kwargs["type"]
    result_path = pathlib.Path(kwargs["result_path"])
    cast(MLOps, client.model("mlops", output=output)).result(experiment_id, experiment_type, result_path)


@mlops.command(help="To deploy the model on to a board")
@click.pass_obj
@click.option(
    "--model-name",
    required=True,
    type=click.Choice(["Depth_Estimation_display-app", "Object_Detection_display-app", "OD_SS_display-app", "Semantic_Segmentation_display-app"]),
    help="Model name those are available",
)
@click.option("--deployment-backend", type=click.Choice(["cmn_app"]), default="cmn_app", help="Type of backend for the deployment")
@click.option("--target", default="v4h2", type=click.Choice(["v4h2", "rz/v2h"]), show_default=True, help="Type of target board")
@click.option("--input-video", type=str, help="Directory path of input video. Only one of input-video or video-location must be provided")
@click.option("--video-location", type=str, help="Location of an existing video in cloud storage. Only one of input-video or video-location must be provided")
# @click.option("--job-type", type=str, help="Type of job, defaults to reaction_cmn_app")
@click.option("-o", "--output", type=str, help="Output format One of: (json, text)")
@handle_errors
def deploy(client: Client, output: str, **kwargs) -> None:
    """
    To deploy the model on to a board

    Parameters:
    - client : Client: The client object
    - output : str: Type of the output
    """
    data = {key: value for key, value in kwargs.items() if value is not None}
    cast(MLOps, client.model("mlops", output=output)).deploy(data)
