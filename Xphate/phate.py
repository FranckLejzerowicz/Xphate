# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the MIT License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import phate
import itertools


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
