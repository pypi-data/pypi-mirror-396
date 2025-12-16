# --------------------------------------------------------------------------------
# Copyright (c) 2025 Zehao Yang
#
# Author: Zehao Yang
#
# This module implements parallel processing for feature preparation:
# • Parallelizing data reading, feature and label calculations, sampling
# • Progress tracking for parallel processing across multiple dates
# --------------------------------------------------------------------------------


import _ext.parallel as _parallel


def prepare_full_features_df(data_dir, start_date, end_date, look_back_days, look_ahead_days, constants_dict, data_params_dict, feature_params_dict, return_params_dict, sampler_params_dict):
    return _parallel.prepare_full_features_df(data_dir, start_date, end_date, look_back_days, look_ahead_days, constants_dict, data_params_dict, feature_params_dict, return_params_dict, sampler_params_dict)