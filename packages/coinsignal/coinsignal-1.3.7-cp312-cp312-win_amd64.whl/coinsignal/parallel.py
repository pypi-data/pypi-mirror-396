# --------------------------------------------------------------------------------
# Copyright (c) 2025 Zehao Yang
#
# Author: Zehao Yang
#
# This module implements parallel processing for feature preparation:
# • Parallelizing data reading, feature and label calculations, sampling
# • Progress tracking for parallel processing across multiple dates
# --------------------------------------------------------------------------------


import pandas as pd
from threading import Thread
from multiprocessing import Manager
from joblib import Parallel, delayed
import _ext.parallel as _parallel


def prepare_sub_full_features_df(data_dir, date, look_back_days, look_ahead_days, constants_dict, data_params_dict, feature_params_dict, return_params_dict, sampler_params_dict, N, n_completed, progress_update_event):
    return _parallel.prepare_sub_full_features_df(data_dir, date, look_back_days, look_ahead_days, constants_dict, data_params_dict, feature_params_dict, return_params_dict, sampler_params_dict, N, n_completed, progress_update_event)

def prepare_full_features_df(data_dir, start_date, end_date, look_back_days, look_ahead_days, constants_dict, data_params_dict, feature_params_dict, return_params_dict, sampler_params_dict):
    dates = pd.date_range(start_date, end_date).strftime('%Y-%m-%d')
    N = len(dates)
    manager = Manager()
    n_completed = manager.Value('i', 0)
    progress_update_event = manager.Event()
    progress_thread = Thread(target=_parallel.update_progress_bar, args=(n_completed, progress_update_event, N), daemon=True)
    progress_thread.start()
    results = Parallel(n_jobs=-1, verbose=0)(delayed(prepare_sub_full_features_df)(data_dir, date, look_back_days, look_ahead_days, constants_dict, data_params_dict, feature_params_dict, return_params_dict, sampler_params_dict, N, n_completed, progress_update_event) for date in dates)
    dfs = [result[0] for result in results]
    errors = [result[1] for result in results]
    n_completed.value = N
    progress_update_event.set()
    progress_thread.join(timeout=2.0)
    full_features_df = pd.concat(dfs, axis=0).sort_index()
    read_data_errors = sum(errors, [])
    return full_features_df, read_data_errors