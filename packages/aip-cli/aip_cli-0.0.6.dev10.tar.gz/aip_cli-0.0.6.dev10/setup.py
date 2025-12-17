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
* File Name    : setup.py
* Version      : 1.00
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Base setup of CLI
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  16.10.2025  TRa     Initial revision
***********************************************************************************************************************
"""
import codecs
import re
from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).resolve().parent

DEPENDENCIES = [
    "requests",
    "click~=8.1.7",
    "python-dateutil",
    "rich==14.0.0",
    "botocore",
    "click-shell",
    "strands-agents",
    "strands-agents-tools",
    "colorama",
    "pyfiglet",
    "rich-gradient",
    "pip-system-certs",
]

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Natural Language :: English",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: Apache Software License",
]


def read(*parts: str) -> str:
    """
    Read file contents
    Return:
    - str: File contents
    """
    return codecs.open(str(here.joinpath(*parts)), "r", "utf-8").read()


def find_version(*file_paths: str) -> str:
    """
    Find version in file
    Return:
    - str: Version string
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("README.rst", encoding="utf-8") as f:
    README = f.read()

setup_options = {
    "name": "aip-cli",
    "version": find_version("aip", "__init__.py"),
    "description": "Renesas AI Platform Command-Line Tools.",
    "long_description": README,
    "author": "Renesas AI Platform",
    "url": "https://ai.aws.renesasworkbench.com/",
    "scripts": ["bin/aip", "bin/aip.cmd"],
    "packages": find_packages(exclude=["tests*"]),
    "install_requires": DEPENDENCIES,
    "license": "Apache License 2.0",
    "python_requires": ">= 3.10",
    "classifiers": CLASSIFIERS,
}

setup(**setup_options)
