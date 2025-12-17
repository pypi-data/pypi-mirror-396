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
* File Name    : settings.py
* Version      : 1.00
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Settings for AIP CLI
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  05.12.2025  PKa     Initial revision
***********************************************************************************************************************
"""
from __future__ import annotations

import sys
from typing import Any, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Public environment choice
EnvName = Literal["prod", "nonprod"]

# Production endpoints
PROD_DEFAULTS = {
    "aip_url":  "https://ai-portal.altium.com",
    "aiwb_url": "https://aiwb.ai-portal.altium.com",
}

# Pattern for deriving non-prod endpoints from a tag.
# We can also remove the derivation_templates, if we think we risk of exposing non-dev environments to public
DERIVATION_TEMPLATES = {
    "aip_url": "https://ai-portal.{tag}.altium.com",
    "aiwb_url": "https://aiwb.ai-portal.{tag}.altium.com",
}

BOOL_TRUE = {"true", "1", "yes", "y", "on"}
BOOL_FALSE = {"false", "0", "no", "n", "off"}


class EnvValidationError(Exception):
    pass


class Settings(BaseSettings):
    # Customer-facing env: defaults to prod/nonprod
    env: EnvName = "prod"                                                   # AIP_ENV

    # tag to provide the actual env name used internally
    env_tag: str | None = None                                              # AIP_ENV_TAG
    bucket_tag: str = "prod"                                                # AIP_BUCKET_TAG

    # Base URLs: prod default, or derived from tag, or explicit override
    url: str | None = None                                                  # AIP_URL
    aiwb_url: str | None = None                                             # AIP_AIWB_URL

    # Runtime knobs
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"        # AIP_LOG_LEVEL
    token_provider: Literal["aip", "oidc", "none"] = "aip"  # noqa: S105    # AIP_TOKEN_PROVIDER

    # Advanced / QA
    inference_bucket: str | None = None                                     # AIP_INFERENCE_BUCKET
    access_key: SecretStr | None = None                                     # AIP_ACCESS_KEY
    oidc_client_id: str | None = "aiwb_workbench"                           # AIP_OIDC_CLIENT_ID
    cloud: str | None = "aws"                                               # AIP_CLOUD
    tenant: str | None = None                                               # AIP_TENANT
    cache_dir: str | None = "~/.aip/cache"                                  # AIP_CACHE_DIR
    token_file: str = "token.json"  # noqa: S105                            # AIP_TOKEN_FILE
    suppress_browser: bool = False                                          # AIP_SUPPRESS_BROWSER
    debug: bool = False                                                     # AIP_DEBUG
    verbose: bool = False                                                   # AIP_VERBOSE


    model_config = SettingsConfigDict(
        env_prefix="AIP_",                  # e.g., AIP_ENV, AIP_ENV_TAG, AIP_URL, AIP_AIWB_URL
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )

    @model_validator(mode="before")
    @classmethod
    def strip_all_strings(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize incoming raw data: strip whitespace/CRLF, and convert
        empty strings to None. Runs before field parsing.
        Parameters:
        - cls : class
        - data : dict[str, Any] : incoming data
        Return:
        - dict[str, Any] : cleaned data
        """
        if not isinstance(data, dict):
            return data
        clean = {}
        for k, v in data.items():
            if isinstance(v, str):
                v2 = v.strip()           # removes '\r', leading/trailing spaces
                clean[k] = v2 if v2 != "" else None
            else:
                clean[k] = v
        return clean

    # Derive URLs based on env and tag
    @field_validator("url", mode="before")
    @classmethod
    def derive_aip_url(cls, v: str | None, info) -> str | None:
        """
        Derive AIP URL based on tag, if not explicitly set.
        Parameters:
        - cls: class
        - v : current value
        - info : validator info
        Return:
        - str | None : derived URL or None
        """
        if v:  # explicit override present
            return v
        env = info.data.get("env", "prod")
        tag = info.data.get("env_tag")
        if env == "prod":
            return PROD_DEFAULTS["aip_url"]
        if tag:
            return DERIVATION_TEMPLATES["aip_url"].format(tag=tag)
        # nonprod without tag → require explicit AIP_URL; leave None for runtime check
        return None

    @field_validator("aiwb_url", mode="before")
    @classmethod
    def derive_aiwb_url(cls, v: str | None, info) -> str | None:
        """
        Derive AIWB URL based on tag, if not explicitly set.

        Parameters:
        - cls: class
        - v : current value
        - info : validator info
        Return:
        - str | None : derived URL or None
        """
        if v:
            return v
        env = info.data.get("env", "prod")
        tag = info.data.get("env_tag")
        if env == "prod":
            return PROD_DEFAULTS["aiwb_url"]
        if tag:
            return DERIVATION_TEMPLATES["aiwb_url"].format(tag=tag)
        return None

    @field_validator("inference_bucket", mode="before")
    @classmethod
    def derive_bucket(cls, v: str | None, info) -> str | None:
        """
        Derive inference bucket name based on tag, if not explicitly set.
        Pattern: aiwb-mlops-{tag}-cmnapp-ud
        Parameters:
        - cls: class
        - v: Current value
        - info: Validator info
        Return:
        - str | None: Derived bucket name or None
        """
        if v:
            return v
        tag = info.data.get("bucket_tag")
        if tag:
            return f"aiwb-mlops-{tag}-cmnapp-ud"
        return None

    @field_validator("debug", "verbose", "suppress_browser", mode="before")
    @classmethod
    def coerce_booleans(cls, v: Any) -> bool:
        """
        Convert Strings to booleans if they are not boolean
        Parameters:
        - cls: class
        - v : Current value
        Return:
        - bool
        """
        if v is None:
            return False  # or preserve default
        if isinstance(v, bool):
            return v
        v = v.strip().lower()
        if v in BOOL_TRUE:
            return True
        if v in BOOL_FALSE:
            return False
        raise EnvValidationError(f"Invalid boolean: {v}")

    @field_validator("env_tag", "bucket_tag", mode="after")
    @classmethod
    def require_tag_for_nonprod(cls, v: str, info) -> str:
        """
        Verification of tag
        Parameters:
        - cls: class
        - v : Current Value
        - info : Validator info
        Return:
        - str
        """
        env = info.data.get("env")
        # If env is nonprod, env_tag and bucket_tag must be provided
        if env == "nonprod" and (v == "prod" or not v):
            raise EnvValidationError(
                "AIP_ENV_TAG and AIP_BUCKET_TAG is required when AIP_ENV='nonprod'."
            )
        return v

    def to_public_dict(self) -> dict:
        """
        Redacted view of settings, safe to print to the console.
        Only includes fields useful for QA; hides sensitive values.
        Return:
        - dict: Settings data dict
        """
        data = self.model_dump(exclude_none=True)
        # Redact secrets
        if "access_key" in data and isinstance(self.access_key, SecretStr):
            data["access_key"] = "***redacted***"

        # Normalize URLs to strings
        if "url" in data and data["url"] is not None:
            data["url"] = str(self.url)
        if "aiwb_url" in data and data["aiwb_url"] is not None:
            data["aiwb_url"] = str(self.aiwb_url)

        return data


def get_settings() -> Settings:
    """
    retrieve all the saved settings

    Return:
    - Settings : object
    """
    try:
        settings = Settings()
    except EnvValidationError as err:
        print(err)
        sys.exit(1)
    return settings
