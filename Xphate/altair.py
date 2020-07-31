# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the MIT License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import altair as alt


def make_figure(i_table, i_res, o_html, full_pds, ts, ts_step,
                decays, decays_step, knns, knns_step):

    print(full_pds['variable'].unique())

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

    circ.save(o_html)
    print('-> Written:', o_html)
