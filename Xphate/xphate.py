# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the MIT License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import pandas as pd
from os.path import isfile, isdir

import phate
import itertools
import multiprocessing as mp
from sklearn.preprocessing import normalize
import altair as alt

from Xphate.filter import do_filter


def get_metadata(m_metadata: str, p_columns: tuple) -> (pd.DataFrame, str):
    metadata = pd.DataFrame()
    columns = []
    if m_metadata:
        with open(m_metadata) as f:
            for line in f:
                break
        metadata = pd.read_csv(
            m_metadata, header=0, sep='\t',
            dtype={line.split('\t')[0]: str}
        )
        metadata = metadata.rename(columns={metadata.columns.tolist()[0]: "sample_name"})
        metadata.columns = [x.replace('\n', '') for x in metadata.columns]
        for p_column in p_columns:
            if p_column in metadata.columns.tolist()[1:]:
                columns.append(p_column)
    return metadata, columns


def run_phate(fpo, tab_norm, knn, decays, ts, n_jobs, verbose):
    phate_op = phate.PHATE()
    data_phates = []
    if not knn:
        knn = 5
    for (decay, t) in itertools.product(*[decays, ts]):
        if not decay:
            decay = 15
        if not t:
            t = 'auto'
        phate_op.set_params(knn=knn, decay=decay, t=t, n_jobs=n_jobs, verbose=verbose)
        data_phate = pd.DataFrame(phate_op.fit_transform(tab_norm), columns=['PHATE1', 'PHATE2'])
        data_phate['knn'] = knn
        data_phate['decay'] = decay
        data_phate['t'] = t
        data_phate['sample_name'] = tab_norm.index.tolist()
        data_phates.append(data_phate)
    pd.concat(data_phates).to_csv(fpo, index=False, sep='\t')


def make_figure(i_table, i_res, figo, full_pds, ts, ts_step, decays, decays_step, knns, knns_step):

    text = []
    if i_table:
        text.append('PHATE for table "%s"' % i_table)
    elif i_res:
        text.append('PHATE for pre-computed table "%s"' % i_res)

    subtext = ['Parameters:']

    tooltip = ['sample_name', 'PHATE1', 'PHATE2']
    circ = alt.Chart(full_pds).mark_point(size=20).encode(
        x='PHATE1:Q',
        y='PHATE2:Q'
    )

    if knns_step:
        slider_knns = alt.binding_range(
            min=min(knns), max=max(knns), step=knns_step, name='knn')
        selector_knns = alt.selection_single(
            name="knn", fields=['knn'], bind=slider_knns, init={'knn': min(knns)})
        tooltip.append('knn')
        circ = circ.add_selection(
            selector_knns
        ).transform_filter(
            selector_knns
        )
        subtext.append('knn ("k") = %s\n' % ', '.join(map(str, knns)))

    if decays_step:
        slider_decays = alt.binding_range(
            min=min(decays), max=max(decays), step=decays_step, name='decay')
        selector_decays = alt.selection_single(
            name="decay", fields=['decay'], bind=slider_decays, init={'decay': min(decays)})
        tooltip.append('decay')
        circ = circ.add_selection(
            selector_decays
        ).transform_filter(
            selector_decays
        )
        subtext.append('decay ("alpha") = %s\n' % ', '.join(map(str, decays)))

    if ts_step:
        slider_ts = alt.binding_range(
            min=min(ts), max=max(ts), step=ts_step, name='t:')
        selector_ts = alt.selection_single(
            name="t", fields=['t'], bind=slider_ts, init={'t': min(ts)})
        tooltip.append('t')
        circ = circ.add_selection(
            selector_ts
        ).transform_filter(
            selector_ts
        )
        subtext.append('t = %s\n' % ', '.join(map(str, ts)))

    if 'variable' in full_pds.columns:
        variable_dropdown = alt.binding_select(
            options=full_pds['variable'].unique(), name='variable:')
        variable_select = alt.selection_single(
            fields=['variable'], bind=variable_dropdown, name="variable",
            init={'variable': sorted(full_pds['variable'], key=lambda x: -len(x))[0]})
        tooltip.extend(['variable', 'factor'])
        circ = circ.encode(
            color='factor:N'
        ).add_selection(
            variable_select
        ).transform_filter(
            variable_select
        )

    circ = circ.encode(tooltip=tooltip)

    title = {
        "text": text,
        "color": "black",
    }
    if subtext != ['Parameters:']:
        title.update({
            "subtitle": (subtext + ["(based on altair)"]),
            "subtitleColor": "grey"
        })

    circ = circ.resolve_legend(
        color="independent",
        size="independent"
    ).properties(
        width=400,
        height=400,
        title=title
    )

    circ.save(figo)
    print('-> Written:', figo)


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


def xphate(
        i_table: str,
        i_res: str,
        o_dir_path: str,
        m_metadata: str,
        p_columns: tuple = None,
        p_column: str = None,
        p_column_value: tuple = None,
        p_column_quant: int = 0,
        p_filter_prevalence: float = 0,
        p_filter_abundance: float = 0,
        p_filter_order: str = 'meta-filter',
        p_ts: tuple = None,
        p_decays: tuple = None,
        p_knns: tuple = None,
        p_jobs: int = 1,
        verbose: bool = False
    ):

    if verbose:
        verbose = 1
    else:
        verbose = 0

    ts_step, ts = get_param(p_ts)
    decays_step, decays = get_param(p_decays)
    knns_step, knns = get_param(p_knns)

    if i_res:
        full_pds = pd.read_csv(i_res, header=0, sep='\t', dtype={'sample_name': str})
    else:
        if not isfile(i_table):
            raise IOError("No input table found at %s" % i_table)
        if verbose:
            print('read')
        tab = pd.read_csv(i_table, header=0, index_col=0, sep='\t')
        if not isdir(o_dir_path):
            os.makedirs(o_dir_path)

        message = 'input'
        if m_metadata and p_column and p_column_value or p_filter_prevalence or p_filter_abundance:
            # Filter / Transform OTU-table
            tab = do_filter(tab, m_metadata, p_filter_prevalence,
                            p_filter_abundance, p_filter_order,
                            p_column, p_column_value, p_column_quant)
            message = 'filtered'
        if tab.shape[0] < 10:
            raise IOError('Too few features in the %s table' % message)

        tab_norm = pd.DataFrame(normalize(tab, norm='l1', axis=0), index=tab.index, columns=tab.columns).T
        jobs, fpos = [], []
        for knn in knns:
            fpo = '%s/phate_knn%s_multi_params.tsv' % (o_dir_path, knn)
            fpos.append(fpo)
            p = mp.Process(target=run_phate, args=(fpo, tab_norm, knn, decays, ts, p_jobs, verbose,))
            jobs.append(p)
            p.start()
        for j in jobs:
            j.join()

        full_pds = pd.concat([pd.read_csv(x, header=0, sep='\t', dtype={'sample_name': str}) for x in fpos])
        fpo = '%s/phate_knn_multi_params.tsv' % o_dir_path
        full_pds.to_csv(fpo, index=False, sep='\t')

    metadata, columns = pd.DataFrame(), []
    if m_metadata:
        if verbose:
            print('Read metadata...', end='')
        metadata, columns = get_metadata(m_metadata, p_columns)
        if verbose:
            print('done.')

    if metadata.shape[0] and len(columns):
        metadata = metadata[
            (['sample_name'] + columns)
        ].set_index(
            'sample_name'
        ).stack().reset_index().rename(
            columns={'level_1': 'variable', 0: 'factor'}
        )
        full_pds = full_pds.merge(metadata, on='sample_name', how='left')

    figo = '%s/phate_knn_multi_params.html' % o_dir_path
    make_figure(i_table, i_res, figo, full_pds, ts, ts_step, decays, decays_step, knns, knns_step)
