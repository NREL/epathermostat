import pandas as pd
import numpy as np
from scipy.stats import norm

from eemeter.location import _load_zipcode_to_lat_lng_index
from eemeter.location import _load_zipcode_to_station_index

from collections import OrderedDict
from collections import defaultdict
from warnings import warn
import json

from thermostat import get_version

REAL_OR_INTEGER_VALUED_COLUMNS_HEATING = [
    'n_days_in_inputfile_date_range',
    'n_days_both_heating_and_cooling',
    'n_days_insufficient_data',
    'n_core_heating_days',

    'baseline90_core_heating_comfort_temperature',
    'regional_average_baseline_heating_comfort_temperature',

    'percent_savings_deltaT_heating_baseline90',
    'avoided_daily_mean_core_day_runtime_deltaT_heating_baseline90',
    'avoided_total_core_day_runtime_deltaT_heating_baseline90',
    'baseline_daily_mean_core_day_runtime_deltaT_heating_baseline90',
    'baseline_total_core_day_runtime_deltaT_heating_baseline90',
    '_daily_mean_core_day_demand_baseline_deltaT_heating_baseline90',
    'percent_savings_deltaT_heating_baseline_regional',
    'avoided_daily_mean_core_day_runtime_deltaT_heating_baseline_regional',
    'avoided_total_core_day_runtime_deltaT_heating_baseline_regional',
    'baseline_daily_mean_core_day_runtime_deltaT_heating_baseline_regional',
    'baseline_total_core_day_runtime_deltaT_heating_baseline_regional',
    '_daily_mean_core_day_demand_baseline_deltaT_heating_baseline_regional',
    'mean_demand_deltaT_heating',
    'alpha_deltaT_heating',
    'tau_deltaT_heating',
    'mean_sq_err_deltaT_heating',
    'root_mean_sq_err_deltaT_heating',
    'cv_root_mean_sq_err_deltaT_heating',
    'mean_abs_err_deltaT_heating',
    'mean_abs_pct_err_deltaT_heating',

    'percent_savings_dailyavgHTD_baseline90',
    'avoided_daily_mean_core_day_runtime_dailyavgHTD_baseline90',
    'avoided_total_core_day_runtime_dailyavgHTD_baseline90',
    'baseline_daily_mean_core_day_runtime_dailyavgHTD_baseline90',
    'baseline_total_core_day_runtime_dailyavgHTD_baseline90',
    '_daily_mean_core_day_demand_baseline_dailyavgHTD_baseline90',
    'percent_savings_dailyavgHTD_baseline_regional',
    'avoided_daily_mean_core_day_runtime_dailyavgHTD_baseline_regional',
    'avoided_total_core_day_runtime_dailyavgHTD_baseline_regional',
    'baseline_daily_mean_core_day_runtime_dailyavgHTD_baseline_regional',
    'baseline_total_core_day_runtime_dailyavgHTD_baseline_regional',
    '_daily_mean_core_day_demand_baseline_dailyavgHTD_baseline_regional',
    'mean_demand_dailyavgHTD',
    'alpha_dailyavgHTD',
    'tau_dailyavgHTD',
    'mean_sq_err_dailyavgHTD',
    'root_mean_sq_err_dailyavgHTD',
    'cv_root_mean_sq_err_dailyavgHTD',
    'mean_abs_err_dailyavgHTD',
    'mean_abs_pct_err_dailyavgHTD',

    'percent_savings_hourlyavgHTD_baseline90',
    'avoided_daily_mean_core_day_runtime_hourlyavgHTD_baseline90',
    'avoided_total_core_day_runtime_hourlyavgHTD_baseline90',
    'baseline_daily_mean_core_day_runtime_hourlyavgHTD_baseline90',
    'baseline_total_core_day_runtime_hourlyavgHTD_baseline90',
    '_daily_mean_core_day_demand_baseline_hourlyavgHTD_baseline90',
    'percent_savings_hourlyavgHTD_baseline_regional',
    'avoided_daily_mean_core_day_runtime_hourlyavgHTD_baseline_regional',
    'avoided_total_core_day_runtime_hourlyavgHTD_baseline_regional',
    'baseline_daily_mean_core_day_runtime_hourlyavgHTD_baseline_regional',
    'baseline_total_core_day_runtime_hourlyavgHTD_baseline_regional',
    '_daily_mean_core_day_demand_baseline_hourlyavgHTD_baseline_regional',
    'mean_demand_hourlyavgHTD',
    'alpha_hourlyavgHTD',
    'tau_hourlyavgHTD',
    'mean_sq_err_hourlyavgHTD',
    'root_mean_sq_err_hourlyavgHTD',
    'cv_root_mean_sq_err_hourlyavgHTD',
    'mean_abs_err_hourlyavgHTD',
    'mean_abs_pct_err_hourlyavgHTD',

    'total_core_heating_runtime',
    'total_auxiliary_heating_core_day_runtime',
    'total_emergency_heating_core_day_runtime',

    'daily_mean_core_heating_runtime',

    'rhu_00F_to_05F',
    'rhu_05F_to_10F',
    'rhu_10F_to_15F',
    'rhu_15F_to_20F',
    'rhu_20F_to_25F',
    'rhu_25F_to_30F',
    'rhu_30F_to_35F',
    'rhu_35F_to_40F',
    'rhu_40F_to_45F',
    'rhu_45F_to_50F',
    'rhu_50F_to_55F',
    'rhu_55F_to_60F',
]

REAL_OR_INTEGER_VALUED_COLUMNS_COOLING = [
    'n_days_in_inputfile_date_range',
    'n_days_both_heating_and_cooling',
    'n_days_insufficient_data',
    'n_core_cooling_days',

    'baseline10_core_cooling_comfort_temperature',
    'regional_average_baseline_cooling_comfort_temperature',

    'percent_savings_deltaT_cooling_baseline10',
    'avoided_daily_mean_core_day_runtime_deltaT_cooling_baseline10',
    'avoided_total_core_day_runtime_deltaT_cooling_baseline10',
    'baseline_daily_mean_core_day_runtime_deltaT_cooling_baseline10',
    'baseline_total_core_day_runtime_deltaT_cooling_baseline10',
    '_daily_mean_core_day_demand_baseline_deltaT_cooling_baseline10',
    'percent_savings_deltaT_cooling_baseline_regional',
    'avoided_daily_mean_core_day_runtime_deltaT_cooling_baseline_regional',
    'avoided_total_core_day_runtime_deltaT_cooling_baseline_regional',
    'baseline_daily_mean_core_day_runtime_deltaT_cooling_baseline_regional',
    'baseline_total_core_day_runtime_deltaT_cooling_baseline_regional',
    '_daily_mean_core_day_demand_baseline_deltaT_cooling_baseline_regional',
    'mean_demand_deltaT_cooling',
    'alpha_deltaT_cooling',
    'tau_deltaT_cooling',
    'mean_sq_err_deltaT_cooling',
    'root_mean_sq_err_deltaT_cooling',
    'cv_root_mean_sq_err_deltaT_cooling',
    'mean_abs_err_deltaT_cooling',
    'mean_abs_pct_err_deltaT_cooling',

    'percent_savings_dailyavgCTD_baseline10',
    'avoided_daily_mean_core_day_runtime_dailyavgCTD_baseline10',
    'avoided_total_core_day_runtime_dailyavgCTD_baseline10',
    'baseline_daily_mean_core_day_runtime_dailyavgCTD_baseline10',
    'baseline_total_core_day_runtime_dailyavgCTD_baseline10',
    '_daily_mean_core_day_demand_baseline_dailyavgCTD_baseline10',
    'percent_savings_dailyavgCTD_baseline_regional',
    'avoided_daily_mean_core_day_runtime_dailyavgCTD_baseline_regional',
    'avoided_total_core_day_runtime_dailyavgCTD_baseline_regional',
    'baseline_daily_mean_core_day_runtime_dailyavgCTD_baseline_regional',
    'baseline_total_core_day_runtime_dailyavgCTD_baseline_regional',
    '_daily_mean_core_day_demand_baseline_dailyavgCTD_baseline_regional',
    'mean_demand_dailyavgCTD',
    'alpha_dailyavgCTD',
    'tau_dailyavgCTD',
    'mean_sq_err_dailyavgCTD',
    'root_mean_sq_err_dailyavgCTD',
    'cv_root_mean_sq_err_dailyavgCTD',
    'mean_abs_err_dailyavgCTD',
    'mean_abs_pct_err_dailyavgCTD',

    'percent_savings_hourlyavgCTD_baseline10',
    'avoided_daily_mean_core_day_runtime_hourlyavgCTD_baseline10',
    'avoided_total_core_day_runtime_hourlyavgCTD_baseline10',
    'baseline_daily_mean_core_day_runtime_hourlyavgCTD_baseline10',
    'baseline_total_core_day_runtime_hourlyavgCTD_baseline10',
    '_daily_mean_core_day_demand_baseline_hourlyavgCTD_baseline10',
    'percent_savings_hourlyavgCTD_baseline_regional',
    'avoided_daily_mean_core_day_runtime_hourlyavgCTD_baseline_regional',
    'avoided_total_core_day_runtime_hourlyavgCTD_baseline_regional',
    'baseline_daily_mean_core_day_runtime_hourlyavgCTD_baseline_regional',
    'baseline_total_core_day_runtime_hourlyavgCTD_baseline_regional',
    '_daily_mean_core_day_demand_baseline_hourlyavgCTD_baseline_regional',
    'mean_demand_hourlyavgCTD',
    'alpha_hourlyavgCTD',
    'tau_hourlyavgCTD',
    'mean_sq_err_hourlyavgCTD',
    'root_mean_sq_err_hourlyavgCTD',
    'cv_root_mean_sq_err_hourlyavgCTD',
    'mean_abs_err_hourlyavgCTD',
    'mean_abs_pct_err_hourlyavgCTD',

    'total_core_cooling_runtime',

    'daily_mean_core_cooling_runtime',
]

REAL_OR_INTEGER_VALUED_COLUMNS_ALL = [
    'n_days_in_inputfile_date_range',
    'n_days_both_heating_and_cooling',
    'n_days_insufficient_data',
    'n_core_cooling_days',
    'n_core_heating_days',

    'baseline10_core_cooling_comfort_temperature',
    'baseline90_core_heating_comfort_temperature',
    'regional_average_baseline_cooling_comfort_temperature',
    'regional_average_baseline_heating_comfort_temperature',

    'percent_savings_deltaT_cooling_baseline10',
    'avoided_daily_mean_core_day_runtime_deltaT_cooling_baseline10',
    'avoided_total_core_day_runtime_deltaT_cooling_baseline10',
    'baseline_daily_mean_core_day_runtime_deltaT_cooling_baseline10',
    'baseline_total_core_day_runtime_deltaT_cooling_baseline10',
    '_daily_mean_core_day_demand_baseline_deltaT_cooling_baseline10',
    'percent_savings_deltaT_cooling_baseline_regional',
    'avoided_daily_mean_core_day_runtime_deltaT_cooling_baseline_regional',
    'avoided_total_core_day_runtime_deltaT_cooling_baseline_regional',
    'baseline_daily_mean_core_day_runtime_deltaT_cooling_baseline_regional',
    'baseline_total_core_day_runtime_deltaT_cooling_baseline_regional',
    '_daily_mean_core_day_demand_baseline_deltaT_cooling_baseline_regional',
    'mean_demand_deltaT_cooling',
    'alpha_deltaT_cooling',
    'tau_deltaT_cooling',
    'mean_sq_err_deltaT_cooling',
    'root_mean_sq_err_deltaT_cooling',
    'cv_root_mean_sq_err_deltaT_cooling',
    'mean_abs_err_deltaT_cooling',
    'mean_abs_pct_err_deltaT_cooling',

    'percent_savings_dailyavgCTD_baseline10',
    'avoided_daily_mean_core_day_runtime_dailyavgCTD_baseline10',
    'avoided_total_core_day_runtime_dailyavgCTD_baseline10',
    'baseline_daily_mean_core_day_runtime_dailyavgCTD_baseline10',
    'baseline_total_core_day_runtime_dailyavgCTD_baseline10',
    '_daily_mean_core_day_demand_baseline_dailyavgCTD_baseline10',
    'percent_savings_dailyavgCTD_baseline_regional',
    'avoided_daily_mean_core_day_runtime_dailyavgCTD_baseline_regional',
    'avoided_total_core_day_runtime_dailyavgCTD_baseline_regional',
    'baseline_daily_mean_core_day_runtime_dailyavgCTD_baseline_regional',
    'baseline_total_core_day_runtime_dailyavgCTD_baseline_regional',
    '_daily_mean_core_day_demand_baseline_dailyavgCTD_baseline_regional',
    'mean_demand_dailyavgCTD',
    'alpha_dailyavgCTD',
    'tau_dailyavgCTD',
    'mean_sq_err_dailyavgCTD',
    'root_mean_sq_err_dailyavgCTD',
    'cv_root_mean_sq_err_dailyavgCTD',
    'mean_abs_err_dailyavgCTD',
    'mean_abs_pct_err_dailyavgCTD',

    'percent_savings_hourlyavgCTD_baseline10',
    'avoided_daily_mean_core_day_runtime_hourlyavgCTD_baseline10',
    'avoided_total_core_day_runtime_hourlyavgCTD_baseline10',
    'baseline_daily_mean_core_day_runtime_hourlyavgCTD_baseline10',
    'baseline_total_core_day_runtime_hourlyavgCTD_baseline10',
    '_daily_mean_core_day_demand_baseline_hourlyavgCTD_baseline10',
    'percent_savings_hourlyavgCTD_baseline_regional',
    'avoided_daily_mean_core_day_runtime_hourlyavgCTD_baseline_regional',
    'avoided_total_core_day_runtime_hourlyavgCTD_baseline_regional',
    'baseline_daily_mean_core_day_runtime_hourlyavgCTD_baseline_regional',
    'baseline_total_core_day_runtime_hourlyavgCTD_baseline_regional',
    '_daily_mean_core_day_demand_baseline_hourlyavgCTD_baseline_regional',
    'mean_demand_hourlyavgCTD',
    'alpha_hourlyavgCTD',
    'tau_hourlyavgCTD',
    'mean_sq_err_hourlyavgCTD',
    'root_mean_sq_err_hourlyavgCTD',
    'cv_root_mean_sq_err_hourlyavgCTD',
    'mean_abs_err_hourlyavgCTD',
    'mean_abs_pct_err_hourlyavgCTD',

    'percent_savings_deltaT_heating_baseline90',
    'avoided_daily_mean_core_day_runtime_deltaT_heating_baseline90',
    'avoided_total_core_day_runtime_deltaT_heating_baseline90',
    'baseline_daily_mean_core_day_runtime_deltaT_heating_baseline90',
    'baseline_total_core_day_runtime_deltaT_heating_baseline90',
    '_daily_mean_core_day_demand_baseline_deltaT_heating_baseline90',
    'percent_savings_deltaT_heating_baseline_regional',
    'avoided_daily_mean_core_day_runtime_deltaT_heating_baseline_regional',
    'avoided_total_core_day_runtime_deltaT_heating_baseline_regional',
    'baseline_daily_mean_core_day_runtime_deltaT_heating_baseline_regional',
    'baseline_total_core_day_runtime_deltaT_heating_baseline_regional',
    '_daily_mean_core_day_demand_baseline_deltaT_heating_baseline_regional',
    'mean_demand_deltaT_heating',
    'alpha_deltaT_heating',
    'tau_deltaT_heating',
    'mean_sq_err_deltaT_heating',
    'root_mean_sq_err_deltaT_heating',
    'cv_root_mean_sq_err_deltaT_heating',
    'mean_abs_err_deltaT_heating',
    'mean_abs_pct_err_deltaT_heating',

    'percent_savings_dailyavgHTD_baseline90',
    'avoided_daily_mean_core_day_runtime_dailyavgHTD_baseline90',
    'avoided_total_core_day_runtime_dailyavgHTD_baseline90',
    'baseline_daily_mean_core_day_runtime_dailyavgHTD_baseline90',
    'baseline_total_core_day_runtime_dailyavgHTD_baseline90',
    '_daily_mean_core_day_demand_baseline_dailyavgHTD_baseline90',
    'percent_savings_dailyavgHTD_baseline_regional',
    'avoided_daily_mean_core_day_runtime_dailyavgHTD_baseline_regional',
    'avoided_total_core_day_runtime_dailyavgHTD_baseline_regional',
    'baseline_daily_mean_core_day_runtime_dailyavgHTD_baseline_regional',
    'baseline_total_core_day_runtime_dailyavgHTD_baseline_regional',
    '_daily_mean_core_day_demand_baseline_dailyavgHTD_baseline_regional',
    'mean_demand_dailyavgHTD',
    'alpha_dailyavgHTD',
    'tau_dailyavgHTD',
    'mean_sq_err_dailyavgHTD',
    'root_mean_sq_err_dailyavgHTD',
    'cv_root_mean_sq_err_dailyavgHTD',
    'mean_abs_err_dailyavgHTD',
    'mean_abs_pct_err_dailyavgHTD',

    'percent_savings_hourlyavgHTD_baseline90',
    'avoided_daily_mean_core_day_runtime_hourlyavgHTD_baseline90',
    'avoided_total_core_day_runtime_hourlyavgHTD_baseline90',
    'baseline_daily_mean_core_day_runtime_hourlyavgHTD_baseline90',
    'baseline_total_core_day_runtime_hourlyavgHTD_baseline90',
    '_daily_mean_core_day_demand_baseline_hourlyavgHTD_baseline90',
    'percent_savings_hourlyavgHTD_baseline_regional',
    'avoided_daily_mean_core_day_runtime_hourlyavgHTD_baseline_regional',
    'avoided_total_core_day_runtime_hourlyavgHTD_baseline_regional',
    'baseline_daily_mean_core_day_runtime_hourlyavgHTD_baseline_regional',
    'baseline_total_core_day_runtime_hourlyavgHTD_baseline_regional',
    '_daily_mean_core_day_demand_baseline_hourlyavgHTD_baseline_regional',
    'mean_demand_hourlyavgHTD',
    'alpha_hourlyavgHTD',
    'tau_hourlyavgHTD',
    'mean_sq_err_hourlyavgHTD',
    'root_mean_sq_err_hourlyavgHTD',
    'cv_root_mean_sq_err_hourlyavgHTD',
    'mean_abs_err_hourlyavgHTD',
    'mean_abs_pct_err_hourlyavgHTD',

    'total_core_cooling_runtime',
    'total_core_heating_runtime',
    'total_auxiliary_heating_core_day_runtime',
    'total_emergency_heating_core_day_runtime',

    'daily_mean_core_cooling_runtime',
    'daily_mean_core_heating_runtime',

    'rhu_00F_to_05F',
    'rhu_05F_to_10F',
    'rhu_10F_to_15F',
    'rhu_15F_to_20F',
    'rhu_20F_to_25F',
    'rhu_25F_to_30F',
    'rhu_30F_to_35F',
    'rhu_35F_to_40F',
    'rhu_40F_to_45F',
    'rhu_45F_to_50F',
    'rhu_50F_to_55F',
    'rhu_55F_to_60F',
]

class ZipcodeGroupSpec(object):
    """ Mapping from zipcodes to groups. Must supply either filepath or
    dictionary.

    Parameters
    ----------
    filepath : str, None
        Path to CSV file containing the columns "zipcode" and "group".
        Each row should map the zipcode column to a target group. E.g.::

            zipcode,group
            01234,group_a
            12345,group_a
            23456,group_a
            43210,groub_b
            54321,group_b
            65432,group_c

        This creates the following grouping:

        - **group_a**: 01234,12345,23456
        - **group_b**: 43210,54321
        - **group_c**: 65432

    dictionary : dict, None
        Dictionary with zipcodes as keys and groups as values. E.g.::

            dictionary = {
                "01234": "group_a",
                "12345": "group_a",
                "23456": "group_a",
                "43210": "group_b",
                "54321": "group_b",
                "65432": "group_c",
            }

        This creates the following grouping:

        - **group_a**: 01234,12345,23456
        - **group_b**: 43210,54321
        - **group_c**: 65432

    label : str
        Extra label identifying the grouping method, for use in cases in which
        there might be ambiguity.
    """

    def __init__(self, filepath=None, dictionary=None, label=None):
        if filepath is not None:
            self.spec = self._load_spec_csv(filepath)
        elif dictionary is not None:
            self.spec = dictionary
        else:
            message = "Please supply either filepath or dictionary."
            raise ValueError(message)

        self.label = label

    def _load_spec_csv(self, filepath):
        df = pd.read_csv(filepath,
                usecols=["zipcode", "group"],
                dtype={"zipcode":str, "group":str})
        return {row["zipcode"]: row["group"] for _, row in df.iterrows()}

    def iter_groups(self, df):
        """ Iterate over groups (in no particular order.)

        Parameters
        ----------
        df : pd.Dataframe
            Dataframe containing all output data from which to draw groupings.
        """

        # avoid adding extra column to input df
        df = df.copy()

        df["_group"] = pd.Series([self.spec.get(zipcode) for zipcode in df["zipcode"]])
        for group, grouped in df.groupby("_group"):
            group_name = group if self.label is None else "{}_{}".format(group, self.label)
            yield group_name, grouped


def combine_output_dataframes(dfs):
    """ Combines output dataframes. Useful when combining output from batches.

    Parameters
    ----------
    dfs : list of pd.DataFrame
        Output dataFrames to combine into one.

    Returns
    -------
    out : pd.DataFrame
        Dataframe with combined output metadata.

    """
    return pd.concat(dfs, ignore_index=True)

def compute_summary_statistics(df, label, target_method="dailyavg",
        target_error_metric="CVRMSE", target_error_max_value=np.inf,
        statistical_power_confidence=.95, statistical_power_ratio=.05):
    """ Computes summary statistics for the output dataframe. Computes the
    following statistics for each real-valued or integer valued column in
    the output dataframe: mean, standard error of the mean, and deciles.

    Parameters
    ----------
    df : pd.DataFrame
        Output for which to compute summary statistics.
    label : str
        Name for this set of thermostat outputs.
    target_method : {"dailyavg", "hourlyavg", "deltaT"}, default "dailyavg"
        Metric method by which samples will be filtered according to bad fits, and
        for which statistical power extrapolation is desired.
    target_error_metric : {"MSE", "RMSE", "CVRMSE", "MAE", "MAPE"}, default "CVRMSE"
        Error metric to use when determining thermostat-core-day-set inclusion in
        statistics output.
    target_error_max_value : float, default np.inf
        Maximum acceptable value for error metric defined by target_error_metric.
    statistical_power_confidence : float in range 0 to 1, default .95
        Confidence interval to use in estimated statistical power calculation.
    statistical_power_ratio : float in range 0 to 1, default .05
        Ratio of standard error to mean desired in statistical power calculation.

    Returns
    -------
    stats : collections.OrderedDict
        An ordered dict containing the summary statistics. Column names are as
        follows, in which ### is a placeholder for the name of the column:

          - mean: ###_mean
          - standard error of the mean: ###_sem
          - 10th quantile: ###_10q
          - 20th quantile: ###_20q
          - 30th quantile: ###_30q
          - 40th quantile: ###_40q
          - 50th quantile: ###_50q
          - 60th quantile: ###_60q
          - 70th quantile: ###_70q
          - 80th quantile: ###_80q
          - 90th quantile: ###_90q
          - number of non-null core day sets: ###_n

        The following general values are also output:

          - label: label
          - number of total core day sets: n_total_core_day_sets

    """

    if target_method not in ["dailyavg", "hourlyavg", "deltaT"]:
        message = 'Method not supported - please use one of "dailyavg",' \
                '"hourlyavg", or "deltaT"'
        raise ValueError(message)

    def _statistical_power_estimate(core_day_set_type_stats, core_day_set_type):

        if core_day_set_type == "heating":
            if target_method == "deltaT":
                method = "{}_heating_baseline90".format(target_method)
            else:
                method = "{}HTD_baseline90".format(target_method)

            stat_power_target_mean = "percent_savings_{}_mean".format(method)
            stat_power_target_sem = "percent_savings_{}_sem".format(method)
            stat_power_target_n = "percent_savings_{}_n".format(method)
        else:
            if target_method == "deltaT":
                method = "{}_cooling_baseline10".format(target_method)
            else:
                method = "{}CTD_baseline10".format(target_method)

            stat_power_target_mean = "percent_savings_{}_mean".format(method)
            stat_power_target_sem = "percent_savings_{}_sem".format(method)
            stat_power_target_n = "percent_savings_{}_n".format(method)

        mean = core_day_set_type_stats[stat_power_target_mean]
        sem = core_day_set_type_stats[stat_power_target_sem]
        n = core_day_set_type_stats[stat_power_target_n]

        n_std_devs = norm.ppf(1 - (1 - statistical_power_confidence)/2)
        std = sem * (n**.5)
        target_interval = mean * statistical_power_ratio
        target_n = (std * n_std_devs / target_interval) ** 2.
        return target_n

    def _filter_rows(core_day_set_type_df, core_day_set_type):
        filtered_df_rows = []
        for i, row in core_day_set_type_df.iterrows():
            if _accept_row(row, core_day_set_type):
                filtered_df_rows.append(row)
        return pd.DataFrame(filtered_df_rows)

    def _accept_row(row, core_day_set_type):
        passes_validity_rules = _passes_validity_rules(row)
        has_physical_tau = _has_physical_tau(row, core_day_set_type)
        has_good_enough_fit = _has_good_enough_fit(row, core_day_set_type)
        return (
            passes_validity_rules
            and has_physical_tau
            and has_good_enough_fit
        )

    def _passes_validity_rules(row):
        try:
            pct_insufficient_data = row.n_days_insufficient_data / row.n_days_in_inputfile_date_range
        except ZeroDivisionError:
            return False
        else:
            return pct_insufficient_data < 0.05

    def _has_physical_tau(row, core_day_set_type):
        if target_method == "deltaT":
            if core_day_set_type == "heating":
                column = "tau_deltaT_heating"
            else:
                column = "tau_deltaT_cooling"
        else:
            if core_day_set_type == "heating":
                column = "tau_{}HTD".format(target_method)
            else:
                column = "tau_{}CTD".format(target_method)

        return -10 <= row[column] <= 50

    def _has_good_enough_fit(row, core_day_set_type):
        if target_error_metric == "MSE":
            error_metric_prefix = "mean_sq_err"
        elif target_error_metric == "RMSE":
            error_metric_prefix = "root_mean_sq_err"
        elif target_error_metric == "CVRMSE":
            error_metric_prefix = "cv_root_mean_sq_err"
        elif target_error_metric == "MAE":
            error_metric_prefix = "mean_abs_err"
        elif target_error_metric == "MAPE":
            error_metric_prefix = "mean_abs_pct_err"
        else:
            message = (
                'Method {} not supported.'
                ' Use one of "MSE", "RMSE", "CVRMSE", "MAE", or "MAPE".'
            ).format(target_error_metric)
            raise ValueError(message)

        if target_method == "deltaT":
            if core_day_set_type == "heating":
                method_suffix = "deltaT_heating"
            else:
                method_suffix = "deltaT_cooling"
        else:
            if core_day_set_type == "heating":
                method_suffix = "{}HTD".format(target_method)
            else:
                method_suffix = "{}CTD".format(target_method)

        column = "{}_{}".format(error_metric_prefix, method_suffix)

        return row[column] < target_error_max_value

    def _get_core_day_set_type_stats(core_day_set_type_df, core_day_set_type, core_day_set_type_columns):
        n_core_day_sets_total = core_day_set_type_df.shape[0]

        filtered_core_day_set_type_df = _filter_rows(core_day_set_type_df, core_day_set_type)

        n_core_day_sets_kept = filtered_core_day_set_type_df.shape[0]
        n_core_day_sets_discarded = n_core_day_sets_total - n_core_day_sets_kept

        core_day_set_type_stats = OrderedDict()
        core_day_set_type_stats["label"] = "{}_{}".format(label, core_day_set_type)
        core_day_set_type_stats["sw_version"] = get_version()
        core_day_set_type_stats["n_thermostat_core_day_sets_total"] = n_core_day_sets_total
        core_day_set_type_stats["n_thermostat_core_day_sets_kept"] = n_core_day_sets_kept
        core_day_set_type_stats["n_thermostat_core_day_sets_discarded"] = n_core_day_sets_discarded

        if n_core_day_sets_total > 0:

            quantiles = [10, 20, 30, 40, 50, 60, 70, 80, 90]

            for column_name in core_day_set_type_columns:
                column = core_day_set_type_df[column_name].replace([np.inf, -np.inf], np.nan).dropna()

                # calculate quantiles
                core_day_set_type_stats["{}_mean".format(column_name)] = np.nanmean(column)
                core_day_set_type_stats["{}_sem".format(column_name)] = np.nanstd(column) / (column.count() ** .5)
                core_day_set_type_stats["{}_n".format(column_name)] = column.count()
                for quantile in quantiles:
                    core_day_set_type_stats["{}_q{}".format(column_name, quantile)] = column.quantile(quantile / 100.)

            core_day_set_type_stats["n_enough_statistical_power"] = \
                    _statistical_power_estimate(core_day_set_type_stats, core_day_set_type)

            return [core_day_set_type_stats]
        else:
            message = "Not enough data to compute summary_statistics for {} {}".format(label, core_day_set_type)
            warn(message)
            return []


    heating_df = df[["heating" in name for name in df["heating_or_cooling"]]]
    cooling_df = df[["cooling" in name for name in df["heating_or_cooling"]]]

    stats = _get_core_day_set_type_stats(heating_df, "heating", REAL_OR_INTEGER_VALUED_COLUMNS_HEATING)
    stats.extend(_get_core_day_set_type_stats(cooling_df, "cooling", REAL_OR_INTEGER_VALUED_COLUMNS_COOLING))

    return stats

def compute_summary_statistics_by_zipcode_group(df,
        filepath=None, dictionary=None, group_spec=None, weights=None,
        target_method="dailyavg", target_error_metric="CVRMSE",
        target_error_max_value=np.inf, statistical_power_confidence=.95,
        statistical_power_ratio=.05):
    """ Filepath to zipcode -> group mapping. Note that this mapping should
    include all zipcodes that may appear in the raw output file dataframe. Any
    zipcodes which do not appear in the mapping but do occur in the ouput data
    will be ignored. The mapping can, however, include zipcodes that do not
    appear in the raw output data.

    Parameters
    ----------
    filepath : str, None
        Path to CSV file containing the columns "zipcode" and "group".
        Each row should map the zipcode column to a target group. E.g.::

            zipcode,group
            01234,group_a
            12345,group_a
            23456,group_a
            43210,groub_b
            54321,group_b
            65432,group_c

        This creates the following grouping:

        - **group_a**: 01234,12345,23456
        - **group_b**: 43210,54321
        - **group_c**: 65432

    dictionary : dict, None
        Dictionary with zipcodes as keys and groups as values. E.g.::

            dictionary = {
                "01234": "group_a",
                "12345": "group_a",
                "23456": "group_a",
                "43210": "group_b",
                "54321": "group_b",
                "65432": "group_c",
            }

        This creates the following grouping:

        - **group_a**: 01234,12345,23456
        - **group_b**: 43210,54321
        - **group_c**: 65432

    group_spec : ZipcodeGroupSpec object
        Initialized group spec object containing a zipcode -> group mapping.
    weights : dict
        Object containing weightings for heating and cooling, by group.
    target_method : {"dailyavg", "hourlyavg", "deltaT"}, default "dailyavg"
        Metric method by which samples will be filtered according to bad fits, and
        for which statistical power extrapolation is desired.
    target_error_metric : {"MSE", "RMSE", "CVRMSE", "MAE", "MAPE"}, default "CVRMSE"
        Error metric to use when determining thermostat-core-day-set inclusion in
        statistics output.
    target_error_max_value : float, default np.inf
        Maximum acceptable value for error metric defined by target_error_metric.
    statistical_power_confidence : float in range 0 to 1, default .95
        Confidence interval to use in estimated statistical power calculation.
    statistical_power_ratio : float in range 0 to 1, default .05
        Ratio of standard error to mean desired in statistical power calculation.

    Returns
    -------
    stats : list of dict
        List of stats dictionaries computed by group.

    """
    if group_spec is not None:
        pass
    elif filepath is not None:
        group_spec = ZipcodeGroupSpec(filepath=filepath)
    elif dictionary is not None:
        group_spec = ZipcodeGroupSpec(dictionary=dictionary)
    else:
        message = "Please supply either the filepath of a CSV file, a" \
                "dictionary, or a ZipcodeGroupSpec object"
        raise ValueError(message)

    if weights is not None:
        with open(weights, 'r') as f:
            national_weights = json.load(f)
    else:
        national_weights = None

    stats = []
    for label, group_df in group_spec.iter_groups(df):
        summary_statistics = compute_summary_statistics(group_df, label,
                target_method=target_method,
                target_error_metric=target_error_metric,
                target_error_max_value=target_error_max_value,
                statistical_power_confidence=statistical_power_confidence,
                statistical_power_ratio=statistical_power_ratio)
        stats.extend(summary_statistics)

    if national_weights is not None:

        heating_groups = { component: key
                for key, value in national_weights["heating"].items()
                for component in value["components"]}
        heating_weights = { key: value["weight"]
                for key, value in national_weights["heating"].items()}

        cooling_groups = { component: key
                for key, value in national_weights["cooling"].items()
                for component in value["components"]}
        cooling_weights = { key: value["weight"]
                for key, value in national_weights["cooling"].items()}

        heating_weight_groups = heating_weights.keys()
        cooling_weight_groups = cooling_weights.keys()
        heating_values = { wg: {"means":[], "medians": [], "counts": [], "weight": heating_weights[wg]} for wg in heating_weight_groups}
        cooling_values = { wg: {"means":[], "medians": [], "counts": [], "weight": cooling_weights[wg]} for wg in cooling_weight_groups}

        for stat in stats:
            label = stat["label"]
            category = label[-7:]
            group = label[:-8]
            count = stat["n_thermostat_core_day_sets_kept"]

            if category == "heating":
                if target_method == "deltaT":
                    method = "deltaT_heating_baseline90"
                else:
                    method = "{}HTD_baseline90".format(target_method)

                weight_group = heating_groups[group]
                mean_value = stat["percent_savings_{}_mean".format(method)]
                median_value = stat["percent_savings_{}_q50".format(method)]
                heating_values[weight_group]["means"].append(mean_value)
                heating_values[weight_group]["medians"].append(median_value)
                heating_values[weight_group]["counts"].append(count)
            else:
                if target_method == "deltaT":
                    method = "deltaT_cooling_baseline10"
                else:
                    method = "{}CTD_baseline10".format(target_method)

                weight_group = cooling_groups[group]
                mean_value = stat["percent_savings_{}_mean".format(method)]
                median_value = stat["percent_savings_{}_q50".format(method)]
                cooling_values[weight_group]["means"].append(mean_value)
                cooling_values[weight_group]["medians"].append(median_value)
                cooling_values[weight_group]["counts"].append(count)

        national_heating_mean_numerator = 0
        national_heating_median_numerator = 0
        national_heating_denominator = 0
        for values in heating_values.values():
            if len(values["means"]) == 0:
                continue
            mean_numerator = 0
            median_numerator = 0
            denominator = 0
            for median, mean, count in zip(values["means"], values["medians"], values["counts"]):
                median_numerator += median * count
                mean_numerator += mean * count
                denominator += count
            try:
                national_heating_mean_numerator += (mean_numerator / denominator) * values["weight"]
                national_heating_median_numerator += (median_numerator / denominator) * values["weight"]
                national_heating_denominator += values["weight"]
            except ZeroDivisionError:
                pass

        try:
            heating_mean = (national_heating_mean_numerator / national_heating_denominator)
        except ZeroDivisionError:
            heating_mean = np.nan
        try:
            heating_median = (national_heating_median_numerator / national_heating_denominator)
        except ZeroDivisionError:
            heating_median = np.nan

        national_cooling_mean_numerator = 0
        national_cooling_median_numerator = 0
        national_cooling_denominator = 0
        for values in cooling_values.values():
            if len(values["means"]) == 0:
                continue
            mean_numerator = 0
            median_numerator = 0
            denominator = 0
            for median, mean, count in zip(values["means"], values["medians"], values["counts"]):
                median_numerator += median * count
                mean_numerator += mean * count
                denominator += count
            try:
                national_cooling_mean_numerator += (mean_numerator / denominator) * values["weight"]
                national_cooling_median_numerator += (median_numerator / denominator) * values["weight"]
                national_cooling_denominator += values["weight"]
            except ZeroDivisionError:
                pass

        try:
            cooling_mean = (national_cooling_mean_numerator / national_cooling_denominator)
        except ZeroDivisionError:
            cooling_mean = np.nan
        try:
            cooling_median = (national_cooling_median_numerator / national_cooling_denominator)
        except ZeroDivisionError:
            cooling_median = np.nan


        if target_method == "deltaT":
            method = "deltaT_heating_baseline90"
        else:
            method = "{}HTD_baseline90".format(target_method)
        stats.append({
            "label": "national_heating",
            "percent_savings_{}_mean_national_weighted_mean".format(method): heating_mean,
            "percent_savings_{}_q50_national_weighted_mean".format(method): heating_median,
        })

        if target_method == "deltaT":
            method = "deltaT_cooling_baseline10"
        else:
            method = "{}CTD_baseline10".format(target_method)
        stats.append({
            "label": "national_cooling",
            "percent_savings_{}_mean_national_weighted_mean".format(method): cooling_mean,
            "percent_savings_{}_q50_national_weighted_mean".format(method): cooling_median,
        })

    return stats


def compute_summary_statistics_by_zipcode(df, target_method="dailyavg",
        target_error_metric="CVRMSE", target_error_max_value=np.inf,
        statistical_power_confidence=.95, statistical_power_ratio=.05):
    """ Compute summary statistics for a particular dataframe by zipcode.

    Parameters
    ----------
    df : pd.Dataframe
        Contains combined (not yet grouped) output data for all thermostats in
        the sample.
    target_method : {"dailyavg", "hourlyavg", "deltaT"}, default "dailyavg"
        Metric method by which samples will be filtered according to bad fits, and
        for which statistical power extrapolation is desired.
    target_error_metric : {"MSE", "RMSE", "CVRMSE", "MAE", "MAPE"}, default "CVRMSE"
        Error metric to use when determining thermostat-core-day-set inclusion in
        statistics output.
    target_error_max_value : float, default np.inf
        Maximum acceptable value for error metric defined by target_error_metric.
    statistical_power_confidence : float in range 0 to 1, default .95
        Confidence interval to use in estimated statistical power calculation.
    statistical_power_ratio : float in range 0 to 1, default .05
        Ratio of standard error to mean desired in statistical power calculation.

    Returns
    -------
    stats : list of dict
        Summary statistics for the input dataframe grouped by USPS ZIP code.
    """
    # Map zipcodes to themselves.
    zipcode_dict = { z: z for z in _load_zipcode_to_lat_lng_index().keys()}
    group_spec = ZipcodeGroupSpec(dictionary=zipcode_dict)

    stats = compute_summary_statistics_by_zipcode_group(df,
            group_spec=group_spec,
            target_method=target_method,
            target_error_metric=target_error_metric,
            target_error_max_value=target_error_max_value,
            statistical_power_confidence=statistical_power_confidence,
            statistical_power_ratio=statistical_power_ratio)
    return stats

def compute_summary_statistics_by_weather_station(df, target_method="dailyavg",
        target_error_metric="CVRMSE", target_error_max_value=np.inf,
        statistical_power_confidence=.95, statistical_power_ratio=.05):
    """ Compute summary statistics for a particular dataframe by weather
    weather station used to find outdoor temperature data

    Parameters
    ----------
    df : pd.Dataframe
        Contains combined (not yet grouped) output data for all thermostats in
        the sample.
    target_method : {"dailyavg", "hourlyavg", "deltaT"}, default "dailyavg"
        Metric method by which samples will be filtered according to bad fits, and
        for which statistical power extrapolation is desired.
    target_error_metric : {"MSE", "RMSE", "CVRMSE", "MAE", "MAPE"}, default "CVRMSE"
        Error metric to use when determining thermostat-core-day-set inclusion in
        statistics output.
    target_error_max_value : float, default np.inf
        Maximum acceptable value for error metric defined by target_error_metric.
    statistical_power_confidence : float in range 0 to 1, default .95
        Confidence interval to use in estimated statistical power calculation.
    statistical_power_ratio : float in range 0 to 1, default .05
        Ratio of standard error to mean desired in statistical power calculation.

    Returns
    -------
    stats : list of dict
        Summary statistics for the input dataframe grouped by weather station
        used to find outdoor temperature data.
    """
    # Map zipcodes to stations. This is the same mapping used to match outdoor
    # temperature data.
    zipcode_dict = _load_zipcode_to_station_index()
    group_spec = ZipcodeGroupSpec(dictionary=zipcode_dict)

    stats = compute_summary_statistics_by_zipcode_group(df, group_spec=group_spec,
        target_method=target_method,
        target_error_metric=target_error_metric,
        target_error_max_value=target_error_max_value,
        statistical_power_confidence=statistical_power_confidence,
        statistical_power_ratio=statistical_power_ratio)
    return stats

def summary_statistics_to_csv(stats, filepath):
    """ Write metric statistics to CSV file.

    Parameters
    ----------
    stats : list of dict
        List of outputs from thermostat.stats.compute_summary_statistics()
    filepath : str
        Filepath at which to save the suppary statistics

    Returns
    -------
    df : pandas.DataFrame
        A pandas dataframe containing the output data.

    """
    quantiles = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    columns = [
        "label",
        "sw_version",
        "n_thermostat_core_day_sets_total",
        "n_thermostat_core_day_sets_kept",
        "n_thermostat_core_day_sets_discarded",
        "n_enough_statistical_power"
    ]
    for column_name in REAL_OR_INTEGER_VALUED_COLUMNS_ALL:
        columns.append("{}_mean".format(column_name))
        columns.append("{}_sem".format(column_name))
        columns.append("{}_n".format(column_name))
        for quantile in quantiles:
            columns.append("{}_q{}".format(column_name, quantile))

    columns += [
        "percent_savings_dailyavgCTD_baseline10_mean_national_weighted_mean",
        "percent_savings_dailyavgHTD_baseline90_mean_national_weighted_mean",
        "percent_savings_deltaT_cooling_baseline10_mean_national_weighted_mean",
        "percent_savings_deltaT_heating_baseline90_mean_national_weighted_mean",
        "percent_savings_hourlyavgCTD_baseline10_mean_national_weighted_mean",
        "percent_savings_hourlyavgHTD_baseline90_mean_national_weighted_mean",

        "percent_savings_dailyavgCTD_baseline10_q50_national_weighted_mean",
        "percent_savings_dailyavgHTD_baseline90_q50_national_weighted_mean",
        "percent_savings_deltaT_cooling_baseline10_q50_national_weighted_mean",
        "percent_savings_deltaT_heating_baseline90_q50_national_weighted_mean",
        "percent_savings_hourlyavgCTD_baseline10_q50_national_weighted_mean",
        "percent_savings_hourlyavgHTD_baseline90_q50_national_weighted_mean",
    ]

    stats_dataframe = pd.DataFrame(stats, columns=columns)
    stats_dataframe.to_csv(filepath, index=False, columns=columns)
    return stats_dataframe
