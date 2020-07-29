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


def run_phate(fpo, tab_norm, knn, decays, ts, n_jobs):
    phate_op = phate.PHATE()
    data_phates = []
    if decays and ts:
        for (decay, t) in itertools.product(*[decays, ts]):
            print('++++ %s :: %s :: %s ++++' % (knn, decay, t))
            phate_op.set_params(knn=knn, decay=decay, t=t, n_jobs=n_jobs)
            data_phate = pd.DataFrame(phate_op.fit_transform(tab_norm),
                                      columns=['PHATE1', 'PHATE2'])
            data_phate['knn'] = knn
            data_phate['decay'] = decay
            data_phate['t'] = t
            data_phate['sample_name'] = tab_norm.index.tolist()
            data_phates.append(data_phate)
    elif decays:
        for decay in decays:
            print('++++ %s :: %s ++++' % (knn, decay))
            phate_op.set_params(knn=knn, decay=decay, n_jobs=n_jobs)
            data_phate = pd.DataFrame(phate_op.fit_transform(tab_norm),
                                      columns=['PHATE1', 'PHATE2'])
            data_phate['knn'] = knn
            data_phate['decay'] = decay
            data_phate['sample_name'] = tab_norm.index.tolist()
            data_phates.append(data_phate)
    elif ts:
        for t in ts:
            print('++++ %s :: %s ++++' % (knn, t))
            phate_op.set_params(knn=knn, t=t, n_jobs=n_jobs)
            data_phate = pd.DataFrame(phate_op.fit_transform(tab_norm),
                                      columns=['PHATE1', 'PHATE2'])
            data_phate['knn'] = knn
            data_phate['t'] = t
            data_phate['sample_name'] = tab_norm.index.tolist()
            data_phates.append(data_phate)
    else:
        print('++++ %s ++++' % knn)
        phate_op.set_params(knn=knn, n_jobs=n_jobs)
        data_phate = pd.DataFrame(phate_op.fit_transform(tab_norm),
                                  columns=['PHATE1', 'PHATE2'])
        data_phate['knn'] = knn
        data_phate['sample_name'] = tab_norm.index.tolist()
        data_phates.append(data_phate)
    pd.concat(data_phates).to_csv(fpo, index=False, sep='\t')


def make_figure(i_table, figo, full_pds, ts, ts_step, decays, decays_step, knns, knns_step):

    slider_knns = alt.binding_range(min=min(knns), max=max(knns), step=knns_step, name='knn')
    selector_knns = alt.selection_single(name="knn", fields=['knn'],
                                         bind=slider_knns, init={'knn': min(knns)})
    if decays_step:
        slider_decays = alt.binding_range(min=min(decays), max=max(decays), step=decays_step, name='decay')
    else:
        slider_decays = alt.binding_range(min=min(decays), max=max(decays), step=1, name='decay')
    selector_decays = alt.selection_single(name="decay", fields=['decay'],
                                           bind=slider_decays, init={'decay': min(decays)})
    print(full_pds)
    if ts_step and 'variable' in full_pds.columns:
        slider_ts = alt.binding_range(min=min(ts), max=max(ts), step=ts_step, name='t:')
        selector_ts = alt.selection_single(name="t", fields=['t'],
                                           bind=slider_ts, init={'t': min(ts)})

        variable_dropdown = alt.binding_select(options=full_pds['variable'].unique(), name='variable:')
        variable_select = alt.selection_single(fields=['variable'], bind=variable_dropdown, name="variable")

        circ = alt.Chart(full_pds).mark_point(size=8).encode(
            x='PHATE1:Q',
            y='PHATE2:Q',
            color='variable:N'
        ).add_selection(
            selector_knns, selector_decays, selector_ts, variable_select
        ).transform_filter(
            selector_knns
        ).transform_filter(
            selector_decays
        ).transform_filter(
            selector_ts
        ).transform_filter(
            variable_select
        )

    elif ts_step:
        slider_ts = alt.binding_range(min=min(ts), max=max(ts), step=ts_step, name='t:')
        selector_ts = alt.selection_single(name="cutoff3", fields=['cutoff3'],
                                           bind=slider_ts, init={'cutoff3': min(ts)})

        circ = alt.Chart(full_pds).mark_point(size=8).encode(
            x='PHATE1:Q',
            y='PHATE2:Q',
        ).add_selection(
            selector_knns, selector_decays, selector_ts
        ).transform_filter(
            selector_knns
        ).transform_filter(
            selector_decays
        ).transform_filter(
            selector_ts
        )

    elif 'variable' in full_pds.columns:
        print('fff')
        variable_dropdown = alt.binding_select(options=full_pds['variable'].unique(), name='variable:')
        variable_select = alt.selection_single(fields=['variable'], bind=variable_dropdown, name="variable")

        circ = alt.Chart(full_pds).mark_point(size=8).encode(
            x='PHATE1:Q',
            y='PHATE2:Q',
            color='factor:N'
        ).add_selection(
            selector_knns, selector_decays, variable_select
        ).transform_filter(
            selector_knns
        ).transform_filter(
            selector_decays
        ).transform_filter(
            variable_select
        )

    else:

        circ = alt.Chart(full_pds).mark_point(size=8).encode(
            x='PHATE1:Q',
            y='PHATE2:Q',
        ).add_selection(
            selector_knns, selector_decays
        ).transform_filter(
            selector_knns
        ).transform_filter(
            selector_decays
        )

    circ.resolve_legend(
        color="independent",
        size="independent"
    ).properties(
        width=400,
        height=400,
        title={
            "text": 'PHATE',
            "subtitle": ([i_table] + ["(based on altair)"]),
            "color": "black",
            "subtitleColor": "grey"
        }
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


def xphate(
        i_table: str,
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

    if verbose:
        print('Table dimension:', tab.shape)
        print('normalize')

    tab_norm = pd.DataFrame(normalize(tab, norm='l1', axis=0),
                            index=tab.index,
                            columns=tab.columns).T
    jobs = []
    fpos = []

    if len(p_ts) == 3:
        ts_step = p_ts[-1]
        ts = range(p_ts[0], p_ts[1], ts_step)
    else:
        ts_step = None
        ts = None

    if len(p_decays) == 3:
        decays_step = p_decays[-1]
        decays = range(p_decays[0], p_decays[1], decays_step)
    else:
        decays_step = None
        decays = [15]

    if len(p_knns) == 3:
        knns_step = p_knns[-1]
        knns = range(p_knns[0], p_knns[1], knns_step)
    else:
        knns_step = 5
        knns = range(5, 21, knns_step)

    for knn in knns:
        fpo = '%s/phate_knn%s_multi_params.tsv' % (o_dir_path, knn)
        fpos.append(fpo)
        p = mp.Process(
            target=run_phate,
            args=(fpo, tab_norm, knn, decays, ts, p_jobs,)
        )
        jobs.append(p)
        p.start()

    for j in jobs:
        j.join()

    full_pds = pd.concat([pd.read_csv(x, header=0, sep='\t') for x in fpos])
    fpo = '%s/phate_knn_multi_params.tsv' % o_dir_path
    full_pds.to_csv(fpo, index=False, sep='\t')

    metadata = pd.DataFrame()
    columns = []
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
    make_figure(i_table, figo, full_pds, ts, ts_step, decays, decays_step, knns, knns_step)
