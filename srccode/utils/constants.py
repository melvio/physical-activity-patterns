from dataclasses import dataclass
import plotly.express as px


@dataclass(frozen=True)
class LabelConstant:
    """ threshold in milli-gravity """
    SEDENTARY_BEHAVIOR_MG = 48
    LIGHT_PHYSICAL_ACTIVITY_MG = 154
    MODERATE_PHYSICAL_ACTIVITY_MG = 389


@dataclass(frozen=True)
class PathConstants:
    BASE_DATA_DIR: str = "../../data/"
    BASE_PCA_DIR: str = BASE_DATA_DIR + "pca_results/"
    BASE_DIR_FIGURES: str = BASE_DATA_DIR + "figures/"
    BASE_DIR_PARTICIPANTS: str = BASE_DATA_DIR + "participants-characteristics/"

    ERGO_CSV_PATH: str = "../../data/participants-characteristics/GeneActiv-data-ERGO5-6-merged.csv"
    ERGO_MORE_CSV_PATH: str = (
        "../../data/participants-characteristics/basic_information_genactive_participants_ergo-5-6_"
        "with_smoking_dexa_anthropometrics_simplified.csv"
    )

    ERGO_MORE_CSV_BASE_PATH: str = (
        "../data/participants-characteristics/basic_information_genactive_participants_ergo-5-6_"
        "with_smoking_dexa_anthropometrics_simplified.csv"
    )

    PA_AND_AVG_CSV_PATH: str = "../../data/participants-characteristics/physical-activity-per-hour-days-and-weekend-with-elaborate-averages.csv"
    PA_AND_AVG_NEW_CSV_PATH: str = BASE_DIR_PARTICIPANTS + "physical-activity-per-hour-days-and-weekend_new_with_averages.csv"

    FEATURES_CSV_PATH: str = "../../data/participants-characteristics/feature-list.csv"
    FEATURES_CSV_WITH_CATEGORIES_PATH: str = "../../data/participants-characteristics/feature-list-with-categories.csv"

    PARTICIPANTS_INFO_CSV_PATH: str = BASE_DIR_PARTICIPANTS + "basic_information_genactive_participants_ergo-5-6_with_smoking_dexa_anthropometrics.csv"

    MISSING_HOUR_DATA_CSV_PATH: str = BASE_DIR_PARTICIPANTS + "missing_hour_data.csv"

    FEATURES_CSV_COMPLETE_BODY_COMP_PATH: str = BASE_DIR_PARTICIPANTS + "feature-list-with-complete-body-composition.csv"

    WEARINFO_CSV_PATH = BASE_DIR_PARTICIPANTS + "wearinfo.csv"

    PCA_HOURS_COMPONENTS_CSV_PATH: str = BASE_PCA_DIR + "hours-together/pca_components.csv"
    PCA_HOURS_LOADINGS_CSV_PATH: str = BASE_PCA_DIR + "hours-together/pca_loadings.csv"
    PCA_HOURS_EXPLAINED_VARIANCE_CSV_PATH: str = BASE_PCA_DIR + "hours-together/explained_variance_ratio.csv"

    PCA_DAYS_COMPONENTS_CSV_PATH: str = BASE_PCA_DIR + "days-together/pca_components.csv"
    PCA_DAYS_LOADINGS_CSV_PATH: str = BASE_PCA_DIR + "days-together/pca_loadings.csv"
    PCA_DAYS_EXPLAINED_VARIANCE_CSV_PATH: str = BASE_PCA_DIR + "days-together/explained_variance_ratio.csv"


@dataclass(frozen=True)
class StatConstants:
    CI95 = [0.025, 0.975]
    PERCENTILES = [0.025, 0.10, 0.25, 0.5, 0.75, 0.90, 0.975]
    PERCENTILES_ICR_25_75 = [0.25, 0.75]
    MEDIAN_IQR_COLS = ["50%", "25%", "75%"]
    MEAN_CI95_COLS = ["mean", "2.5%", "97.5%"]


@dataclass(frozen=True)
class CategoryConstants:
    SEX_MAP = {"male": 0, "female": 1}
    SMOKER_MAP = {"never smoked": 0, "former smoker": 1, "current smoker": 2, "unknown": 0}
    WAIST_MAP = {"normal": 0, "high": 1, "very_high": 2}


@dataclass(frozen=True)
class TimeConstants:
    MINUTES_PER_HOUR: int = 60
    SECONDS_PER_HOUR: int = 60 * MINUTES_PER_HOUR
    HOURS_PER_DAY: int = 24
    SECONDS_PER_DAY: int = HOURS_PER_DAY * SECONDS_PER_HOUR
    DAYS_PER_WEEK: int = 7
    GENEACTIV_FREQUENCY: int = 50

    CONVERSION_G_TO_MG = 1000
    CONVERSION_FROM_G_PER_HOUR_TO_MG = CONVERSION_G_TO_MG / (SECONDS_PER_HOUR * GENEACTIV_FREQUENCY)
    CONVERSION_G_PER_HOUR_TO_MG = CONVERSION_FROM_G_PER_HOUR_TO_MG
    """synonym"""

    AGE_CATEGORIES = [50, 60, 70, 80, 90, 100]
    WEEKDAYS_DICT = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
    WEEKDAYS_INT_STR_CAPITALIZED = {i: s.capitalize() for s, i in WEEKDAYS_DICT.items()}
    WEEKDAYS_STR_LIST = list(WEEKDAYS_DICT.keys())
    WEEKDAYS_STR_CAPITALIZED = list(WEEKDAYS_INT_STR_CAPITALIZED.values())


@dataclass(frozen=True)
class BehaviorConstants:
    """Class of behavior constants"""
    BEHAVIOR_DICT = {
        "sed": "Sedentary Behavior", "lpa": "Light Physical Activity",
        "mpa": "Moderate Physical Activity", "vpa": "Vigorous Physical Activity"
    }
    """dictionary of column labels and readable descriptions"""

    BEHAVIOR_ABBRVS = list(BEHAVIOR_DICT.keys())


@dataclass(frozen=True)
class PlotConstants:
    """
    https://seaborn.pydata.org/tutorial/color_palettes.html
    """
    __FEM_HEX_COLOR = "#eb4729"
    __MAL_HEX_COLOR = "#1b909a"
    SEX_PALETTE = {"female": __FEM_HEX_COLOR, "male": __MAL_HEX_COLOR,
                   "Female": __FEM_HEX_COLOR, "Male": __MAL_HEX_COLOR}
    SEX_INT_PALETTE = {1: __FEM_HEX_COLOR, 0: __MAL_HEX_COLOR}
    """Choosing an appropriate color for gender: https://dataviztoday.com/blog/34"""

    CLUSTER_PALETTE = px.colors.qualitative.Plotly


@dataclass(frozen=True)
class ErrorbarsConstants:
    """https://seaborn.pydata.org/tutorial/error_bars.html"""

    STANDARD_DEVIATION = "sd"
    """
    +- 1 SD
    The standard deviation error bars will always be symmetrical around the estimate. 
    This can be a problem when the data are skewed .
    """
    STANDARD_ERROR = "se"
    """ 
    INterval +/-1 standard error from the mean, i.e. StDev/sqrt(sample_size).
    """
    PERCENTILE = "pi"
    """
    By default a 95% percentile interval
    """

    PERCENTILE_25_75 = ("pi", 50)
    """Inter-quartile Range, i.e. from 25-75%"""

    CONFID_INTERVAL = "ci"
    """Confidence interval around the mean. Usually +2SD of standard error of the mean"""


@dataclass(frozen=True)
class TableConstants:
    TABLE_NAME_BASE_MAP = {
        "wear_age_years": "Age (years)",
        "BMI": "BMI (kg/cm²)",
        "waist_circumference": "Waist Circumference (cm)",
        "hip_cicumference": "Hip Circumference (cm)",
        "waist_hip_ratio": "Waist Hip Ratio",
        "body_fat_percentage": "Body Fat Percentage",
        "FFMI": "FFMI (kg/cm²)",
        "normalized_FFMI": "Normalized FFMI (kg/cm²)",
        "pca0": "First Component",
        "pca1": "Second Component",
        "pca2": "Third Component",
        "avg_g_per_hour": "Acceleration (mg)]"
    }
    TABLE_NAME_MAP_DAY_OF_WEEK = TABLE_NAME_BASE_MAP | {
        "sed_avg_hours_per_day": "SED (hour/day)",
        "lpa_avg_hours_per_day": "LPA (hour/day)",
        "mpa_avg_hours_per_day": "MPA (min/day)",
        "vpa_avg_hours_per_day": "VPA (min/day)"
    }
    """From column to readable table name mappings."""

    TABLE_NAME_MAP_HOURS_PER_DAY = TABLE_NAME_BASE_MAP | {
        "sed_avg_hours_per_day": "SED (min/hour)",
        "lpa_avg_hours_per_day": "LPA (min/hour)",
        "mpa_avg_hours_per_day": "MPA (sec/hour)",
        "vpa_avg_hours_per_day": "VPA (sec/hour)"
    }
