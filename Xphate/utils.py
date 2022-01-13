# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the MIT License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd


def get_param(p_param, param, suffix):
    param_step = None
    param_range = [None]
    if len(p_param) == 3:
        param_step = p_param[-1]
        param_range = range(p_param[0], (p_param[1] + 1), param_step)
        suffix += '_%s-%s-%s-%s' % (
            param, p_param[0], (p_param[1] + 1), param_step)
    elif len(p_param) == 1:
        param_step = 1
        param_range = [p_param[0]]
        suffix += '_%s-%s' % (param, p_param[0])
    return param_step, param_range


def get_metadata(m_metadata: str, p_columns: tuple) -> (pd.DataFrame, str):
    metadata = pd.DataFrame()
    columns = []
    if m_metadata:
        with open(m_metadata) as f:
            for line in f:
                break
        first_var = line.split('\t')[0]
        metadata = pd.read_csv(m_metadata, header=0, sep='\t', dtype={first_var: str})
        metadata = metadata.rename(columns={first_var: 'sample_name'})
        cols = [x.replace('\n', '') for x in metadata.columns]
        metadata.columns = cols
        for p_column in p_columns:
            if p_column in cols:
                columns.append(p_column)
    return metadata, columns
