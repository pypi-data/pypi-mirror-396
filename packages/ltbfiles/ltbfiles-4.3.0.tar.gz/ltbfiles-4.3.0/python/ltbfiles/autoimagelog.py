"""
Functions for reading auto image alignment result files (current and legacy).
"""
from datetime import timezone, datetime
from pathlib import Path
import re
from typing import Union
from dateutil import parser
import pandas as pd

def _date_utc(timestamps: str) -> datetime:
    try:
        return parser.isoparse(timestamps).astimezone(tz=timezone.utc)
    except ValueError:
        return parser.parse(timestamps, dayfirst=True).astimezone(tz=timezone.utc)


def read_aia_csv(filename: Union[Path,str]) -> pd.DataFrame:
    """
    Read an `AutoImage.csv` file as it is written by Sophi_nXt  (used since 2022).
    
    This function automatically takes care of a possible mix of timestamps with and without timezone information.

    :param filename: File to be loaded

    :return:
    - `pandas.DataFrame` containing the file content, indexed by the timestamp as a timezone aware `datetime`.
    """
    aia_data = pd.read_csv(
        filename,
        sep=";",
        dtype={"Error": str},
        converters={"TimeStamp": _date_utc,
                    "SetupName": lambda s: s.split("=")[1]}
    ).set_index("TimeStamp")
    return aia_data


def read_aia_log(filename: Union[Path,str]) -> pd.DataFrame:
    """
    Read a Sophi_7 style (legacy) `AutoImage.log` file.
    
    :param filename: File to be loaded

    :return:
    - `pandas.DataFrame` containing the file content, indexed by the timestamp as a timezone aware `datetime`.
    """
    pattern = re.compile(
        r'^(?P<all_times>\d{2,2}.\d{2,2}.\d{4,4} \d{2,2}:\d{2,2}:\d{2,2}) ' \
        r'Successfully finished auto image alignment Vertical Offset: (?P<offset_vert>[0-9.-]+) ' \
        r'Horizontal Offset: (?P<offset_horz>[0-9.-]+) Number of compared lines:+ (?P<num_lines>\d+)'
    )
    aia_data = pd.DataFrame()
    with open(filename, 'r', encoding="utf-8") as fid:
        for line in fid:
            match = pattern.match(line)
            if match:
                new_line = pd.DataFrame({
                    "TimeStamp": datetime.strptime(match.group('all_times'), '%d.%m.%Y %H:%M:%S'),
                    "VerticalOffset": float(match.group('offset_vert')),
                    "HorizontalOffset": float(match.group('offset_horz')),
                    "ComparedLines": float(match.group('num_lines'))
                }, index=[0])
                aia_data = pd.concat([aia_data, new_line], axis=0)
    return aia_data.set_index("TimeStamp")
