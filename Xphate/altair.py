# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the MIT License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import altair as alt


def make_subplot(circ, select, tooltip, dtype):
    if dtype == 'N':
        title = 'Categorical variables'
    elif dtype == 'Q':
        title = 'Numerical variables'
    tooltip.extend(['variable', 'factor'])
    circ_dtype = circ.encode(
        color='factor:%s' % dtype,
        tooltip=tooltip
    ).add_selection(
        select
    ).transform_filter(
        select
    ).properties(
        title=title
    )
    return circ_dtype


def make_figure(i_table, i_res, o_html, full_pds, ts, ts_step,
                decays, decays_step, knns, knns_step):

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
            min=min(knns),
            max=max(knns),
            step=knns_step,
            name='knn'
        )
        selector_knns = alt.selection_single(
            name="knn",
            fields=['knn'],
            bind=slider_knns,
            init={'knn': min(knns)}
        )
        tooltip.append('knn')
        circ = circ.add_selection(
            selector_knns
        ).transform_filter(
            selector_knns
        )
        subtext.append('knn ("k") = %s\n' % ', '.join(map(str, knns)))

    if decays_step:
        slider_decays = alt.binding_range(
            min=min(decays),
            max=max(decays),
            step=decays_step,
            name='decay'
        )
        selector_decays = alt.selection_single(
            name="decay",
            fields=['decay'],
            bind=slider_decays,
            init={'decay': min(decays)}
        )
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

    has_cats = 0
    has_nums = 0
    if 'variable' in full_pds.columns:

        dtypes_set = set(full_pds['dtype'])
        if 'categorical' in dtypes_set:
            cats = full_pds.loc[full_pds.dtype == 'categorical']
            cats_init = sorted([
                x for x in cats['variable'] if str(x) != 'nan'],
                key=lambda x: -len(x))[0]
            cats_dropdown = alt.binding_select(
                options=cats['variable'].unique(), name='variable:')
            cats_select = alt.selection_single(
                fields=['variable'], bind=cats_dropdown,
                name="categorical variable", init={'variable': cats_init})
            cats_plot = make_subplot(
                circ, cats_select, list(tooltip), 'N')
            has_cats = 1

        if 'numerical' in dtypes_set:
            nums = full_pds.loc[full_pds.dtype == 'numerical']
            cats_init = sorted([
                x for x in nums['variable'] if str(x) != 'nan'],
                key=lambda x: -len(x))[0]
            nums_dropdown = alt.binding_select(
                options=nums['variable'].unique(), name='variable:')
            nums_select = alt.selection_single(
                fields=['variable'], bind=nums_dropdown,
                name="numerical variable", init={'variable': cats_init})
            nums_plot = make_subplot(
                circ, nums_select, list(tooltip), 'Q')
            has_nums = 1

    title = {
        "text": text,
        "color": "black",
    }
    if subtext != ['Parameters:']:
        title.update({
            "subtitle": (subtext + ["(based on altair)"]),
            "subtitleColor": "grey"
        })

    if has_nums and has_cats:
        circ = alt.hconcat(cats_plot, nums_plot)
    elif has_nums:
        circ = nums_plot
    elif has_cats:
        circ = cats_plot

    # circ = circ.resolve_legend(
    #     color="independent",
    #     size="independent"
    # ).properties(
    #     width=400,
    #     height=400,
    #     title=title
    # )
    #
    circ.save(o_html)
    print('-> Written:', o_html)
