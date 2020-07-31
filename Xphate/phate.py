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
    data_phates = []
    if not knn:
        knn = 5
    for (decay, t) in itertools.product(*[decays, ts]):
        if not decay:
            decay = 15
        if not t:
            t = 'auto'
        phate_op = phate.PHATE()
        phate_op.set_params(knn=knn, decay=decay, t=t, n_jobs=n_jobs, verbose=verbose)
        phate_fit = phate_op.fit_transform(tab_norm)
        phate_clusters = phate.cluster.kmeans(phate_op, max_clusters=30)
        data_phate = pd.DataFrame(phate_fit, columns=['PHATE1', 'PHATE2'])
        data_phate['knn'] = knn
        data_phate['decay'] = decay
        data_phate['t'] = t
        data_phate['cluster'] = phate_clusters
        data_phate['sample_name'] = tab_norm.index.tolist()
        data_phates.append(data_phate)
    pd.concat(data_phates).to_csv(fpo, index=False, sep='\t')
