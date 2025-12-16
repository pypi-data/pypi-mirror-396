# --------------------------------------------------------------------------------
# Copyright (c) 2025 Zehao Yang
#
# Author: Zehao Yang
#
# This module implements data sampling functions:
# • Sampling data on time using time intervals
# • Sampling data on move using smoothed price change
# • Sampling data on return using weighted random sampling
# --------------------------------------------------------------------------------


import _ext.sampler as _sampler


DEFAULT_SAMPLER_PARAMS_DICT = {
    'sampling_time': 0,
    'is_time_random': False,
    'sampling_bp': 0,
    'rolling_step': 0,
    'is_sampling_on_ret': False,
    'fraction': 1,
    'weight_limit': 1,
    'is_sign_balanced': False,
}


def sample_data_on_time(price, sampling_time, is_time_random):
    return _sampler.sample_data_on_time(price, sampling_time, is_time_random)

def sample_data_on_move(price, sampling_bp, rolling_step):
    return _sampler.sample_data_on_move(price, sampling_bp, rolling_step)

def sample_data_on_ret(ret, fraction, weight_limit, is_sign_balanced):
    return _sampler.sample_data_on_ret(ret, fraction, weight_limit, is_sign_balanced)

def sample_data(features_map, sampler_params_dict):
    return _sampler.sample_data(features_map, sampler_params_dict)