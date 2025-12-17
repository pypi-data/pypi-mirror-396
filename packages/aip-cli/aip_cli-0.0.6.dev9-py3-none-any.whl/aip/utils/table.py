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
* File Name    : table.py
* Version      : 1.01
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Utils to print the list of json data into a table
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  14.11.2025  PKa     Initial revision
* 1.01  14.11.2025  PKa     Fixing sort bug if the values dont exist
***********************************************************************************************************************
"""
from rich.console import Console
from rich.table import Table


def sorting_table(data: list, sorting_column: str, *, reverse: bool) -> tuple[list, bool]:
    """
    Function to sort the table

    Parameters:
    - data : list of the data needs to be sorted
    - sorting_column : column of the table to be sorted
    - reverse : boolean value for ascending or descending

    Return:
    - tuple : returning sorted data and bool value if further filters must be skipped
    """
    skip_filter = False
    # Step 1: Separate rows with and without valid completed_at
    with_ts = [r for r in data if r.get(sorting_column)]
    without_ts = [r for r in data if not r.get(sorting_column)]
    if not with_ts:
        skip_filter = True
        return data, skip_filter
    # Step 2: Sort only the ones with timestamps

    with_ts_sorted = sorted(with_ts, key=lambda r: r.get(sorting_column), reverse=reverse)

    # Step 3: Combine back with rows without timestamp
    final_data = without_ts + with_ts_sorted
    return final_data, skip_filter


def print_table(data: list, sort_by=None, filter_fn=None, *, reverse=False) -> None:
    """
    Prints the rich table

    Parameters:
    - data : list of dictionary items
    - sort_by : column that must be used to sort. Defaults to None.
    - filter_fn : filter function in terms of lambda. Defaults to None.
    - reverse : if sorting must be reversed. Defaults to True.
    """
    # Step 1: filter
    if filter_fn:
        data = list(filter(filter_fn, data))
    skip = False
    if len(data) == 0:
        return
    # Step 2: sort
    if sort_by:
        data = sorted(data, key=lambda r: r.get(sort_by), reverse=reverse)
    if "completed_at" in data[0]:
        data, skip = sorting_table(data=data, sorting_column="completed_at", reverse=reverse)
    if "updated_at" in data[0] and not skip:
        data, skip = sorting_table(data=data, sorting_column="updated_at", reverse=reverse)
    if "created_at" in data[0] and not skip:
        data, skip = sorting_table(data=data, sorting_column="created_at", reverse=reverse)
    if "uploaded_at" in data[0] and not skip:
        data, skip = sorting_table(data=data, sorting_column="uploaded_at", reverse=reverse)

    columns = list(data[0].keys())

    table = Table(show_header=True, header_style="bold green")

    for col in columns:
        table.add_column(col, overflow="fold")

    for row in data:
        table.add_row(*(str(row.get(col, "")) for col in columns))

    Console().print(table)
