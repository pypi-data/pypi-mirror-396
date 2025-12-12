"""
This module contains functions designed for reading file formats used by LTB spectrometers.

LICENSE
  Copyright (C) 2025 Dr. Sven Merk

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along
  with this program; if not, write to the Free Software Foundation, Inc.,
  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import collections
import configparser
from datetime import timezone
import json
from pathlib import Path
import struct
from typing import Union, Optional, Tuple, List, Dict, Any, IO
import zipfile
from dateutil import parser
import numpy as np
import numpy.typing as npt
from PIL import Image
from PIL.TiffTags import TAGS_V2

__pdoc__ = {}

Spectra = collections.namedtuple('Spectra', ['Y', 'x', 'o', 'head'])
"""Named tuple containing the data loaded from files."""
__pdoc__['Spectra.Y'] = 'A p x n numpy array with "n" being the number of spectra and "p" the number of pixels.'
__pdoc__['Spectra.x'] = 'The wavelength axis, a p x 1 numpy array.'
__pdoc__['Spectra.o'] = 'The spectral order information, a p x 1 numpy array.'
__pdoc__['Spectra.head'] = 'A list[dict] containing the spectra metadata. Its len is "n"'


SPEC_EXTENSIONS = ['.ary', '.aryx']
"""Default set of supported extensions for Aryelle spectra files."""


TIMESTAMP_MISSING = ""
"""Timestamp used in case it is missing"""


METADATA_HEADERS_V1 = (
    "version", "systemSerial", "spectrometerSerial", "setupName", "softwareVersion", \
    "timeStampKernelStart", "timeStampMeasurement", "ramanExcitationWavelength", "movementMode", "posX", \
    "posY", "posZ", "posA", "posB", "posC", \
    "roiName", "sessionGUID", "sessionName", "spectrumCounter", "exposureTime", \
    "shutterMode", "aisApplied", "smoothingLevel", "aiaOffsetHorizontal", "aiaOffsetVertical", \
    "aiaNumberOfLines", "aiaTimeStamp", "binningHorizontal", "binningVertical", "horizontalShiftSpeed", \
    "gainMCP", "gainEMCCD", "experimentalDelay", "qSwitchDelay1", "qSwitchDelay2", \
    "interPulseDelay", "gateWidthMCP", "laserEnergy", "laserEnergySD", "laserPulses", \
    "laserFrequency", "laserPower", "cleaningShots", "average", "subtractDark", \
    "temperatureDetector", "temperatureSpectrometer", "temperatureSample", "temperatureSampleChamber", "temperatureEnvironment")
"""Headers of the unified metadata v1 defined for aryx. All functions will return this metadata."""


METADATA_DEFAULT_V1 = (
    1, "", "", "", "", \
    TIMESTAMP_MISSING, TIMESTAMP_MISSING, np.nan, "AtRest", np.nan, \
    np.nan, np.nan, np.nan, np.nan, np.nan, \
    "", "", "", 1, np.nan, \
    "Open", False, np.nan, np.nan, np.nan, \
    0, TIMESTAMP_MISSING, np.nan, np.nan, np.nan, \
    np.nan, np.nan, np.nan, np.nan, np.nan, \
    np.nan, np.nan, np.nan, np.nan, np.nan, \
    np.nan, np.nan, np.nan, np.nan, True, \
    np.nan, np.nan, np.nan, np.nan, np.nan
)
"""Default values for unified metadata v1, if missing."""


__METADATA_V1_DEFAULTS: Dict[str, Union[int, float, str, bool]] = dict(zip(METADATA_HEADERS_V1, METADATA_DEFAULT_V1))
"""Dictionary mapping V1 headers to their default values for efficient lookup."""


METADATA_HEADERS_V2 = (
    "version", "systemSerial", "spectrometerSerial", "setupName", "softwareVersion", \
    "timeStampKernelStart", "timeStampMeasurement", "ramanExcitationWavelength", "movementMode", "posX", \
    "posY", "posZ", "posA", "posB", "posC", \
    "roiName", "sessionGUID", "sessionName", "spectrumCounter", "exposureTime", \
    "shutterMode", "aisApplied", "smoothingLevel", "orderWidth", "crossTalkThreshold", \
    "aiaOffsetHorizontal", "aiaOffsetVertical", "aiaNumberOfLines", "aiaTimeStamp", "binningHorizontal", \
    "binningVertical", "horizontalShiftSpeed", "gainMCP", "gainEMCCD", "experimentalDelay", \
    "qSwitchDelay1", "qSwitchDelay2", "interPulseDelay", "gateWidthMCP", "laserEnergy", \
    "laserEnergySD", "laserEnergyTarget", "laserPulses", "laserFrequency", "laserPower", \
    "cleaningShots", "average", "subtractDark", "temperatureDetector", "temperatureSpectrometer", \
    "temperatureSample", "temperatureSampleChamber", "temperatureEnvironment")
"""Headers of the unified metadata v2 defined for aryx. All functions will return this metadata."""


METADATA_DEFAULT_V2 = (
    2, "", "", "", "", \
    TIMESTAMP_MISSING, TIMESTAMP_MISSING, np.nan, "AtRest", np.nan, \
    np.nan, np.nan, np.nan, np.nan, np.nan, \
    "", "", "", np.nan, np.nan, \
    "Open", False, np.nan, "", np.nan, \
    np.nan, np.nan, 0, TIMESTAMP_MISSING, np.nan, \
    np.nan, np.nan, np.nan, np.nan, np.nan, \
    np.nan, np.nan, np.nan, np.nan, np.nan, \
    np.nan, np.nan, np.nan, np.nan, np.nan, \
    np.nan, np.nan, True, np.nan, np.nan, \
    np.nan, np.nan, np.nan
)
"""Default values for unified metadata v2, if missing."""


__METADATA_V2_DEFAULTS: Dict[str, Union[int, float, str, bool]] = dict(zip(METADATA_HEADERS_V2, METADATA_DEFAULT_V2))
"""Dictionary mapping V2 headers to their default values for efficient lookup."""


METADATA_ADDED = ("filename", "timestamp", "x_name", "x_unit")
"""Metadata that is added to that loaded from files"""


class UnknownTypeException(Exception):
    """Exception thrown when trying to load a spectrum file that is not supported."""

    def __init__(self, extension: str):
        """Construct an exception message with the given file extension."""
        super().__init__(f"Unknown file extension '{extension}'")


class IncompatibleSpectraException(Exception):
    """Exception thrown whenever spectra are not compatible, e.g. the wavelength does not match."""


class CorruptedFileException(Exception):
    """Exception thrown whenever a spectrum file is incomplete"""


def _load_file(filename: Union[Path,str]) -> Spectra:
    filename = Path(filename)
    ext = filename.suffix.lower()
    if ".ary" == ext:
        return read_ltb_ary(filename)
    if  ".aryx" == ext:
        return read_ltb_aryx(filename)
    raise UnknownTypeException(ext)


def load_files(filelist: Union[List[Path],List[str]], *, interpolate:bool=False) -> Spectra:
    """
    Read the content of multiple spectra files into a merged numpy-array.

    :param filenames: List of filenames to be loaded

    Keyword Arguments
    
    :param interpolate: Interpolate if wavelength axis does not match.

    :return:
    - `Spectra`: namedtuple
        A named tuple containing the loaded data.
    """
    if not isinstance(filelist, list):
        filelist = [filelist]
    assert len(filelist) > 0, "At least one file must be passed"
    y, wl, order, h = _load_file(filelist[0])
    Y = np.full((len(y), len(filelist)), np.nan)
    Y[:,0] = y
    head = [h]
    if len(filelist) > 1:
        for i_file, file in enumerate(filelist[1:], start=1):
            y,x,o,h = _load_file(file)
            if not (np.array_equal(x, wl) and np.array_equal(o, order)):
                if not interpolate:
                    raise IncompatibleSpectraException(
                        f"Can only merge spectra with identical wavelength axis (current: '{str(file)}'")
                y = np.interp(wl, x, y)
                order = np.zeros(x.shape)
            Y[:,i_file] = y
            head.append(h)
    return Spectra(Y, wl, order, head)


def scan_for_files(folder: Union[Path,str], *, extensions=None) -> List[Path]:
    """
    Create a list of all spectra in a given folder.

    :param folder: Name of the folder to be scanned for files
    
    Keyword Arguments

    :param extensions: File extensions that should be searched for. Default = `SPEC_EXTENSIONS`
    
    :return:

    - files: list[Path]
        List of spectra files found within the folder.
    """
    folder = Path(folder)
    if extensions is None:
        extensions = SPEC_EXTENSIONS
    if isinstance(extensions, str):
        extensions = [extensions]
    return [
        folder / file for file in folder.iterdir()
        if any(ext == file.suffix for ext in extensions)
    ]


def load_folder(folder: Union[Path,str], *, interpolate:bool=False, extensions=None) -> Optional[Spectra]:
    """
    Load all spectra to be found in a given folder.

    :param folder: Name of the folder to be scanned for spectra
    
    Keyword Arguments
    
    :param interpolate: Interpolate if wavelength axis does not match.
    :param extensions: File extensions that should be searched for. Default = `SPEC_EXTENSIONS`
    
    :return:
    - `Spectra`: namedtuple
        Spectra loaded from the folder.
    """
    if extensions is None:
        extensions = SPEC_EXTENSIONS
    files = scan_for_files(folder, extensions=extensions)
    if len(files) > 0:
        Y, x, o, head = load_files(files, interpolate=interpolate)
        return Spectra(Y,x,o,head)
    return None


AIF_DTYPE_ARY = np.dtype([('indLow', np.int32),
                        ('indHigh', np.int32),
                        ('order', np.int16),
                        ('lowPix', np.int16),
                        ('highPix', np.int16),
                        ('foo', np.int16),
                        ('lowWave', np.float32),
                        ('highWave', np.float32)])


def __read_ary_spec(spec: bytes, sort_wl: bool) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
    dt = np.dtype([('int', np.float32), ('wl', np.float32)])
    values = np.frombuffer(spec, dtype=dt)
    if sort_wl:
        sort_order = np.argsort(values['wl'])
        x = values['wl'][sort_order]
        y = values['int'][sort_order]
    else:
        sort_order = np.arange(0, len(values['wl']))
        x = values['wl']
        y = values['int']
    return y, x, sort_order


def __read_ary_meta(meta: List[str]) -> Dict:
    head_in = {}
    for i_line in meta:
        stripped_line = str.strip(i_line)
        if '[end of file]' == stripped_line:
            break
        new_entry = stripped_line.split('=')
        head_in[new_entry[0].replace(' ', '_')] = new_entry[1]
    head = __METADATA_V2_DEFAULTS.copy()
    head["spectrometerSerial"] = head_in.get("spectrometer_serial_number", "")
    head["setupName"] = head_in.get("spectrometer_name", "")
    head["softwareVersion"] = head_in.get("software_version", "")
    time_str = f"{head_in.get('date_of_measurement', '')} {head_in.get('time_of_measurement', '')}"
    time = parser.parse(time_str, dayfirst=True).astimezone(tz=timezone.utc)
    head["timeStampMeasurement"] = time.isoformat().replace("+00:00", "Z")
    # cspell:disable-next-line
    head["ramanExcitationWavelength"] = float(head_in.get("Raman_exitation_wavelength", np.nan)) \
        if "Raman" in head_in.get("Scaling", "") else np.nan # Typo in original key is known legacy
    head["exposureTime"] = float(head_in.get("exposure_time", np.nan))
    head["aiaOffsetHorizontal"] = float(head_in.get("AutoImage_HorizontalOffset", 0))
    head["aiaOffsetVertical"] = float(head_in.get("AutoImage_VerticalOffset", 0))
    head["aiaNumberOfLines"] = int(head_in.get("AutoImage_NumberofComparedLines", 0)) # cspell:disable-line
    head["aiaTimeStamp"] = head_in.get("AutoImage_TimeStamp", "")
    head["binningHorizontal"] = int(head_in.get("horizontal_binning", 1))
    head["binningVertical"] = int(head_in.get("vertical_binning", 1))
    head["horizontalShiftSpeed"] = float(head_in.get("HSSpeed", np.nan))
    head["gainMCP"] = int(head_in.get("ICCD_gain", 0))
    head["gainEMCCD"] = int(head_in.get("EMCCDGain", 0))
    head["experimentalDelay"] = float(head_in.get("delay_time", np.nan))
    head["qSwitchDelay1"] = float(head_in.get("Laser_qswitch_delay", np.nan))
    head["gateWidthMCP"] = float(head_in.get("ICCD_gate_width", np.nan))
    head["laserFrequency"] = float(head_in.get("Laser_frequency", np.nan))
    head["average"] = int(head_in.get("Number_of_averaged_spectra", 1))
    return head


def read_ltb_ary(file: Union[Path,str,IO[bytes]], *, sort_wl: bool=True) -> Spectra:
    """
    Read data from a binary *.ary file for LTB spectrometers.

    :param file: Either the Name of the *.ary file to be read, an open file handle or a `io.BinaryIO` object.
        If a name is given, it may be a relative path or full filename.

    Keyword Arguments
    
    :param sortWL: Specify if spectra should be sorted by their wavelength after reading. default = True
    
    :return:

    - `Spectra`: namedtuple
        The spectrum loaded.

    Caution! Due to order overlap, it may happen that two pixels have the
    same wavelength. If this causes problems in later data treatment, such
    pixels should be removed using

    ```
    x, ind = numpy.unique(x, True)
    o=o[ind]
    y=y[ind]
    ```
    """
    x = None
    y = None
    sort_order = None
    order_info = None
    head = {}

    with zipfile.ZipFile(file) as f_zip:
        file_list = f_zip.namelist()

        for i_file in file_list:
            if i_file.endswith('~tmp'):
                y, x, sort_order = __read_ary_spec(f_zip.read(i_file), sort_wl=sort_wl)
            elif i_file.endswith('~aif'):
                order_info = np.frombuffer(f_zip.read(i_file), AIF_DTYPE_ARY)
            elif i_file.endswith('~rep'):
                try:
                    head = __read_ary_meta(f_zip.read(i_file).decode("utf-8").splitlines())
                except Exception as exc:
                    raise CorruptedFileException("Metadata is corrupted") from exc

        if x is None or y is None or order_info is None or not head:
            raise CorruptedFileException("File content is incomplete")
        if isinstance(file, (Path, str)):
            head['filename'] = Path(file)
        elif hasattr(file, "name"):
            head['filename'] = Path(file.name)
        else:
            head['filename'] = "memory"
        head["timestamp"] = parser.isoparse(head["timeStampMeasurement"])
        if head.get("ramanExcitationWavelength", 0) > 0:
            x = (1e7 / head["ramanExcitationWavelength"]) - (1e7 / x)
            head["x_name"] = "Raman shift"
            head["x_unit"] = "cm^{-1}"
        else:
            head["x_name"] = "Wavelength"
            head["x_unit"] = "nm"

        o = np.empty(x.size)
        o[:] = np.nan
        for i_curr_order in order_info:
            o[i_curr_order['indLow']:i_curr_order['indHigh'] + 1] = i_curr_order['order']
        o = o[sort_order]

    return Spectra(y, x, o, head)


AIF_DTYPE_ARYX = np.dtype([('indLow', np.int32),
                      ('indHigh', np.int32),
                      ('order', np.int16),
                      ('lowPix', np.int16),
                      ('highPix', np.int16),
                      ('foo', np.int16),
                      ('lowWave', np.float64),
                      ('highWave', np.float64)])


def __read_aryx_spec(spec: bytes, sort_wl: bool) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
    dt = np.dtype([('int', np.float64), ('wl', np.float64)])
    values = np.frombuffer(spec, dtype=dt)
    if sort_wl:
        sort_order = np.argsort(values['wl'])
    else:
        sort_order = np.arange(0, len(values['wl']))
    x = values['wl'][sort_order]
    y = values['int'][sort_order]
    return y, x, sort_order


def __convert_metadata_1_to_2(head_v1: Dict[str, Any]) -> Dict[str, Any]:
    """Convert metadata from version 1 to version 2 format."""
    # Create v2 dict with proper field ordering using dict comprehension
    head_v2 = {header: head_v1.get(header, __METADATA_V2_DEFAULTS[header]) for header in METADATA_HEADERS_V2}
    head_v2["version"] = 2
    return head_v2


def __convert_legacy_metadata(head_in: Dict[str, Any]) -> dict:
    head = __METADATA_V2_DEFAULTS.copy()
    head["spectrometerSerial"] = head_in["measure"].get("SerialNumber", "")
    head["setupName"] = head_in["measure"].get("SetupName", "")
    if time_str := head_in["measure"].get("ISOFormat"):
        head["timeStampMeasurement"] = time_str
    else:
        time_str = f"{head_in['measure']['Date']} {head_in['measure']['TimeStamp']}"
        time = parser.isoparse(time_str).astimezone(tz=timezone.utc)
        head["timeStampMeasurement"] = time.isoformat().replace("+00:00", "Z")
    head["ramanExcitationWavelength"] = head_in["measure"].get("ExcitationLength", np.nan)
    head["posX"] = head_in["measure"].get("XPos", np.nan)
    head["posY"] = head_in["measure"].get("YPos", np.nan)
    head["posZ"] = head_in["measure"].get("ZPos", np.nan)
    head["exposureTime"] = head_in.get("detector", {}).get("ExposureTime", np.nan)
    head["shutterMode"] = head_in.get("detector", {}).get("Shutter", {}).get("Mode", "Open")
    head["binningHorizontal"] = head_in.get("detector", {}).get("Binning", {}).get("Horizontal", np.nan)
    head["binningVertical"] = head_in.get("detector", {}).get("Binning", {}).get("Vertical", np.nan)
    head["horizontalShiftSpeed"] = head_in.get("detector", {}).get("HorizontalShiftSpeed", np.nan)
    head["gainMCP"] = head_in.get("detector", {}).get("GainMCP", 0)
    head["gainEMCCD"] = head_in.get("detector", {}).get("GainEMCCD", 0)
    head["experimentalDelay"] = head_in.get("libsControl", {}).get("ExperimentalDelay", np.nan)
    head["qSwitchDelay1"] = head_in.get("libsControl", {}).get("FlashLampQSwitchDelay", np.nan)
    head["qSwitchDelay2"] = head_in.get("libsControl", {}).get("FlashLampQSwitchDelay2", np.nan)
    head["interPulseDelay"] = head_in.get("libsControl", {}).get("InterpulseDelay", np.nan)
    head["gateWidthMCP"] = head_in.get("detector", {}).get("ICCDGateWidth", np.nan)
    head["laserFrequency"] = head_in.get("libsControl", {}).get("LaserFrequency", np.nan)
    head["cleaningShots"] = head_in.get("libsControl", {}).get("Laser1CleaningShots", 0)
    head["average"] = head_in.get("detector", {}).get("AverageCount", 1)
    head["subtractDark"] = head_in.get("detector", {}).get("SubtractDarkImage", True)
    head["temperatureDetector"] = head_in.get("detector", {}).get("Temperature", np.nan)
    return head


def __read_aryx_meta(f_zip: zipfile.ZipFile) -> dict:
    head = {}
    file_list = f_zip.namelist()
    if "metadata_summary.json" in file_list:
        head_s = f_zip.read("metadata_summary.json").decode("utf-8")
        head = json.loads(head_s)
        if head["version"] == 1:
            # Convert v1 to dictionary with proper v1 defaults for missing values
            head_v1 = {k: head[k] if head[k] is not None else __METADATA_V1_DEFAULTS[k]
                      for k in METADATA_HEADERS_V1}
            # Convert v1 to v2
            head = __convert_metadata_1_to_2(head_v1)
        elif head["version"] == 2:
            # Already v2 format, only set defaults where missing
            head = {k: head[k] if head[k] is not None else __METADATA_V2_DEFAULTS[k] for k in METADATA_HEADERS_V2}
        else:
            raise CorruptedFileException(f"Unsupported metadata version: {head['version']}")
    else:
        rep_file = [file for file in file_list if file.endswith('~json')]
        if len(rep_file) == 1:
            head_s = f_zip.read(rep_file[0]).decode("utf-8")
            try:
                head = __convert_legacy_metadata(json.loads(head_s))
            except Exception as exc:
                raise CorruptedFileException("Metadata is malformed") from exc
    return head


def read_ltb_aryx(file: Union[Path,str,IO[bytes]], *, sort_wl:bool=True) -> Spectra:
    """
    Read data from a binary *.aryx file for LTB spectrometers.

    :param file: Either the Name of the *.aryx file to be read, an open file handle or a `io.BinaryIO` object.
        If a name is given, it may be a relative path or full filename.
    
    Keyword Arguments
    
    :param sortWL: Specify if spectra should be sorted by their wavelength after reading. default = True
    
    :return:

    - `Spectra`: namedtuple
        The spectrum loaded.
    """
    x = None
    y = None
    sort_order = None
    order_info = None

    with zipfile.ZipFile(file) as f_zip:
        file_list = f_zip.namelist()
        head = __read_aryx_meta(f_zip)
        for i_file in file_list:
            if i_file.endswith('~tmp'):
                y, x, sort_order = __read_aryx_spec(f_zip.read(i_file), sort_wl=sort_wl)
            elif i_file.endswith('~aif'):
                aif = f_zip.read(i_file)
                order_info = np.frombuffer(aif, AIF_DTYPE_ARYX)

        if x is None or y is None or order_info is None or not head:
            raise CorruptedFileException("File content is incomplete")

        if isinstance(file, (Path, str)):
            head['filename'] = Path(file)
        elif hasattr(file, "name"):
            head['filename'] = Path(file.name)
        else:
            head['filename'] = "memory"
        head["timestamp"] = parser.isoparse(str(head["timeStampMeasurement"]))

        if (wl := float(head["ramanExcitationWavelength"])) > 0:
            x = (1e7 / wl) - (1e7 / x)
            head["x_name"] = "Raman shift"
            head["x_unit"] = "cm^{-1}"
        else:
            head["x_name"] = "Wavelength"
            head["x_unit"] = "nm"

        o = np.empty(x.size)
        o[:] = np.nan
        for i_curr_order in order_info:
            o[i_curr_order['indLow']:i_curr_order['indHigh'] + 1] = i_curr_order['order']
        o = o[sort_order]

    return Spectra(y, x, o, head)


def write_ltb_aryx(file: Union[str,Path,IO[bytes]], spec: Spectra) -> None:
    """
    Write data to a binary *.aryx file for LTB spectrometers, readable by Sophi_nXt.

    :param file: Target for writing. Can be a file name, BytesIO object or an open file handle.
    :param spec: Named tuple `Spectra` containing the spectrum to be written.
        Only a single spectrum can be written to a file.
    """
    if len(spec.Y.shape) > 1:
        raise ValueError("The aryx file format can only store singular spectra")
    ind = np.lexsort((spec.x, -spec.o))
    y = spec.Y[ind]
    x = spec.x[ind]
    o = spec.o[ind]

    orders = np.unique(o)
    aif = np.empty((len(orders)), dtype=AIF_DTYPE_ARYX)
    for i, order in enumerate(orders):
        i_order = np.argwhere(order == o)
        first_pix = i_order[0].item()
        last_pix = i_order[-1].item()
        aif["indLow"][i] = first_pix
        aif["indHigh"][i] = last_pix
        aif["order"][i] = order
        aif["lowPix"][i] = 0 # raw image column start, can not be recovered -> fake
        aif["highPix"][i] = last_pix - first_pix # raw image column end, can not be recovered -> fake
        aif["foo"][i] = 0
        aif["lowWave"][i] = x[first_pix]
        aif["highWave"][i] = x[last_pix]

    if isinstance(file, (Path, str)):
        stem = Path(file).stem
    elif hasattr(file, "name"):
        stem = Path(file.name).stem
    else:
        stem = "spectrum"
    head_write = {k: spec.head[k] if not isinstance(spec.head[k], float) or not np.isnan(spec.head[k]) else None \
                  for k in METADATA_HEADERS_V2}
    with zipfile.ZipFile(file, mode="w") as f_zip:
        f_zip.writestr(stem + ".~tmp", np.vstack((y,x)).T.tobytes())
        f_zip.writestr(stem + ".~aif", aif.tobytes())
        f_zip.writestr("metadata_summary.json", json.dumps(head_write, allow_nan=False))


def _make_header_from_array(data):
    head = {'ChipWidth': int(data[0]),
            'ChipHeight': int(data[1]),
            'PixelSize': float(data[2]),
            'HorBinning': int(data[3]),
            'VerBinning': int(data[4]),
            'BottomOffset': int(data[5]),
            'LeftOffset': int(data[6]),
            'ImgHeight': int(data[7]),
            'ImgWidth': int(data[8])
            }
    return head


def read_ltb_raw(file: Union[Path,str,IO[bytes]]) -> Tuple[np.ndarray, dict]:
    """
    Read a *.raw image file created with LTB spectrometers.
    
    :param file: Either the Name of the *.aryx file to be read, an open file handle or a `io.BinaryIO` object.
        If a name is given, it may be a relative path or full filename.

    :return:
    
    - image: np.array of image shape
    - head: dict containing image properties
    """
    data = np.loadtxt(file)
    head = _make_header_from_array(data[0:9])
    image = np.reshape(data[9:].astype(np.int32), (head['ImgHeight'], head['ImgWidth']))
    return image, head


def read_ltb_rawb(filename: Union[Path,str]) -> Tuple[np.ndarray, dict]:
    """
    Read a *.rawb image file created with LTB spectrometers.
    
    :param filename: Name of the *.rawb file to be read. May be a relative path or full filename.

    :return:

    - image : np.array of image shape
    - head : dict containing image properties
    """
    struct_fmt = '=iidiiiiii'
    struct_len = struct.calcsize(struct_fmt)
    struct_unp = struct.Struct(struct_fmt).unpack_from

    with open(filename,'rb') as f_file:
        metadata = f_file.read(struct_len)
        im_stream = np.fromfile(f_file, dtype=np.int32)
        h = struct_unp(metadata)
        head = _make_header_from_array(h)
        image = np.reshape(im_stream, (head['ImgHeight'], head['ImgWidth']))
    return image, head


def read_ltb_rawx(file: Union[Path,str,IO[bytes]]) -> Tuple[np.ndarray, dict]:
    """
    Reads a *.rawx image file created with LTB spectrometers.
    
    :param file: Either the Name of the *.aryx file to be read, an open file handle or a `io.BinaryIO` object.
        If a name is given, it may be a relative path or full filename.

    :return:
    - image : np.array of image shape
    - head : dict containing all measurement and spectrometer parameters
    """
    with zipfile.ZipFile(file) as f_zip:
        file_list = f_zip.namelist()
        image = None
        sophi_head = configparser.ConfigParser()
        aryelle_head = configparser.ConfigParser()
        for i_file in file_list:
            if i_file.endswith('rawdata'):
                img = f_zip.read(i_file).decode("utf-8").splitlines()
                image = np.loadtxt(img)
            elif i_file.lower() == 'aryelle.ini':
                ary_ini = f_zip.read(i_file).decode("utf-8")
                aryelle_head.read_string(ary_ini)
            elif i_file.lower() == 'sophi.ini':
                sophi_ini = f_zip.read(i_file).decode("utf-8")
                sophi_head.read_string(sophi_ini)
        width = int(aryelle_head['CCD']['width']) // int(sophi_head['Echelle 1']['vertical binning'])
        height = int(aryelle_head['CCD']['height']) // int(sophi_head['Echelle 1']['horizontal binning'])
        head = {'sophi_ini': sophi_head,
                'aryelle_ini': aryelle_head}
        assert image is not None
        image = image.reshape((height, width))

    return image, head


def read_ltb_tiff(file: Union[Path,str]) -> Tuple[np.ndarray, dict]:
    """
    Read a *.tif detector raw image file created with LTB spectrometers.
    
    :param file: Name of the *.tif file to be read. May be a relative path, full filename or opened file stream.

    :return:

    - image : np.array of image shape
    - head : dict containing measurement metadata
    """
    tag_id = next((tag for tag, value in TAGS_V2.items() if value.name == 'ImageDescription'), None)
    with Image.open(file) as img:
        head = img.tag_v2.get(tag_id, {}) # type: ignore
        image = np.array(img)
    return image, json.loads(head)
