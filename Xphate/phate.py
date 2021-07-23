# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the MIT License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from os.path import splitext
import pandas as pd
import phate
import itertools


def run_phate(fpo, fpo_3d, tab_norm, knn, decays, ts, n_jobs, make_3d, verbose):
    data_phates = []
    data_phates_3d = []
    if not knn:
        knn = 5
    for (decay, t) in itertools.product(*[decays, ts]):
        if not decay:
            decay = 15
        if not t:
            t = 'auto'
        phate_op = phate.PHATE()
        phate_op.set_params(
            knn=knn, decay=decay, t=t, n_jobs=n_jobs, verbose=verbose)
        phate_fit = phate_op.fit_transform(tab_norm)
        data_phate = pd.DataFrame(phate_fit, columns=['PHATE1', 'PHATE2'])
        data_phate['knn'] = knn
        data_phate['decay'] = decay
        data_phate['t'] = t
        data_phate['sample_name'] = tab_norm.index.tolist()
        for k in range(2, 11):
            phate_clusters = phate.cluster.kmeans(phate_op, n_clusters=k)
            data_phate['cluster_k%s' % k] = phate_clusters
        data_phates.append(data_phate)
        if make_3d:
            phate_op.set_params(n_components=3)
            phate_3d = phate_op.transform()
            data_phate_3d = pd.DataFrame(
                phate_3d, columns=['PHATE1', 'PHATE2', 'PHAT3'])
            data_phate['knn'] = knn
            data_phate['decay'] = decay
            data_phate['t'] = t
            data_phate['sample_name'] = tab_norm.index.tolist()
            data_phates_3d.append(data_phate_3d)

    pd.concat(data_phates).to_csv(fpo, index=False, sep='\t')
    if make_3d:
        pd.concat(data_phates_3d).to_csv(fpo_3d, index=False, sep='\t')
