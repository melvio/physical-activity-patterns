#!/usr/bin/env python3
import sklearn


def notebook_setup():
    """
    Keeping this function as an example of common setup of a jupyter notebook.
    """
    from utils.constants import *
    from utils.printers import col_print
    import numpy as np
    import pandas as pd
    import scipy
    import seaborn as sns
    import sklearn

    sns.set_style("whitegrid")
    sklearn.set_config(transform_output="pandas")

