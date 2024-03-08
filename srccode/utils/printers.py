import pandas as pd

"""
Helper functions for the sake of printing stuff
"""


def col_print(df: pd.DataFrame, *,
              startswith_pattern: str = None,
              in_str: str = None) \
        -> None:
    """
    Print columns
    """
    cols = df.columns
    join_pat = " | "
    if startswith_pattern:
        prt_str = join_pat.join([col for col in cols if col.startswith(startswith_pattern)])
    elif in_str:
        prt_str = join_pat.join([col for col in cols if in_str in col])
    else:
        prt_str = join_pat.join([col for col in cols])

    print(prt_str)
