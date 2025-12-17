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
* Version      : 1.09
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Core component of MLOps command and subcommands
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  05.11.2025  PKa     Initial revision
* 1.01  28.11.2025  Msh     Added config functions
* 1.02  28.11.2025  PKa     Integration with backend
* 1.03  28.11.2025  PKa     Integration with backend
* 1.04  28.11.2025  HRh     Fixing errors of deploy
* 1.05  28.11.2025  PKa     Fixing errors of list-models
* 1.06  29.11.2025  PKa     Fixing errors of deploy
* 1.07  03.12.2025  PKa     Format entries into a table
* 1.08  03.12.2025  PKa     Introduction of settings
* 1.09  11.12.2025  NIt     Validation check added for video option in deploy
***********************************************************************************************************************
"""
import logging
import pathlib

from aip.utils.table import print_table

from .client import Client
from .model import ServiceModel
from .storage import Storage

logger = logging.getLogger(__name__)


def get_mlops_config(client: Client) -> dict:
    """
    Fetch MLOps config from the Renesas backend.
    Parameters:
    - client: Client instance to get the config
    Return:
    - dict: MLOps BE configuration
    """
    api_url = f"{client.aip_url}/api/v1/mlops/bootstrap"
    token = client.load_auth_token()

    response, error = client.request(
        api_url,
        headers={"Authorization": f"Bearer {token.get('id_token')}"}
    )

    if not error:
        return response

    status, message = response.get("status"), response.get("message")
    logger.error(f"Failed to fetch MLOps config. Status: {status}, Message: {message}")
    return {}



class MLOps(ServiceModel):
    service_name = "mlops"

    def __init__(self, client: Client | None = None, output: str | None = 'json'):
        """
        Initialize the MLOps model with a client and output format.
        Parameters:
        - client: AI Platform Client instance
        - output: Output format (default: 'json')
        Return:
        - None
        """
        super().__init__(client, output)
        self.token = self._client.load_auth_token()

    def list_models(self, model_type: str) -> None:
        """
        Lists the existing models that can be used
        Parameters:
        - model_type : Type of models to filter
        """
        response, error = self._client.request(
            f"{self._url}/api/models/active/{model_type}",
            headers={"Authorization": f"Bearer {self.token.get('id_token')}"},
        )
        if error:
            self.stderr(response)
        elif self.output == "json":
            self.stdout(response)
        elif model_type != "all":
            print_table(response)
        else:
            print("Trainable Models:")
            print_table(response, filter_fn=lambda r: r.get("model_type") == "trainable")
            print("Deployable Apps:")
            print_table(response, filter_fn=lambda r: r.get("model_type") != "trainable")

    def list_experiments(self) -> None:
        """
        Lists the experiments of the current user
        """
        user_id = self._client.get_user_sub()
        response, error = self._client.request(
            f"{self._url}/api/jobs/user/{user_id}",
            headers={"Authorization": f"Bearer {self.token.get('id_token')}"},
        )
        if error:
            self.stderr(response)
        elif self.output == "json":
            self.stdout(response)
        else:
            print_table(response)

    def train(self, payload: dict) -> None:
        """
        Sends an API request to train an experiment with payload

        Parameters:
        - payload : Parameters essential for training
        """
        response, error = self._client.request(
            f"{self._url}/api/v1/jobs/train/cli",
            method="post",
            json=payload,
            headers={"Authorization": f"Bearer {self.token.get('id_token')}"},
        )
        if error:
            self.stdout(response)
        else:
            self.stdout(response)

    def status(self, experiment_id: str, experiment_type: str) -> None:
        """
        Fetches the status of the experiment

        Parameters:
        - experiment_id : ID of the experiment
        - experiment_type : Type of the experiment
        """
        response, error = self._client.request(
            f"{self._url}/api/jobs/{experiment_id}/status",
            headers={"Authorization": f"Bearer {self.token.get('id_token')}"},
            params={"job_type": experiment_type},
        )
        if error:
            self.stdout(response)
        else:
            self.stdout(response)

    def result(self, experiment_id: str, experiment_type: str, result_path: pathlib.Path) -> None:
        """
        Fetches the result of the experiment

        Parameters:
        - experiment_id : ID of the experiment
        - experiment_type : Type of the experiment
        - result_path : Path to save the result file
        """
        user_email = self._client.get_user_sub()
        response, error = self._client.request(
            f"{self._url}/api/v1/jobs/{experiment_id}/results",
            params={"job_type": experiment_type, "user_id": user_email},
            headers={"Authorization": f"Bearer {self.token.get('id_token')}"},
        )
        if error:
            self.stdout(response)
        else:
            if response.get("status") == "completed" and response.get("result_s3_location"):
                Storage(self._client).pull(response=response.get("result_s3_location"), filepath=result_path)
            self.stdout(response)

    def deploy(self, payload: dict) -> None:
        """
        Deploy a common app on to the hardware

        Parameters:
        - payload : Parameters needed for deploy
        """
        # validate mutually exclusive inputs
        has_input_video = "input_video" in payload and payload["input_video"]
        has_video_location = "video_location" in payload and payload["video_location"]

        if has_input_video and has_video_location:
            self.stderr("Provide either 'input_video' or 'video_location', not both.")
            return

        if payload["deployment_backend"] == "cmn_app":
            storage = Storage(self._client)
            if "input_video" in payload:
                input_video_path = payload["input_video"]
                _, s3_location = storage.upload(file=input_video_path, data_type="media")
                if not s3_location:
                    self.stderr("Failed to upload input video to storage")
                    return
                s3_file = f"s3://{s3_location['bucket']}/{s3_location['object_key']}"
                payload["bucket_name"] = s3_location['bucket']
                payload["object_key"] = s3_location['object_key']
                payload["input_s3_location"] = s3_file
                payload["job_type"] = "deploy"
                payload["file_info"] = storage.get_file_info(file=s3_file)
            elif "video_location" in payload:
                s3_file = payload["video_location"]
                if s3_file.startswith("s3://"):
                    s3_file = s3_file[len("s3://"):]
                    parts = s3_file.split("/", 1)
                    bucket_name = parts[0]
                    object_key = parts[1] if len(parts) > 1 else ""
                else:
                    bucket_name = self._client.settings.derive_bucket()
                    object_key = payload["video_location"]
                # Send as separate fields for AIP Backend
                payload["bucket_name"] = bucket_name
                payload["object_key"] = object_key
                payload["input_s3_location"] = f"s3://{bucket_name}/{object_key}"
                payload["job_type"] = "deploy"
                payload["file_info"] = storage.get_file_info(file=payload["input_s3_location"])
            else:
                payload["job_type"] = "deploy"
        elif payload["deployment_backend"] == "app_register":
            app_location_path = payload["app_location"]  # noqa: F841
            self.stderr("App register deployment backend is not yet supported")
            return
        else:
            self.stderr(f"Unsupported deployment backend: {payload['deployment_backend']}")
            return
        response, error = self._client.request(
            f"{self._url}/api/v1/jobs/deploy",
            method="POST",
            json=payload,
            headers={"Authorization": f"Bearer {self.token.get('id_token')}"}
        )
        if error:
            self.stderr(response)
        else:
            self.stdout(response)
