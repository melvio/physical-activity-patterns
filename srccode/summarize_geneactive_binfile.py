import glob
from collections import OrderedDict
from logging import debug, error
from pathlib import Path

from pandas import DataFrame, read_csv

from read_binfile import load_genactiv_bin
from setup_logging import configure_logging
from utils.fileutils import drop_extension


def _dict_header_to_dataframe(header: OrderedDict) -> DataFrame:
    """

    >>> _dict_header_to_dataframe(OrderedDict({"x_gain": -1.0, "handedness": "right"}))
               header_value
    x_gain             -1.0
    handedness        right

    :param header:
    :return:
    """
    df_headers = DataFrame(data=header.values(), index=list(header.keys()))
    df_headers.columns = ["header_value"]
    return df_headers


def get_header_csv_path(binfile_path: str) -> Path:
    """
    From a binfile return a corresponding header-csv Path object.

    :param binfile_path:
    :return: CSV path for header
    """
    return Path(drop_extension(binfile_path) + "_header.csv")


def _write_header_to_csv(
        csv_header_path: Path,
        header: OrderedDict,
        overwrite_existing=False
) -> None:
    """Writes the OrderedDict to csv file

    :param csv_header_path:
    :param header:
    :param overwrite_existing: if true, will overwrite pre-exising header file
    :return: Nothing
    """

    if overwrite_existing is False and csv_header_path.exists():
        debug(f"header CSV {csv_header_path=} already exists, not overwriting")
    else:
        debug(f"creating header CSV {csv_header_path=}")
        header_df: DataFrame = _dict_header_to_dataframe(header)
        header_df.to_csv(csv_header_path)


def summarize_granular_dataframe(granular_df: DataFrame, *,
                                 duration_summary: str = '1min'):
    """

    :param granular_df: dataframe with lots of activity data
    :param duration_summary: duration to group data by (standard 1 min)
    :return:
    """
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Timestamp.round.html
    granular_df['time'] = granular_df['time'].dt.round(freq=duration_summary)
    granular_df = granular_df[['time', 'vector_magnitude']]
    granular_df = granular_df.groupby('time').sum()
    return granular_df


def create_summarized_csv_path(*, original_path: str,
                               summary_duration: str) -> Path:
    """
    Takes a string path, remove extension, adds summary_duration, add .csv,
    returns it as a Path.

    :param original_path:
    :param summary_duration:
    :return: Path object for summarized vector magnitude CSV
    """
    return Path(f"{drop_extension(original_path)}_summary_{summary_duration}.csv")


def _write_summarized_dataframe_to_csv(
        summarized_df: DataFrame, *,
        csv_write_path: Path,
        overwrite_existing: bool
) -> None:
    """

    :param summarized_df:
    :param csv_write_path:
    :param overwrite_existing:
    :return:
    """
    if csv_write_path.exists():
        if overwrite_existing:
            debug(f"overwriting CSV file at {csv_write_path}")
            summarized_df.to_csv(csv_write_path)
        else:
            debug(f"skipping {csv_write_path} because it already exists")
    else:
        debug(f"creating new CSV file at {csv_write_path}")
        summarized_df.to_csv(csv_write_path)


def create_summarized_csvs_from_genactiv_binfiles(
        binfile_paths: [str],
        durations: [str],
        overwrite_existing=False,
        skip_analysis_if_header_csv_already_exists=True
) -> None:
    """

    :param binfile_paths: all the .bin files to be summarized
    :param durations: duration to summarize over, @see https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases
    :param overwrite_existing: if True overwrite pre-existing ergoid_summary_time.csv files
    :param skip_analysis_if_header_csv_already_exists: if ergoid_header.csv exist skip all analysis
    :return: nothing
    """
    binfiles_count: int = len(binfile_paths)
    debug(f"about to summarize: {binfiles_count=} binfiles: {binfile_paths=} for {durations=}")
    binfiles_failed: [str] = []

    for binfile_count, binfile_path in enumerate(binfile_paths):
        csv_header_path: Path = get_header_csv_path(binfile_path)
        percent_done: str = f"{100 * binfile_count / binfiles_count:.4}%"
        if skip_analysis_if_header_csv_already_exists and csv_header_path.exists():
            debug(f"skipping reading in {binfile_path=}, because {csv_header_path=} exists. {percent_done=}")
        else:
            try:
                header, activity_df = load_genactiv_bin(genactiv_file_path=binfile_path)
                _write_header_to_csv(
                    csv_header_path=csv_header_path,
                    header=header,
                    overwrite_existing=overwrite_existing
                )
                for duration in durations:
                    summarized_df: DataFrame = summarize_granular_dataframe(
                        granular_df=activity_df,
                        duration_summary=duration
                    )
                    summary_path: Path = create_summarized_csv_path(
                        original_path=binfile_path,
                        summary_duration=duration
                    )
                    _write_summarized_dataframe_to_csv(
                        summarized_df,
                        csv_write_path=summary_path,
                        overwrite_existing=overwrite_existing
                    )
                debug(f"finished {binfile_path=}. {binfile_count=}, total {binfiles_count=}. {percent_done=}")
            except Exception as exc:
                error(f"failed to summarize {binfile_path=}, trying the next one", exc_info=exc)
                binfiles_failed.append(binfile_path)
    debug(f"Finished create_summarized_csvs_from_genactiv_binfiles: failed binfiles {binfiles_failed}")


if __name__ == '__main__':
    configure_logging(__file__)
    # import doctest
    #
    # doctest.testmod()

    binfile_path_list_ergo5: [str] = glob.glob("../data/ERGO5-COPY/*.bin")
    binfile_path_list_ergo6: [str] = glob.glob("../data/ERGO6-COPY/*.bin")
    create_summarized_csvs_from_genactiv_binfiles(
        binfile_paths=binfile_path_list_ergo5 + binfile_path_list_ergo6,
        durations=['30S', '1min', '15min', '1H', '24H'],
        overwrite_existing=False,
        skip_analysis_if_header_csv_already_exists=True
    )
