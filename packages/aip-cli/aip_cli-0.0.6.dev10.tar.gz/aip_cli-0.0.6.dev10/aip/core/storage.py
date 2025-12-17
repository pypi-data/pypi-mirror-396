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
* Version      : 1.06
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Core of Storage command and sub commands
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  14.11.2025  PKa     Initial revision
* 1.01  28.11.2025  PKa     Integration with backend
* 1.02  28.11.2025  PKa     Fixing integration problems
* 1.03  28.11.2025  PKa     Fixing integration problems with result
* 1.04  02.12.2025  PKa     Fixing endpoint problems for storage
* 1.05  03.12.2025  PKa     Format entries into a table
* 1.06  05.12.2025  PKa     Removing download failed since for training results
***********************************************************************************************************************
"""
import ast
import logging
import os
import pathlib
from urllib.parse import quote

from aip.utils.console import show_loading_status
from aip.utils.table import print_table

import requests

from .client import Client
from .model import ServiceModel

logger = logging.getLogger(__name__)


class Storage(ServiceModel):
    service_name = "storage"

    def __init__(self, client: Client | None = None, output: str | None = "json"):
        """
        Initialize the Storage model with a client and output format.
        Parameters:
        - client: AI Platform Client instance
        - output: Output format (default: 'json')
        """
        super().__init__(client, output)
        self.token = self._client.load_auth_token()
        self._cloud = "aws"
        if "localhost" in self._url and self._cloud not in ("azure", "aws"):
            self.stderr(
                f"AIWB_CLOUD environment variable is required when AIWB_URL=`{self._url}`. Please set AIWB_CLOUD to one of 'aws' or 'azure'."
            )


    def upload(self, file, data_type, bucket: str | None = None) -> tuple[str | None, dict | None]:
        """
        Uploads a file to the storage service
        Parameters:
        - file: Path to the file to upload
        - data_type: Type of data being uploaded (e.g., "media", "model", "archive")
        - bucket: Optional bucket name to upload to
        Return:
        - Tuple containing data ID and S3 location dictionary
        """
        user_email = self._client.get_user_sub()
        file_name = pathlib.Path(file).name
        payload = {"data_type": data_type, "file_name": file_name, "bucket": bucket, "user_id": user_email}
        logger.info(f"Uploading file: {file_name} of type: {data_type}")

        response, error = self._client.request(
            f"{self._url}/api/storage",
            method="post",
            json=payload,
            headers={"Authorization": f"Bearer {self.token.get('id_token')}"},
        )  # AIP Backend URL
        logger.info(f"Received response: {response} with error: {error}")
        if error:
            self.stderr(response)
            return None, None
        if data_type in {"media", "archive"}:
            if not bucket:
                bucket = response["bucket"]
            data_id = response["data_id"]
            object_key = response["object_key"]
            presigned_url = response["url"]
            self.push(presigned_url, object_storage_name=bucket, s3_key=object_key, single_file=file)
            payload = {"data_id": data_id, "status": "completed", "user_id": user_email}
            self._client.request(
                f"{self._url}/api/storage/status",
                method="POST",
                json=payload,
                headers={"Authorization": f"Bearer {self.token.get('id_token')}"},
            )  # AIP Backend URL
            print(f"Data uploaded successfully with data ID: {data_id}")
            input_s3_location = {"bucket": bucket, "object_key": object_key}
            return data_id, input_s3_location
        if data_type == "model":
            # push the model to model registry
            return None, None

        self.stderr("Cannot upload to the storage")
        return None, None

    def push(self, presigned_url, object_storage_name, s3_key, single_file):  # noqa: ARG002
        """
        Upload file to the presigned URL
        Parameters:
        - presigned_url : Presigned URL for upload
        - object_storage_name : Name of the object storage bucket
        - s3_key : S3 object key
        - single_file : Path to the single file to upload
        """
        presigned_url = ast.literal_eval(presigned_url)
        with show_loading_status("Uploading..."):
            if single_file:
                file_path = pathlib.Path(single_file)
                with open(file_path, "rb") as f:
                    files = {"file": (os.path.basename(file_path), f)}
                    response, err = self._client.request(
                        url=presigned_url["url"],
                        data=presigned_url["fields"],
                        files=files,
                        method="POST",
                    )
                if not err:
                    print(f"Uploaded {file_path} successfully")
                else:
                    print(f"Failed to upload {file_path}: {response['text']}")


    def pull(self, response, filepath):
        """
        Download file from the presigned URL
        Parameters:
        - response : Presigned URL for download
        - filepath : Path to save the downloaded file
        """
        presigned_url = response["url"]
        filename = response.get("object_key").split("/")[-1]
        # this may be replaced with requests package as content must be unpacked directly to the file
        response = requests.get(
                url=presigned_url,
                timeout=60)

        if response.status_code == 200:
            # Full path to save to
            save_path = pathlib.Path.joinpath(filepath, filename)

            # Save file in chunks
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Download successful: {save_path}")


    def get_dataset_list(self, *, user_specific: bool = False) -> None:
        """
        List dataset objects in the S3 bucket with an optional prefix

        Parameters:
        - user_specific: Boolean indicating if the datasets should be user specific

        Return:
            List of dataset object keys
        """
        response, error = self._client.request(
            f"{self._url}/api/dataset-loader/list",
            method="get",
            params={"user_specific": str(user_specific).lower(), "user_id": self._client.get_user_sub()},
            headers={"Authorization": f"Bearer {self.token.get('id_token')}"},
        )
        if error:
            self.stderr(response)
        elif self.output == "json":
            self.stdout(response)
        else:
            print_table(response['datasets'])


    def get_file_info(self, file: str) -> dict:
        """
        Get file information for a given file in storage

        Parameters:
        - file: S3 object key of the file

        Return:
            Dictionary containing file information
        """
        response, error = self._client.request(
            f"{self._url}/api/dataset-loader/details",
            method="get",
            params={"s3location": quote(file, safe=""), "user_id": self._client.get_user_sub()},
            headers={"Authorization": f"Bearer {self.token.get('id_token')}"},
        )
        if error:
            self.stderr(response)
            return {}
        return response
