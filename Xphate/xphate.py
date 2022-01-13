# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the MIT License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import sys
import pandas as pd
from os.path import abspath, dirname, isfile, isdir, splitext

import multiprocessing as mp
from sklearn.preprocessing import normalize

from Xphate.filter import do_filter
from Xphate.utils import get_metadata, get_param
from Xphate.phate import run_phate
from Xphate.altair import make_figure


def xphate(
        i_table: str,
        i_res: str,
        o_html: str,
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
        clusters: bool = False,
        separate: bool = False,
        make_3d: bool = True,
        verbose: bool = False
    ):

    if verbose:
        verbose = 1
    else:
        verbose = 0

    suffix = ''
    ts_step, ts = get_param(p_ts, 't', suffix)
    decays_step, decays = get_param(p_decays, 'd', suffix)
    knns_step, knns = get_param(p_knns, 'k', suffix)

    if i_res:
        print('i_res', i_res)
        full_pds = pd.read_csv(i_res, header=0, sep='\t', dtype={'sample_name': str})
    else:
        i_table = abspath(i_table)
        if not isfile(i_table):
            raise IOError("No input table found at %s" % i_table)
        if verbose:
            print('read')
        tab = pd.read_csv(i_table, header=0, index_col=0, sep='\t')

        o_html = abspath(o_html)
        if not o_html.endswith('.html'):
            o_html = '%s%s.html' % (o_html, suffix)
        if not isdir(dirname(o_html)):
            os.makedirs(dirname(o_html))

        message = 'input'
        if m_metadata and p_column and p_column_value or p_filter_prevalence or p_filter_abundance:
            # Filter / Transform OTU-table
            tab = do_filter(tab, m_metadata, p_filter_prevalence,
                            p_filter_abundance, p_filter_order,
                            p_column, p_column_value, p_column_quant)
            message = 'filtered'

        o_few = '%s/TOO_FEW.%sf.skip' % (dirname(o_html), tab.shape[0])
        if tab.shape[0] < 10:
            print('Too few features to perform PHATE (%s features)' % tab.shape[0])
            with open(o_few, 'w'):
                pass
            sys.exit(0)

        tab_norm = pd.DataFrame(
            normalize(tab, norm='l1', axis=0),
            index=tab.index, columns=tab.columns).T
        o_few = '%s/TOO_FEW.%ss.skip' % (dirname(o_html), tab_norm.columns.size)
        if isfile(o_few) or tab_norm.columns.size <= 50:
            print('Too few samples to perform PHATE (%s samples)' % tab_norm.columns.size)
            with open(o_few, 'w'):
                pass
            sys.exit(0)

        jobs, fpos, fpos_3d = [], [], []
        for knn in knns:
            fpo = '%s_tmp-%s.tsv' % (splitext(o_html)[0], knn)
            fpos.append(fpo)
            fpo_3d = '%s_tmp-%s_3d.tsv' % (splitext(o_html)[0], knn)
            fpos_3d.append(fpo_3d)
            p = mp.Process(
                target=run_phate,
                args=(fpo, fpo_3d, tab_norm, knn, decays,
                      ts, p_jobs, make_3d, verbose,))
            jobs.append(p)
            p.start()
        for j in jobs:
            j.join()

        full_pds = pd.concat([pd.read_csv(
            x, header=0, sep='\t', dtype={'sample_name': str}) for x in fpos])
        full_pds = full_pds.set_index(
            [x for x in full_pds.columns if 'cluster' not in x]
        ).stack().reset_index().rename(
            columns={'level_6': 'variable', 0: 'factor'})
        fpo = '%s_xphate.tsv' % splitext(o_html)[0]
        full_pds.to_csv(fpo, index=False, sep='\t')
        for i in fpos:
            os.remove(i)

        if make_3d:
            full_pds_3d = pd.concat([pd.read_csv(
                x, header=0, sep='\t', dtype={'sample_name': str}) for x in
                fpos_3d])
            fpo_3d = '%s_xphate_3d.tsv' % splitext(o_html)[0]
            full_pds_3d.to_csv(fpo_3d, index=False, sep='\t')

    metadata, columns = pd.DataFrame(), []
    if m_metadata:
        if verbose:
            print('Read metadata...', end='')
        metadata, columns = get_metadata(m_metadata, p_columns)
        if verbose:
            print('done.')

    if metadata.shape[0] and len(columns):
        if verbose:
            print('Merge metadata...', end='')
        metadata = metadata[
            (['sample_name'] + columns)
        ].set_index(
            'sample_name')
        dtypes = {'NA': 'avoid'}
        for col in columns:
            dt = str(metadata[col].dtype)
            if dt == 'object':
                dtype = 'categorical'
            else:
                dtype = 'numerical'
            dtypes[col] = dtype
        metadata = metadata.stack().reset_index().rename(
            columns={'level_1': 'variable', 0: 'factor'})
        full_pds_meta = full_pds.drop(
            columns=['variable', 'factor']
        ).merge(
            metadata, on='sample_name', how='left'
        ).fillna('NA')
        full_pds_meta['dtype'] = [dtypes[var] for var in full_pds_meta.variable]

        if verbose:
            print('done.')
        full_pds['dtype'] = 'categorical'
        full_pds = pd.concat([full_pds, full_pds_meta], sort=False)

    make_figure(i_table, i_res, o_html, full_pds, ts,
                ts_step, decays, decays_step, knns, knns_step,
                clusters, separate)
