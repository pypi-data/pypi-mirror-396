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
* File Name    : aip/core/dataset.py
* Version      : 1.02
* Product Name : AIP-CLI
* Device(s)    : NA
* Description  : Dataset model for AI Platform.
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author   Description
* 1.00  17.11.2025  MSh      Initial revision.
* 1.01  27.11.2025  PKa      Updating Product Name
* 1.02  28.11.2025  PKa      Fixing integration problems with result
***********************************************************************************************************************
"""
import logging

from .client import Client
from .model import ServiceModel

logger = logging.getLogger(__name__)


class DatasetModel(ServiceModel):
    service_name = "dataset_loader"

    def __init__(self, client: Client | None = None, output: str | None = 'json'):
        """
        Initialize the DatasetModel with a client and output format.
        Parameters:
        - client: AI Platform Client instance
        - output: Output format (default: 'json')
        Return:
            None
        """
        super().__init__(client, output)

    def get_dataset_list(self, prefix: str = "") -> list:
        """
        List dataset objects in the S3 bucket with an optional prefix

        Parameters:
        - prefix: S3 object key prefix to filter datasets (default: "")

        Return:
            List of dataset object keys
        """
        response, error = self._client.request(
            f"{self._url}/api/dataset-loader/list",
            method="get",
            params={"prefix": prefix}
        )
        if error:
            self.stderr(response)
        return response.get("datasets", [])
