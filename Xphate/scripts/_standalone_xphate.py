# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the MIT License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import click

from Xphate.xphate import xphate
from Xphate import __version__


@click.command()
@click.option(
    "-i", "--i-table", required=False, type=str,
    help="Features table, input path."
)
@click.option(
    "-j", "--i-res", required=False, type=str,
    help="Table to make figure from."
)
@click.option(
    "-o", "--o-html", required=True, type=str,
    help="Visualization html, output path."
)
@click.option(
    "-m", "--m-metadata", required=False, type=str,
    help="Sample metadata table."
)
@click.option(
    "-l", "--p-labels", required=False, type=str, multiple=True,
    help="Sample metadata column(s) to use for labeling."
)
@click.option(
    "-c", "--p-column", required=False, type=str,
    default=None, help="Column from metadata `-m` to use for "
                       "filtering based on values of `-v`."
)
@click.option(
    "-v", "--p-column-value", required=False, type=str, multiple=True,
    default=None, help="Filtering value to select samples based"
                       " on column passed to `-c`."
)
@click.option(
    "-q", "--p-column-quant", required=False, type=int,
    default=0, help="Filtering quantile / percentile for samples based on"
                    " column passed to `-c` (must be between 0 and 100)."
)
@click.option(
    "-fp", "--p-filter-prevalence", required=False, type=float,
    default=0, help="Filter features based on their minimum sample prevalence "
                    "(number >1 for sample counts: <1 for samples fraction)."
)
@click.option(
    "-fa", "--p-filter-abundance", required=False, type=float,
    default=0, help="Filter features based on their minimum sample abundance "
                    "(number >1 for abundance counts: <1 for abundance fraction)."
)
@click.option(
    "-f", "--p-filter-order", required=False, default='meta-filter',
    type=click.Choice(['meta-filter', 'filter-meta']),
    show_default=True, help="Order to apply the filters: 'filter-meta' first the prevalence/"
                            "abundance and then based on variable; 'meta-filter' first based "
                            "on variable and then the prevalence/abundance on the remaining."
)
@click.option(
    "-t", "--p-ts", required=False, type=int, multiple=True,
    default=None, help="Min, Max and Step for the `t` parameter."
)
@click.option(
    "-d", "--p-decays", required=False, type=int, multiple=True,
    default=None, help="Min, Max and Step for the `decay` parameter."
)
@click.option(
    "-k", "--p-knns", required=False, type=int, multiple=True,
    default=None, help="Min, Max and Step for the `knns` parameter."
)
@click.option(
    "-n", "--p-cpus", required=False, type=int,
    default=1, help="Number of jobs."
)
@click.option(
    "--clusters/--no-clusters", default=False
)
@click.option(
    "--verbose/--no-verbose", default=False
)
@click.version_option(__version__, prog_name="Xphate")
def standalone_xphate(
        i_table,
        i_res,
        o_html,
        m_metadata,
        p_labels,
        p_column,
        p_column_value,
        p_column_quant,
        p_filter_prevalence,
        p_filter_abundance,
        p_filter_order,
        p_ts,
        p_decays,
        p_knns,
        p_cpus,
        clusters,
        verbose
):

    xphate(
        i_table,
        i_res,
        o_html,
        m_metadata,
        p_labels,
        p_column,
        p_column_value,
        p_column_quant,
        p_filter_prevalence,
        p_filter_abundance,
        p_filter_order,
        p_ts,
        p_decays,
        p_knns,
        p_cpus,
        clusters,
        verbose
    )


if __name__ == "__main__":
    standalone_xphate()
