#!/usr/bin/env python3
# pyrotoolbox, a collection of tools to work with PyroScience GmbH data.
# Copyright (C) 2025, Christoph Staudinger
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""This module contains parser to load data from different logfile formats.

The "parse" function is able to detect all possible input formats.

The return is for all functions a dataframe containing the data and a dictionary containing the parsed metadata.
Independent of the input format the columns and metadata-names should be identical. Other functions in this module
expect these naming conventions.
"""

import glob
import sys

import pandas as pd
import numpy as np
import re
from dateutil import parser as duparser
import datetime as dt

# Current software-versions. Used to display warnings if a newer logfiles is loaded.
CURRENT_WORKBENCH_VERSION = "1.5.4"
CURRENT_DEVELOPERTOOL_VERSION = "162"


def parse(fname: str) -> tuple[pd.DataFrame, dict]:
    """Reads any pyroscience textfile. Not .pyr files! Returns a dataframe and a dict with metadata.

    :param fname: path to the textfile
    """
    with open(fname, "r", encoding="latin1") as f:
        firstline = f.readlines(50)[0]
        nextthousand = f.read(1000)
    if "--- Experiment ---" in firstline or "--- System ---" in firstline:
        if "FirePlate" in nextthousand:
            return read_fireplate_workbench(fname)
        return read_workbench(fname)
    elif firstline.startswith("#Info	PyroSimpleLogger"):
        return read_developertool(fname)
    elif firstline.startswith("#Info	Device Log"):
        return read_aquaphoxlogger(fname)
    elif firstline.startswith("#Log_File"):
        return read_fsgo2(fname)
    elif firstline.startswith("#FDO2 Logger"):
        return read_fdo2_logger(fname)
    else:
        raise ValueError(f"Could not identify logfile: {fname}. Exiting.")


def read_workbench(fname: str) -> tuple[pd.DataFrame, dict]:
    """Loads and parses a Workbench file and returns a pandas DataFrame and a dictionary with metadata

    :param fname: file name of the logfile
    :return: (DataFrame, metadata-dict)
    """
    # first load header lines
    lines = []
    with open(fname, "r", encoding="latin1") as f:
        for line in f:
            if line.startswith("#"):
                line = line[1:]
            lines.append(line[:-1])
            if len(lines) > 50:
                break
    if lines[0].endswith("\t"):  # might not be the best method, but should detect workbench summary files
        raise ValueError('Pass a logfile for an individual channel (Found in "ChannelData").')

    metadata = {}
    l = 0
    # get experiment notes
    if not "--- Experiment ---" in lines[0]:
        print("Warning: Experiment section not found in logfile", file=sys.stderr)
    else:
        metadata["experiment_name"] = lines[1]
        l = 2
        metadata["experiment_description"] = ""
        while not lines[l].startswith("--- System ---"):
            metadata["experiment_description"] += lines[l] + "\n"
            l += 1

    # get system data
    if not "--- System ---" in lines[l]:
        raise ValueError("System section not found in logfile")
    match = re.search(r"(Workbench \S+)", lines[l + 1])
    if not match:
        raise ValueError("Unable to parse Workbench version!")
    metadata["software_version"] = match.groups()[0]
    if metadata["software_version"].rsplit(maxsplit=1)[-1][1:6] > CURRENT_WORKBENCH_VERSION:
        print("Warning! Unknown Workbench version! Please update pyrotoolbox.", file=sys.stderr)
    l += 3
    # get instrument data
    if not "--- Instrument ---" in lines[l]:
        raise ValueError("Instrument section not found in logfile")
    serial_number = ""
    if metadata["software_version"].rsplit(maxsplit=1)[-1][1:6] <= "1.4.7":
        match = re.match(r"Device: (.+) SN:(\S+) Firmware:(\S+) Build:(\S+)", lines[l + 1])
        if not match:
            raise ValueError("Unable to parse instrument information!")
        device, uid, firmware, build = match.groups()
    else:
        match = re.match(r"Device: (.+) SN:(\S+) UiD:(\S+) Firmware:(\S+) Build:(\S+)", lines[l + 1])
        if not match:
            raise ValueError("Unable to parse instrument information!")
        device, serial_number, uid, firmware, build = match.groups()
    firmware = firmware + ":" + build
    metadata["device"] = device
    metadata["device_serial"] = serial_number
    metadata["uid"] = uid
    metadata["firmware"] = firmware

    l += 2
    # get channel data
    if not "--- Channel ---" in lines[l]:
        raise ValueError("Channel section not found in logfile")
    match = re.match(r"Channel \[.*Ch\.(\d)\] - (.*) - (.*)", lines[l + 1])
    if not match:  # might be PT100
        match = re.match(r"Channel \[.*(T\d)\] - (.*)", lines[l + 1])
        if not match:
            raise ValueError("Unable to parse Channel information!")
        channel, sensor_type = match.groups()
        metadata["channel"] = channel
    else:  # non pt100 sensors
        channel, sensor_type, sensor_code = match.groups()
        metadata["channel"] = int(channel)
        metadata["sensor_code"] = sensor_code.strip()

    l += 2
    if sensor_type in ("pH Sensor", "Oxygen Sensor", "Optical Temperature Sensor"):
        # get settings and calibration
        if not lines[l].startswith("--- Settings & Calibration ---"):
            raise ValueError("Settings and Calibration section not found in logfile")
        metadata["settings"] = _parse_workbench_settings(lines[l + 1], lines[l + 2])

        metadata["calibration"] = _parse_workbench_calibration(
            metadata["settings"]["analyte"], lines[l + 3], lines[l + 4]
        )

        l += 5

    # get header count
    header = 0
    while not "--- Measurement Data ---" in lines[header]:
        header += 1
        if header > len(lines):
            raise ValueError("Could not find start of data")

    if sensor_type == "pH Sensor":
        if metadata["software_version"].count(".") <= 2:  # old Version format hat only 2 dots
            usecols = [0, 1, 2, 4, 5, 6, 7, 8]
        else:
            if isinstance(metadata["settings"]["temperature"], str) and metadata["settings"]["temperature"].startswith(
                "Optical Temperature Sensor"
            ):
                usecols = [0, 1, 2, 3, 5, 6, 7, 8, 9, 16]
            else:
                usecols = [0, 1, 2, 3, 5, 6, 7, 8, 9, 13]
    elif sensor_type == "Oxygen Sensor":
        if metadata["software_version"].count(".") <= 2:  # old Version format hat only 2 dots
            usecols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 17]
        elif metadata["software_version"] <= "Workbench V1.0.1.808":
            usecols = [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 15, 20]
        else:
            if isinstance(metadata["settings"]["temperature"], str) and metadata["settings"]["temperature"].startswith(
                "Optical Temperature Sensor"
            ):
                usecols = [0, 1, 2, 3, 4, 5, 6, 7, 11, 19]
            else:
                usecols = [0, 1, 2, 3, 4, 5, 6, 7, 11, 16]
    elif sensor_type == "Optical Temperature Sensor":
        usecols = [0, 1, 2, 3, 4, 5, 6, 7]
    elif sensor_type == "PT100 Temperature Sensor":
        usecols = [0, 1, 2, 3, 4]
    else:
        raise ValueError("Unknown Sensor type: " + sensor_type)

    df = pd.read_csv(
        fname,
        skiprows=header + 1,
        skip_blank_lines=False,
        encoding="latin1",
        usecols=usecols,
        sep="\t",
        na_values=[
            "NaN",
            ">NaN",
            ">8.5",
            "<5.5",
            ">9.5",
            "<6.5",
            ">7.5",
            "<5.5",
            ">6.5",
            "<4.5",
            "<3.5",
            "<4",
            ">8",
            "<5",
        ],
    )
    df.index = pd.to_datetime(df.iloc[:, 0] + " " + df.iloc[:, 1], dayfirst=True)
    df.drop([df.columns[0], df.columns[1]], axis=1, inplace=True)
    df.columns = [c.split(" [")[0].strip() for c in df.columns]  # cut off e.g. [A Ch.1 Main]

    # re-encode status
    def reencode_status(s: str):
        if s == "OK":
            return 0
        if s == "NotOK()":  # This is a bug in the workbench. Just create a new error code
            return 1 << 16
        l = s[6:-1].split(",")
        status = 0
        for i in l:
            if i in ("12", "13"):
                status |= 2
            elif i in ("11", "14", "15"):  # TODO is 15 the auto amp warning?
                continue
            else:
                status |= 1 << int(i)
        return status

    df["Status"] = df["Status"].map(reencode_status)

    df = df.rename(
        columns={
            "Date_time": "date_time",
            "dt (s)": "time_s",
            "Oxygen (%O2)": "oxygen_%O2",
            "Oxygen (%air sat.)": "oxygen_%airsat",
            "Oxygen (%air sat)": "oxygen_%airsat",  # with and without . is possible
            "Oxygen (mbar)": "oxygen_hPa",
            "Oxygen (Torr)": "oxygen_torr",
            "Oxygen (µM)": "oxygen_µM",
            "Oxygen (µmol/L)": "oxygen_µM",
            "Oxygen (mg/L)": "oxygen_mg/L",  # todo
            "Oxygen (µg/L)": "oxygen_µg/L",
            "Oxygen (mL/L)": "oxygen_mL/L",
            "Oxygen (hPa)": "oxygen_hPa",
            "dphi (°)": "dphi",
            "Signal Intensity (mV)": "signal_intensity",
            "Ambient Light (mV)": "ambient_light",
            "Status": "status",
            "Sample Temp. (°C)": "sample_temperature",
            "Case Temp. (°C)": "case_temperature",
            "Fixed Temp (°C)": "fixed_temperature",
            "Pressure (mbar)": "pressure",
            "pH (pH)": "pH",
            "R": "R",
            "Optical Temp. (°C)": "optical_temperature",
            "Idev (nm)": "ldev",
            "ldev (nm)": "ldev",
        }
    )
    df.index.name = "date_time"

    return df, metadata


def _parse_workbench_settings(line1: str, line2: str) -> dict:
    """Returns a dict with the following entries:

    'duration': duration of the flash, str
    'intensity': intensity of the flash, str
    'amp': signal amplification factor, str
    'frequency': modulation frequency, str
    'crc_enable': Cyclic Redundancy Check enabled, bool
    'write_lock': write lock enabled, bool
    'auto_flash_duration': automatic flash duration adjustment, bool
    'auto_amp': automatic amplification reduction, bool
    'analyte': 'none', 'oxygen', 'temperature' or 'pH'
    'fiber_type': '230 um', '430 um' or '1 mm'
    'temperature': temperature setting, str or float
    'pressure': pressure setting, str or float
    'salinity': salinity of the sample, float

    This function must return compatible dictionaries to _parse_simplelogger_settings
    """
    d = {}
    for name, value in zip(line1.split("\t")[1:], line2.split("\t")[1:]):
        if value == "TRUE":
            value = True
        elif value == "FALSE":
            value = False
        else:
            try:
                value = int(value)
            except:
                pass
        d[name] = value
    if d["Radio Temp"] == "External Temperature Sensor":
        temperature = "external sensor"
    elif d["Radio Temp"] == "Internal Temperature Sensor":
        temperature = "internal sensor"
    elif d["Radio Temp"] == "Optical Temperature":
        temperature = "Optical Temperature Sensor on Channel {}".format(d["Opt. Temp. Chan."])
    elif d["Radio Temp"] in ("Fixed", "Fixed Temperature ('C)"):
        temperature = float(d["Temperature (°C)"])
    else:
        print("unknown temperature setting: ", d["Radio Temp"], file=sys.stderr)
        temperature = "unknown"
    if d["Radio Pressure"] == "Internal Pressure Sensor":
        pressure = "internal sensor"
    elif d["Radio Pressure"] == "Fixed Pressure (mbar)":
        pressure = float(d["Pressure (mbar)"])
    else:
        print("unknown pressure setting", d["Radio Pressure"], file=sys.stderr)
        pressure = "unknown"

    r = {
        "duration": d["Duration"],
        "intensity": d["Intensity"].split(" ")[0],
        "amp": d["Amp"].split("(")[1][:-1],
        "frequency": d["Frequency (Hz)"],
        "crc_enable": d["Crc Enable"],
        "write_lock": d["Write Lock"],
        "auto_flash_duration": d["Autom. Flash Duration"],
        "auto_amp": d["Autom. Amp Level"],
        "analyte": d["Analyte"],
        "fiber_type": d["Fiber Type"],
        "temperature": temperature,
        "pressure": pressure,
        "salinity": float(d["Salinity (g/l)"]),
    }
    if "Fiber Length (mm)" in d:
        r["fiber_length_mm"] = d["Fiber Length (mm)"]  # introduced with FW4.10

    return r


def _parse_workbench_calibration(analyte: str, line1: str, line2: str) -> dict:
    calibration = {}
    if analyte == "oxygen":
        rename_dict = {
            "lastCal1": "date_calibration_high",
            "lastCal2": "date_calibration_zero",
            "dphi 100% (°)": "dphi100",
            "dphi 0% (°)": "dphi0",
            "f": "f",
            "m": "m",
            "F(Hz)": "freq",
            "tt(%/K)": "tt",
            "kt(%/K)": "kt",
            "Background Amplitude (mV)": "bkgdAmpl",
            "Background dphi (°)": "bkgdDphi",
            "mt(1/K)": "mt",
            "Air Pressure (mbar)": "pressure",
            "Temperature (°C)": "temp100",
            "Humidity (%RH)": "humidity",
            "Temperature (°C) at 0%": "temp0",
            "Partial Volume of Oxygen (%O2)": "percentO2",
        }
    elif analyte == "pH":
        rename_dict = {
            "lastCal1": "date_calibration_acid",
            "lastCal2": "date_calibration_base",
            "lastCal3": "date_calibration_offset",
            "R1": "R1",
            "pH1 (pH)": "pH1",
            "temp1 (°C)": "temp1",
            "salinity1 (g/L)": "salinity1",
            "R2": "R2",
            "pH2 (pH)": "pH2",
            "temp2 (°C)": "temp2",
            "salinity2 (g/L)": "salinity2",
            "offset (pH)": "offset",
            "dPhi_ref (°)": "dphi_ref",
            "attenuation coefficient (1/m)": "attenuation_coefficient",
            "bkgdAmpl (mV)": "bkgdAmpl",
            "bkgdDphi (°)": "bkgdDphi",
            "dsf_dye": "dsf_dye",
            "dtf_dye": "dtf_dye",
            "pka": "pka",
            "slope": "slope",
            "bottom_t": "bottom_t",
            "top_t": "top_t",
            "slope_t": "slope_t",
            "pka_t": "pka_t",
            "pka_is1": "pka_is1",
            "pka_is2": "pka_is2",
            ###### < FW4.10 registers
            "pka (pH)": "pka",
            "pka_t (pH/K)": "pka_t",
            "dyn_t (1/K)": "dyn_t",
            "bottom_t (1/K)": "bottom_t",
            "slope_t (1/K)": "slope_t",
            "f": "f",
            "lambda_std (nm)": "lambda_std",
            "dPhi1 (°)": "dphi1",
            "ldev1 (nm)": "ldev1",
            "dPhi2 (°)": "dphi2",
            "ldev2 (nm)": "ldev2",
            "Aon": "Aon",
            "Aoff": "Aoff",
        }
    elif analyte == "temperature":
        rename_dict = {
            "lastCal1": "date_calibration_offset",
            "M": "M",
            "N": "N",
            "C": "C",
            "Tofs (K)": "temp_offset",
            "Background Amplitude (mV)": "bkgdAmpl",
            "Background dphi (°)": "bkgdDphi",
        }
    elif analyte == "none":
        rename_dict = {}
    else:
        print("Warning! Unknown analyte. Please update!", file=sys.stderr)
        return {}
    # Bugfix for workbench 1.5.4.2482 and pH
    if line1.startswith("Calibration:WellNr"):
        line1 = line1.replace("Calibration:WellNr\t", "Calibration:\tWellNr")
        line2 = "\t" + line2.replace("/t#", "")
    if line2.endswith("Not calibrated"):
        return {k: None for k in rename_dict.values()}
    for name, value in zip(line1.split("\t")[1:], line2.split("\t")[1:]):
        if name in rename_dict:
            name = rename_dict[name]
        else:
            if name not in ("Ksv (1/mbar)", "Method", "Tofs(K)", "WellNr"):
                print(f"skipping {name}. value: {value}", file=sys.stderr)
            continue
        if name.startswith("date_calibration"):
            if value in ("01/01/2001", "01.01.2001", "01.01.2000", "Not calibrated"):
                value = None
            else:
                value = duparser.parse(value, dayfirst=True)
        else:
            value = round(float(value), 6)
        if name in ("kt", "tt") and isinstance(value, float):  # convert from %/K to 1/K
            value /= 100
            value = round(value, 6)
        calibration[name] = value
    return calibration


def read_fireplate_workbench(fname: str) -> tuple[pd.DataFrame, dict]:
    """Loads and parses a Workbench file of a fireplate and returns a pandas DataFrame and a dictionary with metadata

    :param fname: path to the lofile
    :return: DataFrame, metadata-dict
    """

    def channel_number_to_coordinate(channel: str):
        """Converts either '1' or 'A1' to 'A01'"""
        channel = channel.strip()
        try:  # works for Workbench > 1.5.4
            channel = int(channel)
            return "ABCDEFGH"[(channel - 1) // 12] + f"{(channel - 1) % 12 + 1:0>2}"
        except:
            pass
        if len(channel) == 3:
            return channel
        elif len(channel) == 2:
            return channel[0] + "0" + channel[1]
        else:
            raise ValueError(f'Invalid channel name "{channel}"')

    # first load header lines
    lines = []
    with open(fname, "r", encoding="latin1") as f:
        for line in f:
            if line.startswith("#"):
                line = line[1:]
            lines.append(line[:-1])
            if len(lines) > 200:
                break

    metadata = {}
    l = 0
    # get experiment notes
    if not "--- Experiment ---" in lines[0]:
        print("Warning: Experiment section not found in logfile", file=sys.stderr)
    else:
        metadata["experiment_name"] = lines[1]
        l = 2
        metadata["experiment_description"] = ""
        while not lines[l].startswith("--- System ---"):
            metadata["experiment_description"] += lines[l] + "\n"
            l += 1

    # get system data
    if not "--- System ---" in lines[l]:
        raise ValueError("System section not found in logfile")
    match = re.search(r"(Workbench \S+)", lines[l + 1])
    if not match:
        raise ValueError("Unable to parse Workbench version!")
    metadata["software_version"] = match.groups()[0]
    l += 3
    # get instrument data
    if not "--- Instrument ---" in lines[l]:
        raise ValueError("Instrument section not found in logfile")
    match = re.match(r"Device: (.+) SN:(\S+) UiD:(\S+) Firmware:(\S+) Build:(\S+)", lines[l + 1])
    if not match:
        raise ValueError("Unable to parse instrument information!")
    device, serial_number, uid, firmware, build = match.groups()
    firmware = firmware + ":" + build
    metadata["device"] = device
    metadata["device_serial"] = serial_number
    metadata["uid"] = uid
    metadata["firmware"] = firmware

    l += 2
    # get channel data
    if not "--- Channel ---" in lines[l]:
        raise ValueError("Channel section not found in logfile")
    match = re.match(r"Group \[.*Gr\.(\d)\] - (.*) - (.*) - Well numbers: (.*)", lines[l + 1])
    channel, sensor_type, sensor_code, well_numbers = match.groups()
    metadata["group"] = int(channel)
    metadata["sensor_code"] = sensor_code.strip()
    metadata["channels"] = [channel_number_to_coordinate(i) for i in well_numbers.split(",")]

    l += 2
    if sensor_type not in ("pH Sensor", "Oxygen Sensor", "Optical Temperature Sensor"):
        raise ValueError(f"Unknown sensor type {sensor_type}")

    # get settings and calibration
    if not lines[l].startswith("--- Settings & Calibration ---"):
        raise ValueError("Settings and Calibration section not found in logfile")
    metadata["settings"] = _parse_workbench_settings(lines[l + 1], lines[l + 2])

    metadata["calibration"] = {}
    for i, channel in enumerate(metadata["channels"]):
        metadata["calibration"][channel] = _parse_workbench_calibration(
            metadata["settings"]["analyte"], lines[l + 3], lines[l + 4 + i]
        )

    l += 5 + i

    # get header count
    header = 0
    while not "--- Measurement Data ---" in lines[header]:
        header += 1
        if header > len(lines):
            raise ValueError("Could not find start of data")

    if sensor_type == "Oxygen Sensor":
        # last two are case temp and pressure
        usecols = list(range(0, 3 + len(metadata["channels"]) * 5)) + [
            3 + len(metadata["channels"]) * 5 + 3,
            3 + len(metadata["channels"]) * 5 + 8,
        ]
    elif sensor_type == "Optical Temperature Sensor":
        usecols = list(range(0, 3 + len(metadata["channels"]) * 5))
    elif sensor_type == "pH Sensor":
        usecols = [0, 1, 2]
        for i in range(len(metadata["channels"])):
            for j in range(1, 7):
                usecols.append(3 + i * 7 + j)
        # case temp
        usecols.append(3 + len(metadata["channels"]) * 7 + 3)
    else:
        raise ValueError("Unknown Sensor type: " + sensor_type)

    df = pd.read_csv(
        fname,
        skiprows=header + 1,
        skip_blank_lines=False,
        encoding="latin1",
        usecols=usecols,
        sep="\t",
        na_values=[
            "NaN",
            ">NaN",
            ">8.5",
            "<5.5",
            ">9.5",
            "<6.5",
            ">7.5",
            "<5.5",
            ">6.5",
            "<4.5",
            "<3.5",
            "<4",
            ">8",
            "<5",
        ],
    )
    df.index = pd.to_datetime(df.iloc[:, 0] + " " + df.iloc[:, 1], dayfirst=True)
    df.drop([df.columns[0], df.columns[1]], axis=1, inplace=True)

    def rename_column(column: str):
        if column.strip().startswith("dt (s)"):
            return "time_s"
        if column.strip().startswith("Pressure"):
            return "pressure"
        if column.strip().startswith("Case Temp"):
            return "case_temperature"

        col, info = column.split(" [")
        channel = info[:-6].rsplit(".")[-1]
        channel_name = channel_number_to_coordinate(channel)
        name = {
            "Date_time": "date_time",
            "dt (s)": "time_s",
            "Oxygen (%O2)": "oxygen_%O2",
            "Oxygen (%air sat.)": "oxygen_%airsat",
            "Oxygen (%air sat)": "oxygen_%airsat",  # with and without . is possible
            "Oxygen (mbar)": "oxygen_hPa",
            "Oxygen (Torr)": "oxygen_torr",
            "Oxygen (µM)": "oxygen_µM",
            "Oxygen (µmol/L)": "oxygen_µM",
            "Oxygen (mg/L)": "oxygen_mg/L",
            "Oxygen (µg/L)": "oxygen_µg/L",
            "Oxygen (mL/L)": "oxygen_mL/L",
            "Oxygen (hPa)": "oxygen_hPa",
            "dphi (°)": "dphi",
            "Signal Intensity (mV)": "signal_intensity",
            "Ambient Light (mV)": "ambient_light",
            "Status": "status",
            "Sample Temp. (°C)": "sample_temperature",
            "Case Temp. (°C)": "case_temperature",
            "Fixed Temp (°C)": "fixed_temperature",
            "Pressure (mbar)": "pressure",
            "pH (pH)": "pH",
            "pH": "pH",
            "R": "R",
            "Optical Temp. (°C)": "optical_temperature",
        }[col]
        return channel_name + "_" + name

    def reencode_status(s: str):
        if s == "OK":
            return 0
        l = s[6:-1].split(",")
        status = 0
        for i in l:
            if i in ("12", "13"):
                status |= 2
            elif i in ("11", "14", "15"):  # TODO is 15 the auto amp warning?
                continue
            else:
                status |= 1 << int(i)
        return status

    df.columns = [rename_column(i) for i in df.columns]

    for c in list(df.filter(regex="status")):
        df[c] = df[c].map(reencode_status)

    df.index.name = "date_time"

    return df, metadata


def read_developertool(fname: str) -> tuple[pd.DataFrame, dict]:
    """Loads and parses a logfile from the PyroDeveloperTool

    :param fname: path to the logfile
    :return: (DataFrame, metadata-dict)
    """
    # first load header lines
    lines = []
    with open(fname, "r", encoding="latin1") as f:
        for line in f:
            lines.append(line[:-1])
            if len(lines) > 30:
                break

    metadata = {}
    # get experiment notes
    metadata["software_version"] = lines[0].split("\t", maxsplit=1)[1]

    if metadata["software_version"].split()[1][1:] > CURRENT_DEVELOPERTOOL_VERSION:
        print(
            f'Warning! Unknown DeveloperTool version "{metadata["software_version"]}"! Please update pyrotoolbox.',
            file=sys.stderr,
        )

    metadata["experiment_name"] = lines[2].split("\t", maxsplit=1)[1]
    metadata["experiment_description"] = lines[3].split("\t", maxsplit=1)[1]

    metadata["device"] = lines[4].split("\t", maxsplit=1)[1]
    metadata["uid"] = lines[6].split("\t", maxsplit=1)[1]
    metadata["firmware"] = lines[7].split("\t", maxsplit=1)[1] + ":" + lines[8].split("\t", maxsplit=1)[1]
    metadata["channel"] = lines[12].split("\t")[1]

    # parse settings
    metadata["settings"] = _parse_developertool_settings(lines[14], lines[15])

    # parse calibration
    metadata["calibration"] = _parse_developertool_calibration(metadata["settings"]["analyte"], lines[16], lines[17])

    # parse referenceSettings
    metadata["settings"].update(_parse_developertool_ref_settings(lines[20], lines[21]))

    # parse calibration status
    metadata["calibration"].update(_parse_developertool_calibration_status(metadata["settings"]["analyte"], lines[23]))

    # get header count
    header = 0
    while not lines[header].startswith("DateTime (YYYY-MM-DD hh:mm:ss)"):
        header += 1
        if header > len(lines):
            raise ValueError("Could not find start of data")

    # 0 -> datetime
    # 1 fraction of second
    # 2 Comment
    # 3 status
    # 4 dphi
    # 5 uM
    # 6 mbar
    # 7 airSat
    # 8 tempSample
    # 9 tempCase
    # 10 signalIntensity
    # 11 ambient light
    # 12 pressure
    # 13 humidity
    # 14 resistortemp
    # 15 percento2
    # 16 tempOptical
    # 17 ph
    # 18 R
    # 19 forward: raw results
    if metadata["settings"]["analyte"] == "oxygen":
        usecols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]
    elif metadata["settings"]["analyte"] == "temperature":
        usecols = [0, 1, 2, 3, 4, 8, 9, 10, 11, 12, 13, 16]
    elif metadata["settings"]["analyte"] == "pH":
        usecols = [0, 1, 2, 3, 4, 8, 9, 10, 11, 12, 13, 17, 18]
    elif metadata["settings"]["analyte"] == "none":
        usecols = [0, 1, 2, 3, 4, 8, 9, 10, 11, 12, 13]
    else:
        raise ValueError(f'Unknown analyte "{metadata["settings"]["analyte"]}". Please update software.')

    df = pd.read_csv(
        fname,
        skiprows=header,
        encoding="latin1",
        usecols=usecols,
        sep="\t",
        skip_blank_lines=False,
        na_values=["-300000"],
        dtype={"Comment": "object", "Fraction of Second (ms)": "string"},
    )
    df.index = pd.to_datetime(df.iloc[:, 0] + " " + df.iloc[:, 1].astype(str), format="%Y-%m-%d %H:%M:%S %f")
    df.drop([df.columns[0], df.columns[1]], axis=1, inplace=True)

    df = (df.select_dtypes(exclude="object") / 1000).combine_first(df)  # to exclude 'comment' column
    df["status"] *= 1000
    if "R (0.000001)" in df.columns:
        df["R (0.000001)"] /= 1000
    if "umolar (0.000001 umol/L)" in df.columns:  # oxygenx1000
        df["umolar (0.000001 umol/L)"] /= 1000
    if "mbar (0.000001 mbar)" in df.columns:  # oxygenx1000
        df["mbar (0.000001 mbar)"] /= 1000
    if "airSat (0.000001 %air sat)" in df.columns:  # oxygenx1000
        df["airSat (0.000001 %air sat)"] /= 1000
    if "percentO2 (0.000001 %O2)" in df.columns:  # oxygenx1000
        df["percentO2 (0.000001 %O2)"] /= 1000

    rename_dict = {
        "Comment": "comment",
        "status": "status",
        "dphi (0.001 °)": "dphi",
        "umolar (0.001 umol/L)": "oxygen_µM",
        "mbar (0.001 mbar)": "oxygen_hPa",
        "airSat (0.001 %air sat)": "oxygen_%airsat",
        "umolar (0.000001 umol/L)": "oxygen_µM",
        "mbar (0.000001 mbar)": "oxygen_hPa",
        "airSat (0.000001 %air sat)": "oxygen_%airsat",
        "tempSample (0.001 °C)": "sample_temperature",
        "tempCase (0.001 °C)": "case_temperature",
        "signalIntensity (0.001 mV)": "signal_intensity",
        "ambientLight (0.001 mV)": "ambient_light",
        "pressure (0.001 mbar)": "pressure",
        "humidity (0.001 %RH)": "humidity",
        # 'resistorTemp (0.001 Ohm or 0.001 mV)',
        "percentO2 (0.001 %O2)": "oxygen_%O2",
        "percentO2 (0.000001 %O2)": "oxygen_%O2",
        "tempOptical (0.001 °C)": "optical_temperature",
        "pH (0.001 pH)": "pH",
        "R (0.000001)": "R",
        "ldev (0.001 nm)": "ldev",
    }

    df.rename(columns=rename_dict, inplace=True)
    df.index.name = "date_time"
    df["time_s"] = np.round((df.index - df.index[0]).total_seconds(), 3)

    return df, metadata


def _parse_developertool_settings(line1: str, line2: str) -> dict:
    """Returns a dict with the following entries:

    'duration': duration of the flash, str
    'intensity': intensity of the flash, str
    'amp': signal amplification factor, str
    'frequency': modulation frequency, str
    'crc_enable': Cyclic Redundancy Check enabled, bool
    'write_lock': write lock enabled, bool
    'auto_flash_duration': automatic flash duration adjustment, bool
    'auto_amp': automatic amplification reduction, bool
    'analyte': 'none', 'oxygen', 'temperature' or 'pH'
    'fiber_type': '230 um', '430 um' or '1 mm'
    'temperature': temperature setting, str or float
    'pressure': pressure setting, str or float
    'salinity': salinity of the sample, float

    This function must return compatible dictionaries to _parse_workbench_settings
    """
    d = {}
    for name, value in zip(line1.split("\t")[1:], line2.split("\t")[1:]):
        try:
            value = int(value)
        except:
            pass
        if name == "temp (0.001 °C)":
            if value == -300000:
                d["temperature"] = "external sensor"
            elif value == -299999:
                d["temperature"] = "internal sensor"
            elif value < -300000:
                d["temperature"] = "Optical Temperature Sensor on Channel {}".format(-value - 300000)
            else:
                d["temperature"] = value / 1000
        elif name == "pressure (0.001 mbar)":
            if value == -1:
                d["pressure"] = "internal sensor"
            else:
                d["pressure"] = value / 1000
        elif name == "salinity (0.001 g/L)":
            d["salinity"] = value / 1000
        elif name == "duration (1=1ms, 8=128ms)":
            d["duration"] = f"{2 ** (value - 1)}ms"
        elif name == "intensity (0=10%, 7=100%)":
            d["intensity"] = ("10%", "15%", "20%", "30%", "40%", "60%", "80%", "100%")[value]
        elif name == "amp (3=40x, 4=80x, 5=200x, 6=400x)":
            d["amp"] = ("1x", "unknown", "unknown", "unknown", "40x", "200x", "400x")[value]
        elif name == "frequency (Hz)":
            d["frequency"] = value
        elif name == "crcEnable":
            d["crc_enable"] = bool(value)
        elif name == "writeLock":
            d["write_lock"] = bool(value)
        elif name in (
            "options (1=autoFlashDur., 2=autoAmp, 4= 1000xOxygen)",
            "options (bit0=autoFlashDur., bit1=autoAmpl., bit2=1000xOxygen)",
            "autoRange (0=disabled, 1=autoFlashDur., 2=autoAmp, 3= autoFlashDur.+autoAmp)",
        ):
            d["auto_flash_duration"] = bool(value & 1)
            d["auto_amp"] = bool(value & 2)
            # d['oxygen_x1000'] = value & 4  # skipped for compatibility with workbench
        elif name == "broadcast":
            pass  # skipped
        elif name == "analyte (0=none, 1=O2, 2=T, 3=pH, 4=CO2)":
            d["analyte"] = ("none", "oxygen", "temperature", "pH")[value]
        elif name == "fiberType (0=230um, 1=430um, 2=1mm)":
            d["fiber_type"] = ("230 um", "430 um", "1 mm")[value]
        elif name == "fiberLength (mm)":
            d["fiber_length_mm"] = value
        elif name == "dual frequency (Hz)":
            pass
        else:
            raise ValueError(f'Unknown setting: "{name}"')
    return d


def _parse_developertool_calibration(analyte: str, line1: str, line2: str) -> dict:
    calibration = {}
    if analyte == "oxygen":
        rename_dict = {
            "dphi0 (0.001 °)": ("dphi0", 1e3),
            "dphi100 (0.001 °)": ("dphi100", 1e3),
            "temp0 (0.001 °C)": ("temp0", 1e3),
            "temp100 (0.001 °C)": ("temp100", 1e3),
            "pressure (0.001 mbar)": ("pressure", 1e3),
            "humidity (0.001 %RH)": ("humidity", 1e3),
            "f (0.001)": ("f", 1e3),
            "m (0.001)": ("m", 1e3),
            "calFreq (Hz)": ("freq", 1),
            "tt (10e-5/K)": ("tt", 1e5),
            "kt (10e-5/K)": ("kt", 1e5),
            "bkgdAmp (0.001 mV)": ("bkgdAmpl", 1e3),
            "bkgdDphi (0.001 °)": ("bkgdDphi", 1e3),
            # 'useKsv':
            # 'ksv(10e-6 / mbar)':
            "ft (10e-6 / K)": ("ft", 1e6),
            "mt (10e-6/K)": ("mt", 1e6),
            # 'tempOffset (0.001 °C)': ('Tofs', 1e3),
            "percentO2 (0.001 %O2)": ("percentO2", 1e3),
        }
    elif analyte == "pH":
        rename_dict = {
            "R1 (0.000001)": ("R1", 1e6),
            "pH1 (0.001 pH)": ("pH1", 1e3),
            "temp1 (0.001 °C)": ("temp1", 1e3),
            "salinity1 (0.001 g/L)": ("salinity1", 1e3),
            "R2 (0.000001)": ("R2", 1e6),
            "pH2 (0.001 pH)": ("pH2", 1e3),
            "temp2 (0.001 °C)": ("temp2", 1e3),
            "salinity2 (0.001 g/L)": ("salinity2", 1e3),
            "offset (0.001 pH)": ("offset", 1e3),
            "dPhi_ref (0.001 °)": ("dphi_ref", 1e3),
            "att. coeff. (0.000001)": ("attenuation_coefficient", 1e6),
            "bkgdAmp (0.001 mV)": ("bkgdAmpl", 1e3),
            "bkgdDphi (0.001 °)": ("bkgdDphi", 1e3),
            "dsf_dye (0.000001)": ("dsf_dye", 1e6),
            "dtf_dye (0.000001)": ("dtf_dye", 1e6),
            "pka (0.001)": ("pka", 1e3),
            "slope (0.000001)": ("slope", 1e6),
            "bottom_t (0.000001)": ("bottom_t", 1e6),
            "top_t (0.000001)": ("top_t", 1e6),
            "slope_t (0.000001)": ("slope_t", 1e6),
            "pka_t (0.000001)": ("pka_t", 1e6),
            "pka_is1 (0.001)": ("pka_is1", 1e3),
            "pka_is2 (0.001)": ("pka_is2", 1e3),
            ###### < FW4.10 registers
            "pka (0.001 pH)": ("pka", 1e3),
            "slope (10e-6)": ("slope", 1e6),
            "salanity1 (0.001 g/L)": ("salinity1", 1e3),
            "salanity2 (0.001 g/L)": ("salinity2", 1e3),
            "pka_t (10e-6 pH/K)": ("pka_t", 1e6),
            "dyn_t (10e-6 1/K)": ("dyn_t", 1e6),
            "bottom_t (10e-6 1/K)": ("bottom_t", 1e6),
            "slope_t (10e-6 1/K)": ("slope_t", 1e6),
            "f (10e-6)": ("f", 1e6),
            "lambda_std (0.001 nm)": ("lambda_std", 1e3),
            "dPhi1 (0.001 °)": ("dphi1", 1e3),
            "ldev1 (0.001 nm)": ("ldev1", 1e3),
            "dPhi2 (0.001 °)": ("dphi2", 1e3),
            "ldev2 (0.001 nm)": ("ldev2", 1e3),
            "pka_is1 (10e-6)": ("pka_is1", 1e6),
            "pka_is2 (10e-6)": ("pka_is2", 1e6),
            "Aon (10e-6)": ("Aon", 1e6),
            "Aoff (10e-6)": ("Aoff", 1e6),
            #### aquaphox registers 410 (slightly different names)
            "R1 (10e-6)": ("R1", 1e6),
            "pH1 (0.001)": ("pH1", 1e3),
            "R2 (10e-6)": ("R2", 1e6),
            "pH2 (0.001)": ("pH2", 1e3),
            "offset (0.001)": ("offset", 1e3),
            "attenuation_coefficient (10e-6 1/m)": ("attenuation_coefficient", 1e6),
            "bkgdAmpl (0.001 mV)": ("bkgdAmpl", 1e3),
            "dsf_dye (10e-6)": ("dsf_dye", 1e6),
            "dtf_dye (10e-6)": ("dtf_dye", 1e6),
            "top_t (10e-6 1/K)": ("top_t", 1e6),
            #### aquaphox registers 405 (slightly different names)
            "slope (0.001)": ("slope", 1e3),
            "dyn_t (10e-6 1/K": ("dyn_t", 1e6),
            "Aon (0.001)": ("Aon", 1e3),
            "Aoff (0.001)": ("Aoff", 1e3),
        }
    elif analyte == "temperature":
        rename_dict = {
            "M (0.01)": ("M", 100),
            "N (0.01)": ("N", 100),
            "C (0.001)": ("C", 1e3),
            "Tofs (0.001 °C)": ("temp_offset", 1e3),
            "bkgdAmp (0.001 mV)": ("bkgdAmpl", 1e3),
            "bkgdDphi (0.001 °)": ("bkgdDphi", 1e3),
        }
    elif analyte == "none":
        rename_dict = {}
    else:
        print(f'Warning! Unknown analyte: "{analyte}". Please update!', file=sys.stderr)
        return {}
    for name, value in zip(line1.split("\t")[1:], line2.split("\t")[1:]):
        if name in rename_dict:
            name, factor = rename_dict[name]
        else:
            if name not in ("useKsv", "ksv (10e-6/mbar)", "-", "tempOffset (0.001 °C)"):
                print(f"skipping {name}. value: {value}", file=sys.stderr)
            continue
        value = round(float(value) / factor, 6)
        calibration[name] = value
    return calibration


def _parse_developertool_ref_settings(line1: str, line2: str) -> dict:
    d = {}
    for name, value in zip(line1.split("\t")[1:], line2.split("\t")[1:]):
        try:
            value = int(value)
        except:
            pass
        if name == "referenceMode (0=standard, 1=averaging, 2=smart averaging)":
            d["referenceMode"] = ("standard", "averaging", "smart averaging")[value]
        elif name == "refDurationAveragingMode (ms)":
            d["refDurationAveragingMode"] = value
        elif name == "refDurationStandardMode (ms)":
            d["refDurationStandardMode"] = value
        elif name == "timeLimitSmartAveragingMode (s)":
            d["timeLimitSmartAveragingMode "] = value
        else:
            raise ValueError(f'Unknown ref setting: "{name}"')
    return d


def _parse_developertool_calibration_status(analyte: str, line2: str) -> dict:
    if analyte == "oxygen":
        calibration_points = ["date_calibration_high", "date_calibration_zero"]
    elif analyte == "pH":
        calibration_points = ["date_calibration_acid", "date_calibration_base", "date_calibration_offset"]
    elif analyte == "temperature":
        calibration_points = ["date_calibration_offset"]
    elif analyte == "none":
        calibration_points = []
    else:
        print(f'Warning! Unknown analyte "{analyte}". Please update!', file=sys.stderr)
        return {}

    d = {}
    for name, value in zip(calibration_points, line2.split("\t")[1:]):
        if value in ("60000101", "10101", "0"):
            d[name] = None
        else:
            day = int(value[-2:])
            month = int(value[-4:-2])
            year = int("20" + value[-6:-4])
            minutes = int(value[:-6])
            d[name] = dt.datetime(year=year, month=month, day=day, hour=minutes // 60, minute=minutes % 60)
    return d


def read_developertool_directory(pattern: str = "*.txt"):
    """parses all files matching the pattern (default *.txt) and returns 3 dictionaries

        first dictionary is UID/Name-ChX -> List of Dataframes

        second dictionary is UID/Name-ChX -> List of metadata-dicts

        third dictionary is UID/Name-ChX -> List of filenames

    :param pattern: files to load. Default: *.txt
    """
    data = {}
    metadata = {}
    filenames = {}
    nof_files = len(glob.glob(pattern))
    i = 0
    for path in sorted(glob.glob(pattern)):
        i += 1
        print("parsing files {}/{}: {}".format(i, nof_files, path))
        # get UID. This will break in 2030. Have fun fixing that!
        name = path.split("/")[-1].split(" 202")[0][-16:]
        channel = path.rsplit("Ch", maxsplit=1)[-1].split(".txt")[0]
        name += "-" + channel
        d, m = read_developertool(path)
        if name not in data:
            data[name] = []
            metadata[name] = []
            filenames[name] = []
        data[name].append(d)
        metadata[name].append(m)
        filenames[name].append(path)

    print(115 * "-")
    print("Summary")
    print(115 * "-")
    max_keylen = max([len(k) for k in data.keys()])
    max_namelen = max(len(name) for names in filenames.values() for name in names) + 2
    print(f'{"Key":^{max_keylen}}    {"filenames":^{max_namelen}} datapoints')
    print(115 * "-")
    for key, d in data.items():
        print(f"{key:<{max_keylen}} ", end="")
        for i in range(len(d)):
            if i > 0:
                print((max_keylen + 1) * " ", end="")
            print(f"{i:>2} {filenames[key][i]:<{max_namelen}} {len(d[i]):>10}")
        print(115 * "-")

    return data, metadata, filenames


def read_aquaphoxlogger(fname: str) -> tuple[pd.DataFrame, dict]:
    """Loads and parses a logfile from an AquapHOx-Logger

    :param fname: path to the logfile
    :return: (DataFrame, metadata-dict)
    """
    # first load header lines
    lines = []
    with open(fname, "r", encoding="latin1") as f:
        for line in f:
            lines.append(line[:-1])
            if len(lines) > 40:
                break

    metadata = {}
    # get experiment notes

    metadata["experiment_name"] = lines[2].split("\t", maxsplit=1)[1]
    metadata["experiment_description"] = lines[3].split("\t", maxsplit=1)[1]

    metadata["device"] = lines[4].split("\t", maxsplit=1)[1]
    metadata["uid"] = lines[6].split("\t", maxsplit=1)[1]
    if lines[7].startswith("#Serial number"):  # introduced in firmware 410:6
        metadata["device_serial"] = lines[7].split("\t")[1]
        lines.pop(7)
    metadata["firmware"] = lines[7].split("\t", maxsplit=1)[1] + ":" + lines[8].split("\t", maxsplit=1)[1]
    metadata["software_version"] = "Firmware " + metadata["firmware"]  # firmware writes this logfiles
    metadata["channel"] = lines[12].split("\t")[1]

    metadata["settings"] = _parse_developertool_settings(lines[14], lines[15])

    metadata["calibration"] = _parse_developertool_calibration(metadata["settings"]["analyte"], lines[16], lines[17])

    if metadata["firmware"] >= "405":
        sensor_type, led_code, amp_code, middle, last = lines[23].split("\t")[1:6]
        metadata["sensor_code"] = (
            int(sensor_type).to_bytes(4, "big").decode("ascii").split("\x00")[0]
            + "ABCDEFGH"[int(led_code)]
            + str(int(amp_code) + 1)
            + f"-{middle:0>3}-{last:0>3}"
        )

        # parse calibration status
        metadata["calibration"].update(
            _parse_developertool_calibration_status(metadata["settings"]["analyte"], lines[25])
        )

        # parse referenceSettings
        metadata["settings"].update(_parse_developertool_ref_settings(lines[32], lines[33]))
    else:
        # parse referenceSettings
        metadata["settings"].update(_parse_developertool_ref_settings(lines[20], lines[21]))

    # get header count
    header = 0
    while not lines[header].startswith("DateTime (YYYY-MM-DD hh:mm:ss)"):
        header += 1
        if header > len(lines):
            raise ValueError("Could not find start of data")
    if metadata["firmware"] >= "410:6":
        header += 1

    # 0 -> datetime
    # 1 fraction of second
    # 2 Comment
    # 3 status
    # 4 dphi
    # 5 uM
    # 6 mbar
    # 7 airSat
    # 8 tempSample
    # 9 tempCase
    # 10 signalIntensity
    # 11 ambient light
    # 12 pressure
    # 13 humidity
    # 14 resistortemp
    # 15 percento2
    # 16 tempOptical
    # 17 ph
    # 18 R
    # 19 forward: empty registers
    if metadata["settings"]["analyte"] == "oxygen":
        usecols = [0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]
    elif metadata["settings"]["analyte"] == "temperature":
        usecols = [0, 3, 4, 8, 9, 10, 11, 12, 13, 16]
    elif metadata["settings"]["analyte"] == "pH":
        usecols = [0, 3, 4, 8, 9, 10, 11, 12, 13, 17, 18]
    elif metadata["settings"]["analyte"] == "none":
        usecols = [0, 3, 4, 8, 9, 10, 11, 12, 13]
    else:
        raise ValueError(f'Unknown analyte "{metadata["settings"]["analyte"]}". Please update software.')

    df = pd.read_csv(
        fname,
        skiprows=header,
        encoding="latin1",
        usecols=usecols,
        sep="\t",
        skip_blank_lines=False,
        na_values=["-300000"],
    )
    df.index = pd.to_datetime(df.iloc[:, 0])
    df.drop(df.columns[0], axis=1, inplace=True)
    df = (df.select_dtypes(exclude="object") / 1000).combine_first(df)  # to exclude 'comment' column
    df["status"] *= 1000
    if (
        metadata["settings"]["analyte"] == "pH"
        and metadata["firmware"].startswith("410")
        and "ldev (0.001 nm)" in df.columns
    ):  # workaround for wrong column name. Might not only be 410
        df["R (10e-6)"] = df["ldev (0.001 nm)"] / 1000
        del df["ldev (0.001 nm)"]

    rename_dict = {
        "Comment": "comment",
        "status": "status",
        "dphi (0.001 °)": "dphi",
        "umolar (0.001 umol/L)": "oxygen_µM",
        "mbar (0.001 mbar)": "oxygen_hPa",
        "airSat (0.001 %air sat)": "oxygen_%airsat",
        "tempSample (0.001 °C)": "sample_temperature",
        "tempCase (0.001 °C)": "case_temperature",
        "signalIntensity (0.001 mV)": "signal_intensity",
        "ambientLight (0.001 mV)": "ambient_light",
        "pressure (0.001 mbar)": "pressure",
        "humidity (0.001 %RH)": "humidity",
        # 'resistorTemp (0.001 Ohm or 0.001 mV)',
        "percentO2 (0.001 %O2)": "oxygen_%O2",
        "tempOptical (0.001 °C)": "optical_temperature",
        "pH (0.001 pH)": "pH",
        "R (10e-6)": "R",
        "ldev (0.001 nm)": "ldev",
    }

    df.rename(columns=rename_dict, inplace=True)
    df.index.name = "date_time"
    df["time_s"] = np.round((df.index - df.index[0]).total_seconds(), 3)

    return df, metadata


def read_fsgo2(fname: str) -> tuple[pd.DataFrame, dict]:
    """Loads and parses a logfile from a FSGO2

    :param fname: path to the logfile
    :return: (DataFrame, metadata-dict)
    """
    lines = []
    with open(fname, "r", encoding="latin1") as f:
        for line in f:
            lines.append(line[:-1])
            if len(lines) > 30:
                break

    metadata = {}
    metadata["experiment_name"] = lines[0].split("\t", maxsplit=1)[1]
    metadata["experiment_description"] = lines[1].split("\t", maxsplit=1)[1]

    metadata["device"] = lines[2].split("\t", maxsplit=1)[1]
    metadata["firmware"] = lines[3].split("\t", maxsplit=1)[1]
    metadata["uid"] = lines[4].split("\t", maxsplit=1)[1]
    metadata["software_version"] = "Firmware " + metadata["firmware"]  # firmware writes this logfiles

    # parse settings
    settings = {"analyte": "oxygen"}
    for k, v in zip(lines[10].split("\t")[1:], lines[11].split("\t")[1:]):
        try:
            v = int(v)
        except:
            pass
        if k == "Temperature":
            if v == "Case":  # untested!
                settings["temperature"] = "external sensor"
            elif v == "Sensor":
                settings["temperature"] = "internal sensor"
            else:
                settings["temperature"] = v  # untested!
        elif k == "Pressure":
            if v == "Sensor":
                settings["pressure"] = "internal sensor"
            else:
                settings["pressure"] = v  # untested!
        elif k == "Salinity":
            settings["salinity"] = float(v.split()[0])
        elif k == "LED intensity":
            settings["intensity"] = v
        elif k == "Amplification":
            settings["amp"] = v
        elif k == "Frequency":
            settings["frequency"] = v
    metadata["settings"] = settings

    # parse calibration
    calibration = {}
    for k, v in zip(lines[12].split("\t")[1:], lines[13].split("\t")[1:]):
        if k == "dphi0":
            calibration["dphi0"] = float(v[:-1])
        elif k == "dphi100":
            calibration["dphi100"] = float(v[:-1])
        elif k == "Temp0":
            calibration["temp0"] = float(v[:-2])
        elif k == "Temp100":
            calibration["temp100"] = float(v[:-2])
        elif k == "Pressure":
            calibration["pressure"] = float(v.split(" ")[0])
        elif k == "Humidity":
            calibration["humidity"] = float(v.split("%")[0])
        elif k == "f":
            calibration["f"] = float(v)
        elif k == "m":
            calibration["m"] = float(v)
        elif k == "tt":
            calibration["tt"] = float(v.split("%")[0]) / 100
        elif k == "kt":
            calibration["kt"] = float(v.split("%")[0]) / 100
        elif k == "bkgdAmp":
            calibration["bkgdAmpl"] = float(v.split(" ")[0])
        elif k == "bkgdDphi":
            calibration["bkgdDphi"] = float(v[:-1])
        elif k == "ft":
            calibration["ft"] = float(v.split("/")[0])
        elif k == "mt":
            calibration["mt"] = float(v.split("/")[0])
        elif k == "PercentO2":
            calibration["percentO2"] = float(v.split("%")[0])
        elif k in ("calFreq", "useKsv", "ksv", "not used"):
            continue
        else:
            print(f"skipping calibration parameter {k}. value: {v}", file=sys.stderr)
    metadata["calibration"] = calibration

    # parse calibration status
    for k, v in zip(lines[8].split("\t")[1:], lines[9].split("\t")[1:]):
        if k == "Sensor Code":
            metadata["sensor_code"] = v
        elif k == "Calibrate Air":
            if v == "not cal.":
                metadata["calibration"]["date_calibration_high"] = None
            else:
                metadata["calibration"]["date_calibration_high"] = duparser.parse(v, dayfirst=True)
        elif k == "Calibrate 0%":
            if v == "not cal.":
                metadata["calibration"]["date_calibration_zero"] = None
            else:
                metadata["calibration"]["date_calibration_zero"] = duparser.parse(v, dayfirst=True)

    # get header count
    header = 14
    while not lines[header].startswith("Data_Point"):
        header += 1
        if header > len(lines):
            raise ValueError("Could not find start of data")

    usecols = [1, 2, 5, 6, 7, 8, 10, 11, 12, 13, 14]

    df = pd.read_csv(
        fname,
        skiprows=header,
        encoding="latin1",
        usecols=usecols,
        sep="\t",
        decimal=",",
        skip_blank_lines=False,
        na_values=["--,---", "no sensor"],
    )
    df.index = pd.to_datetime(df.iloc[:, 0])
    df.drop(df.columns[0], axis=1, inplace=True)

    rename_dict = {
        "Oxygen(mg/L)": "oxygen_mgL",
        "Oxygen(%O2)": "oxygen_%O2",
        "Temperature(°C)": "sample_temperature",
        "Air_Pressure(mbar)": "pressure",
        "Humidity(%RH)": "humidity",
        "Time(s)": "time_s",
        "Status": "status",
        "dphi(°)": "dphi",
        "Intensity(mV)": "signal_intensity",
        "Ambient_Light(mV)": "ambient_light",
        "Case_Temperature(°C)": "case_temperature",
    }
    df.rename(columns=rename_dict, inplace=True)
    df.index.name = "date_time"

    return df, metadata


def read_fdo2_logger(fname: str) -> tuple[pd.DataFrame, dict]:
    """Loads and parses a logfile from the FDO2 Logger

    :param fname: path to the logfile
    :return: (DataFrame, metadata-dict)
    """
    lines = []
    with open(fname, "r", encoding="latin1") as f:
        for line in f:
            lines.append(line[:-1])
            if len(lines) > 30:
                break

    metadata = {}
    metadata["experiment_name"] = ""
    metadata["experiment_description"] = ""

    metadata["device"] = lines[2].split("\t", maxsplit=1)[1]
    metadata["firmware"] = lines[3].split("\t", maxsplit=1)[1].replace(",", ".")
    metadata["uid"] = lines[4].split("\t", maxsplit=1)[1]
    metadata["software_version"] = lines[1].split("\t", maxsplit=1)[1].replace(",", ".")

    # parse settings
    settings = {}
    settings["analyte"] = "oxygen"
    for k, v in zip(lines[6].split("\t")[1:], lines[7].split("\t")[1:]):
        try:
            v = int(v)
        except:
            pass
        if k == "temp (m°C)":
            if v == -300000:
                settings["temperature"] = "external sensor"
            elif v == -299999:
                settings["temperature"] = "internal sensor"
            else:
                settings["temperature"] = v
        elif k == "pressure (ubar)":
            if v == -1:
                settings["pressure"] = "internal sensor"
            else:
                settings["pressure"] = v / 1000
        elif k == "salinity (mg/L)":
            settings["salinity"] = v / 1000
        elif k == "mode (1=1ms, 8=128ms)":
            settings["duration"] = f"{2 ** (v - 1)}ms"
        elif k == "intensity (0=10%, 7=100%)":
            settings["intensity"] = ("10%", "15%", "20%", "30%", "40%", "60%", "80%", "100%")[v]
        elif k == "amp (4=80x, 6=400x)":
            settings["amp"] = ("1x", "unknown", "unknown", "unknown", "40x", "200x", "400x")[v]
        elif k == "frequency (Hz)":
            settings["frequency"] = v
        elif k == "crcEnable (0=off, 1=on)":
            settings["crc_enable"] = bool(v)
        elif k == "writeLock (13579=locked)":
            settings["write_lock"] = v == 13579
        elif k == "autoMode (bit0=autoFlash, bit1=autoAmp)":
            settings["auto_flash_duration"] = bool(v & 1)
            settings["auto_amp"] = bool(v & 2)
        elif k == "broadcast interval (ms)":
            settings["broadcast_interval_ms"] = v
        else:
            raise ValueError(f"Unknown settings register {k}")
    metadata["settings"] = settings

    # parse calibration
    calibration = {}
    for k, v in zip(lines[8].split("\t")[1:], lines[9].split("\t")[1:]):
        v = int(v) / 1000
        if k == "dphi0 (m°)":
            calibration["dphi0"] = v
        elif k == "dphi100 (m°)":
            calibration["dphi100"] = v
        elif k == "temp0 (m°C)":
            calibration["temp0"] = v
        elif k == "temp100 (m°C)":
            calibration["temp100"] = v
        elif k == "pressure (ubar)":
            calibration["pressure"] = v
        elif k == "humidity (m%RH)":
            calibration["humidity"] = v
        elif k == "f (e-3)":
            calibration["f"] = v
        elif k == "m (e-3)":
            calibration["m"] = v
        elif k == "tt (e-5/K)":
            calibration["tt"] = round(v / 100, 5)
        elif k == "kt (e-5/K)":
            calibration["kt"] = round(v / 100, 5)
        elif k == "bkgdAmp (uV)":
            calibration["bkgdAmpl"] = v
        elif k == "bkgdDphi (m°)":
            calibration["bkgdDphi"] = v
        elif k == "ft (e-6 / K)":
            calibration["ft"] = round(v / 1000, 6)
        elif k == "mt (e-6/K)":
            calibration["mt"] = round(v / 1000, 6)
        elif k == "percentO2 (m%O2)":
            calibration["percentO2"] = v
        elif k == "tempOffset (m°C)":
            calibration["temp_offset"] = v
        elif k in ("calFreq (Hz)", "useKsv (0-1)", "ksv (e-6/mbar)"):
            continue
        else:
            raise ValueError(f"Unknown calibration register {k}")
    metadata["calibration"] = calibration

    # parse user calibration
    user_calibration = {}
    for k, v in zip(lines[10].split("\t")[1:], lines[11].split("\t")[1:]):
        if int(v) == -1000:
            v = None
        else:
            v = int(v) / 1000
        if k == "dphi0 (m°)":
            user_calibration["dphi0"] = v
        elif k == "dphi100 (m°)":
            user_calibration["dphi100"] = v
        elif k == "temp0 (m°C)":
            user_calibration["temp0"] = v
        elif k == "temp100 (m°C)":
            user_calibration["temp100"] = v
        elif k == "pressure (ubar)":
            user_calibration["pressure"] = v
        elif k == "humidity (m%RH)":
            user_calibration["humidity"] = v
        elif k == "percentO2 (m%O2)":
            user_calibration["percentO2"] = v
        elif k == "m (0.001)":
            user_calibration["m"] = v
        elif k == "crcEnable (0..1)":
            user_calibration["crc_enable"] = v != 0
        elif k == "broadcastInterval (ms)":
            user_calibration["broadcast_interval_ms"] = v
        else:
            raise ValueError(f"Unknown user calibration register {k}")
    metadata["user_calibration"] = user_calibration

    # get header count
    header = 10
    while "DateTime" not in lines[header]:
        header += 1
        if header > len(lines):
            raise ValueError("Could not find start of data")

    if "," in lines[header + 1].split("\t")[2]:
        decimal = ","
    else:
        decimal = "."

    df = pd.read_csv(
        fname, skiprows=header, encoding="latin1", sep="\t", decimal=decimal, skip_blank_lines=False, index_col=False
    )
    df.index = pd.to_datetime(df.iloc[:, 0])
    df.drop(df.columns[0], axis=1, inplace=True)

    rename_dict = {
        "Time (s)": "time_s",
        "Oxygen (hPa)": "oxygen_hPa",
        "Temperature (°C)": "sample_temperature",
        "dphi (°)": "dphi",
        "Signal Intensity (mV)": "signal_intensity",
        "Ambient Light (mV)": "ambient_light",
        "Pressure (mbar)": "pressure",
        "Humidity (%RH)": "humidity",
    }
    df.rename(columns=rename_dict, inplace=True)
    df.index.name = "date_time"

    return df, metadata
