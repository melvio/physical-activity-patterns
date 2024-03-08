import pandas as pd


def get_labeled_csv_name(*, ergoid, interval):
    return f"../data/physical-activity/{ergoid}_labeled_summary_{interval}.csv"


def get_physical_activity_data(
        *, ergo: int, ergoid: int, interval: str = "30S"
) -> pd.DataFrame:
    """

    :param ergo:
    :param ergoid:
    :param interval:
    :return:
    """

    physical_activity_csv_path = f"../data/ERGO{ergo}-COPY/{ergoid}_summary_{interval}.csv"

    return pd.read_csv(physical_activity_csv_path, parse_dates=["time"])
