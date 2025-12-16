# --------------------------------------------------------------------------------
# Copyright (c) 2025 Zehao Yang
#
# Author: Zehao Yang
#
# This module implements return (label) calculation functions:
# • Calculating return values for multiple horizons and decay multipliers
# • Handling time, duration, and range return types
# • Supporting funding rate adjustment and discrete return calculation
# --------------------------------------------------------------------------------


import _ext.label as _label


DEFAULT_RETURN_PARAMS_DICT = {
    'horizons': [600],
    'decay_multipliers': [0.5, 0.8, 1, 1.5, 2, 3, 5, 10],
    'return_type': 'time',
    'range_merge_step': 1,
    'horizon_limit': 1,
    'n_multi': 1,
    'multi_limits': [1, 1],
    'half_life': 0,
    'duration_vlimits': None,
    'duration_qlimits': [0, 1],
    'duration_handling': '',
    'is_funding_adjusted': False,
    'is_discrete': False,
    'y_multiplier': 10000
}


def calculate_return(features_map, return_params_dict):
    return _label.calculate_return(features_map, return_params_dict)