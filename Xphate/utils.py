# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the MIT License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd


def get_param(p_param):
    param_step = None
    param = [None]
    if len(p_param) == 3:
        param_step = p_param[-1]
        param = range(p_param[0], (p_param[1] + 1), param_step)
    elif len(p_param) == 1:
        param_step = None
        param = [p_param[0]]
    return param_step, param


def get_metadata(m_metadata: str, p_columns: tuple) -> (pd.DataFrame, str):
    metadata = pd.DataFrame()
    columns = []
    if m_metadata:
        with open(m_metadata) as f:
            for line in f:
                break
        metadata = pd.read_csv(m_metadata, header=0, sep='\t', dtype={line.split('\t')[0]: str})
        metadata = metadata.rename(columns={metadata.columns.tolist()[0]: 'sample_name'})
        metadata.columns = [x.replace('\n', '') for x in metadata.columns]
        for p_column in p_columns:
            if p_column in metadata.columns.tolist()[1:]:
                columns.append(p_column)
    return metadata, columns
