import dataclasses
import io
from collections import OrderedDict
from datetime import datetime, timedelta
from logging import debug, error, warning
from pathlib import Path

import numpy as np
from pandas import DataFrame

from setup_logging import configure_logging
from utils.fileutils import drop_extension, is_bin_file


@dataclasses.dataclass(frozen=True)
class BinFile:
    """
    Constants related to binfiles
    """
    HEADER_LINES: int = 59
    """number of lines in header of a .bin file"""

    MEASUREMENTS_PER_PAGE: int = 300
    """One line of HEX values inside a .bin file contains 300 coordinates (3x100: X,Y,Z)"""

    HEX_SIZE: int = 12
    """Number of bits in a hex value"""

    MILLISEC_DELTA_PER_MEASUREMENT: int = 20
    """20ms"""

    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S:%f"
    """Format of timestamps in .bin files"""

    FLOAT_PRECISION = np.float16
    """Default float precision to use np.ndarrays"""


def decode_genactiv12(val: int) -> int:
    """
    Turns hexadecimal byte value from GENactiv watch into octadecimal value

    :param val: hexadecimal value to turn into decimal value
    :return: octadecimal
    """
    if (val & 2048) != 0:
        val -= 4096
    return val


def extract_header_value(genactiv_header: [str], *, line: int) -> str:
    """
    From the geneactiv header return the header value for a specific line.


    :param genactiv_header: list of strings with format (key:string)
    :param line: line to extract header from (0 indexed line)
    :return: value from line
    """
    return genactiv_header[line].split(":")[1]


def extract_header_float(genactiv_header: [str], *,
                         line: int,
                         default: float = 0.0) -> float:
    """
    Return float value from header, or return default if value can't be parsed

    :param genactiv_header:
    :param line:
    :param default:
    :return:
    """
    value: str = extract_header_value(genactiv_header, line=line)
    try:
        return float(value)
    except ValueError:
        warning(f"failed to extract a float {value=} from header {line=}: {genactiv_header[line]}")
        return default


def extract_header_int(genactiv_header: [str], line: int, *,
                       default: int = 0) -> int:
    """
    Return int value from header, or return default if value can't be parsed

    :param genactiv_header:
    :param line:
    :param default:
    :return:
    """
    value: str = extract_header_value(genactiv_header, line=line)
    try:
        return int(value)
    except ValueError:
        warning(f"failed to extract an int {value=} from header {line=}: {genactiv_header[line]}")
        return default


def extract_start_monitoring_time(header_datetime: str) -> datetime:
    """
    Takes the start time value from a binfile header and returns a python datetime.

    :param header_datetime:
    :return: start_datetime of monitoring
    """
    if header_datetime == "0000-00-00 00:00:00:000":
        return datetime.strptime("0001-01-01", "%y-%m-%d")
    else:
        return datetime.strptime(header_datetime, BinFile.DATETIME_FORMAT)


def extract_measurement_frequency(
        genactiv_header: [str], *,
        default: float = 50.0) -> float:
    """Extract frequency from geneactive header, return 50.0 (Hz) as default if parsing fails

    >>> extract_measurement_frequency([":"]*20)
    50.0

    >>> extract_measurement_frequency([":"]*20, default=40.0)
    40.0

    :param genactiv_header:
    :param default: default frequency to return
    :return: Frequency in Hz (min^-1)
    """
    try:
        # frequency might be written in European style (, instead of .)
        freq_value: str = genactiv_header[19].split(":")
        freq_value_sans_hz: str = freq_value[1].replace(" Hz", "")
        freq_value_comma_save: str = freq_value_sans_hz.replace(",", ".")
        return float(freq_value_comma_save)
    except BaseException as exc:
        error(f"failed to extract frequency from {genactiv_header[19]}, using {default=}", exc_info=exc)
        return default


def parse_genactiv_header(genactiv_header: list[str]) -> OrderedDict:
    """
    Turns list of strings of the header of GENactiv file into an OrderedDict
    
    :param genactiv_header: list of lines of GENactiv headers
    :return: OrderedDict key-value (String, Any) mapping of the GENactiv headers
    """
    header_info = OrderedDict()

    header_info["start_datetime"] = genactiv_header[21][11:]
    header_info["start_datetime_python"] = extract_start_monitoring_time(header_datetime=header_info["start_datetime"])

    header_info["device_id"] = extract_header_value(genactiv_header, line=1)
    header_info["firmware"] = genactiv_header[4][24:]
    header_info["calibration_date"] = genactiv_header[5][17:]

    header_info["subject_code"] = extract_header_int(genactiv_header, line=38)
    header_info["date_of_birth"] = extract_header_value(genactiv_header, line=39)
    header_info["sex"] = extract_header_value(genactiv_header, line=40)

    header_info["height"] = extract_header_float(genactiv_header, line=41)
    header_info["weight"] = extract_header_float(genactiv_header, line=42)
    header_info["handedness"] = extract_header_value(genactiv_header, line=43)

    header_info["x_gain"] = float(extract_header_value(genactiv_header, line=47))
    header_info["x_offset"] = float(extract_header_value(genactiv_header, line=48))
    header_info["y_gain"] = float(extract_header_value(genactiv_header, line=49))
    header_info["y_offset"] = float(extract_header_value(genactiv_header, line=50))
    header_info["z_gain"] = float(extract_header_value(genactiv_header, line=51))
    header_info["z_offset"] = float(extract_header_value(genactiv_header, line=52))

    header_info["number_pages"] = int(extract_header_value(genactiv_header, line=57))
    header_info["frequency"] = extract_measurement_frequency(genactiv_header)
    header_info["epoch"] = timedelta(seconds=1) / int(header_info["frequency"])

    debug(f"{header_info=}")
    return header_info


def adjust_axis_for_gain_and_offset(
        *, axis_values: np.ndarray,
        axis_gain: float,
        axis_offset: float,
        ftype=BinFile.FLOAT_PRECISION
) -> np.ndarray:
    """adjust axis_values for watch gain and offset

    :param axis_values: ndarray with axis (x OR y OR z) values
    :param axis_gain:
    :param axis_offset:
    :param ftype: float type to use for the np.ndarray (float16 doesn't seem to give
                 rounding errors, probably bc the watch isn't sufficiently precise for it to matter.)
    :return: ndarray with adjusted axis values
    """
    return np.array([(v * 100 - axis_offset) / axis_gain for v in axis_values], dtype=ftype)


def vector_magnitude(*, xs: np.ndarray, ys: np.ndarray, zs: np.ndarray, ftype=BinFile.FLOAT_PRECISION) -> np.ndarray:
    """
    takes x,y,z coordinates and returns vector magnitude

    https://activinsights.com/wp-content/uploads/2023/10/GENEActiv-1.2-July-2023-instructions-WC.pdf
    The gravity-subtracted sum of vector magnitudes is calculated as follows:

     SVM^g s = ∑ | (x2+y2+z2)^0.5 - 1g |

    :param xs: array of x values
    :param ys: array of y values
    :param zs: array of z values
    :param ftype: float data type to use for the returned ndarray.
    :return: ndarray of vector magnitudes
    """
    return np.absolute(np.sqrt(xs ** 2 + ys ** 2 + zs ** 2) - 1, dtype=ftype)


def load_genactiv_bin(genactiv_file_path: str) -> (OrderedDict, DataFrame):
    """
    Loads a GENactiv .bin file and returns: (.bin file header, DataFrame with activity data)

    :param genactiv_file_path: .bin filepath
    :return: (binheader, DataFrame of timestamped vector magnitudes)
    """
    debug(f"loading {genactiv_file_path=}")
    bin_file = open(genactiv_file_path, "rb")
    data: io.BytesIO = io.BytesIO(bin_file.read())

    header_lines: list[str] = [data.readline().strip().decode() for _ in range(BinFile.HEADER_LINES)]
    header_info: OrderedDict = parse_genactiv_header(header_lines)

    number_of_pages: int = int(header_info["number_pages"])

    lines_in_body: int = BinFile.MEASUREMENTS_PER_PAGE * number_of_pages
    x_values: np.ndarray = np.empty(lines_in_body, dtype=int)
    y_values: np.ndarray = np.empty(lines_in_body, dtype=int)
    z_values: np.ndarray = np.empty(lines_in_body, dtype=int)
    ga_timestamps = np.empty(lines_in_body, dtype=type(header_info["start_datetime_python"]))

    obs_num: int = 0
    timestamp_num: int = 0

    for current_page in range(number_of_pages):
        if current_page % 20_000 == 0 and current_page != 0:
            debug(f"{current_page=} out of {number_of_pages=} for {genactiv_file_path=}")

        # per 8 lines in de data, the 3rd line contains the timestamp, 10-33 are the timestamp characters
        page_time: str = [data.readline() for _ in range(9)][3].strip().decode()
        try:
            page_time: datetime = datetime.strptime(page_time[10:33], BinFile.DATETIME_FORMAT)
        except Exception as exc:
            error(f"failed to read {page_time=} on {current_page=} of {genactiv_file_path=}")
            raise exc

        # For each 12 byte measurement in page (300 bytes per line)
        # 3600 HEX characters per line
        # 300 blocks of 12 HEX characters, coding for 1x, 1y, and 1z value
        # iow. 1 line of HEX characters codes for 100 x,y,z measurements (and 300 total measurements)
        for k in range(BinFile.MEASUREMENTS_PER_PAGE):
            # frequency of 50 Hz (measurements/sec),
            # 50 Hz * 300 measurements: approx 6s of measurement per line of HEX values
            ga_timestamps[timestamp_num] = (
                    page_time + (timedelta(milliseconds=BinFile.MILLISEC_DELTA_PER_MEASUREMENT) * k)
            )
            timestamp_num += 1

        for _ in range(BinFile.MEASUREMENTS_PER_PAGE):
            # note: the 9th line is the HEX-value for activity
            block: bytes = data.read(BinFile.HEX_SIZE)

            x_hex: int = int(block[0:3], 16)
            y_hex: int = int(block[3:6], 16)
            z_hex: int = int(block[6:9], 16)

            x_values[obs_num] = decode_genactiv12(x_hex)
            y_values[obs_num] = decode_genactiv12(y_hex)
            z_values[obs_num] = decode_genactiv12(z_hex)

            obs_num += 1

        _ = data.read(2)  # \r\b character at end of 3600 line

    debug(f"adjusting x-axis for gain and offset for {genactiv_file_path=}")
    x_values: np.ndarray = adjust_axis_for_gain_and_offset(
        axis_values=x_values, axis_gain=header_info["x_gain"], axis_offset=header_info["x_offset"]
    )

    debug(f"adjusting y-axis for gain and offset for {genactiv_file_path=}")
    y_values: np.ndarray = adjust_axis_for_gain_and_offset(
        axis_values=y_values, axis_gain=header_info["y_gain"], axis_offset=header_info["y_offset"]
    )

    debug(f"adjusting z-axis for gain and offset for {genactiv_file_path=}")
    z_values: np.ndarray = adjust_axis_for_gain_and_offset(
        axis_values=z_values, axis_gain=header_info["z_gain"], axis_offset=header_info["z_offset"]
    )

    debug(f"calculating vector magnitude array for {genactiv_file_path=}")
    vm: np.ndarray = vector_magnitude(xs=x_values, ys=y_values, zs=z_values)

    # prevent memory usage problems before creating dataframe
    del x_values, y_values, z_values

    debug(f"creating timestamp and vector-magnitude dataframe for {genactiv_file_path=}")
    return header_info, DataFrame(data={"time": ga_timestamps, "vector_magnitude": vm})


def turn_bin_file_into_csv(filepath_name: str, *,
                           overwrite_existing=False) -> None:
    """
    Takes a filepath of a .bin file and turns it into CSV


    >>> turn_bin_file_into_csv(".thisisnotgood")
    Traceback (most recent call last):
    Exception: .thisisnotgood is not a .bin file

    :param overwrite_existing: Overwrite currently existing CSV if True
    :param filepath_name: file path to .bin file
    """
    if is_bin_file(filepath_name) is False:
        raise Exception(f"{filepath_name} is not a .bin file")

    debug(f"going to load: {filepath_name=}")

    _, df = load_genactiv_bin(filepath_name)

    debug(f"finished loading: {filepath_name=}")
    csv_path: Path = Path(f"{drop_extension(filepath_name)}_granular-milliseconds.csv")

    if csv_path.exists():
        if not overwrite_existing:
            debug(f"skipping {csv_path} because it exists already")
        else:
            debug(f"overwriting {csv_path}")
            df.to_csv(csv_path)
    else:
        debug(f"creating new {csv_path}")
        df.to_csv(csv_path)


def turn_bin_files_into_csv(filepath_names: [str]) -> None:
    """
    Turn a list containing filepaths with .bin files into .csv files
    
    :param filepath_names: 
    :return: 
    """
    for filepath in filepath_names:
        try:
            turn_bin_file_into_csv(filepath)
        except ValueError | Exception as exc:
            debug(f"Failed to transform {filepath}", exc_info=exc)


if __name__ == "__main__":
    configure_logging(__file__)
    # import doctest
    # doctest.testmod()

    # particular binfile ->  to dataframe
    header, df = load_genactiv_bin("../data/sample-from-ergo8/486-partial2.bin")
    print("debug")

    # decode all files in a particular lcoation
    # binfiles: [str] = glob.glob("../data/ERGO6-COPY/[3-9][0-9][0-9].bin")
    # logging.debug(f"going to turn binfiles into granular csvs: {binfiles}")
    # turn_bin_files_into_csv(binfiles)
