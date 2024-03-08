from datetime import timedelta
from logging import debug, error
from pathlib import Path

import pandas as pd

from setup_logging import configure_logging
from utils.data_retrieval import get_physical_activity_data, get_labeled_csv_name
from utils.constants import PathConstants, LabelConstant


def chop_interval(activity_df: pd.DataFrame, *,
                  first_date, weardays: int) -> pd.DataFrame:
    """

    :param activity_df:
    :param first_date:
    :param weardays:
    :return:
    """
    wearsec: int = weardays * 24 * 60 * 60
    last_date = first_date + timedelta(seconds=wearsec)
    return activity_df[(activity_df["time"] >= first_date) & (activity_df["time"] < last_date)]


def label_activity(vector_magnitude_g: float) -> str:
    """
    Takes a vector magnitude, and returns a label for intensity of activity

    vector_magnitude_g:
    """
    g_to_mg_conversion = 1000
    hz = 50
    epoch_sec = 30
    conversion = g_to_mg_conversion / (hz * epoch_sec)
    vector_magnitude_mg_per_epoch = vector_magnitude_g * conversion  # (to summarize: div 1.5)
    if vector_magnitude_mg_per_epoch < LabelConstant.SEDENTARY_BEHAVIOR_MG:
        return "sed"
    elif vector_magnitude_mg_per_epoch < LabelConstant.LIGHT_PHYSICAL_ACTIVITY_MG:
        return "lpa"
    elif vector_magnitude_mg_per_epoch < LabelConstant.MODERATE_PHYSICAL_ACTIVITY_MG:
        return "mpa"
    else:
        return "vpa"  # vigorous


def add_physical_activity_labels(row) -> None:
    """
    For every row in dataframe create a new CSV with PA labels.

    :param row:
    :return:
    """
    ergoid = row["ergoid"]
    interval = "30S"
    path = Path(get_labeled_csv_name(ergoid=ergoid, interval=interval))

    try:
        debug(f"Currently working on participant {ergoid=}")
        df_pa_full: pd.DataFrame = get_physical_activity_data(ergo=row["ERGO"], ergoid=ergoid, interval=interval)
        df_pa: pd.DataFrame = chop_interval(df_pa_full, first_date=row["wear_date"], weardays=row["nr_weardays"])

        t_series: pd.Series = df_pa["time"]
        df_pa["timestamp_hour"] = t_series.map(lambda t: t.hour)
        df_pa["timestamp_day_of_week"] = t_series.map(lambda t: t.weekday())  # 0 = Monday,... ,5 = Saturday, 6 = Sunday
        df_pa["timestamp_is_weekend"] = df_pa["timestamp_day_of_week"] >= 5

        df_pa["ergoid"] = ergoid
        df_pa["activity_intensity_category"] = df_pa["vector_magnitude"].map(label_activity)

        debug(f"about to write {path=}")
        df_pa.to_csv(path)
    except Exception as exc:
        error(f"failed to create a CSV for {ergoid=}.", exc_info=exc)


if __name__ == '__main__':
    configure_logging(__file__)

    df_ergo = pd.read_csv(PathConstants.ERGO_MORE_CSV_BASE_PATH, index_col=0, parse_dates=["wear_date"])
    df_ergo["ERGO"] = df_ergo["ERGO"].astype('Int64')
    debug(f"going to label {df_ergo.shape[0]} number of CSV files")

    df_ergo.apply(add_physical_activity_labels, axis="columns")
