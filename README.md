# Xphate

An interactive vizualization to explore different parameters to [PHATE](https://phate.readthedocs.io/en/stable/index.html)

## Installation

```
pip install -U git+https://github.com/FranckLejzerowicz/Xphate.git
```
#### Requisites

* python >= 3.6
* [PHATE](https://phate.readthedocs.io/en/stable/index.html) (python implentation)

## Input
    

## Outputs



## Example


## Visualization



### Optional arguments

```
  -i, --i-table TEXT              Features table, input path.
  -j, --i-res TEXT                Table to make figure from.
  -o, --o-html TEXT               Visualization html, output path.  [required]
  -m, --m-metadata TEXT           Sample metadata table.
  -l, --p-labels TEXT             Sample metadata column(s) to use for
                                  labeling.

  -c, --p-column TEXT             Column from metadata `-m` to use for
                                  filtering based on values of `-v`.

  -v, --p-column-value TEXT       Filtering value to select samples based on
                                  column passed to `-c`.

  -q, --p-column-quant INTEGER    Filtering quantile / percentile for samples
                                  based on column passed to `-c` (must be
                                  between 0 and 100).

  -fp, --p-filter-prevalence FLOAT
                                  Filter features based on their minimum
                                  sample prevalence (number >1 for sample
                                  counts: <1 for samples fraction).

  -fa, --p-filter-abundance FLOAT
                                  Filter features based on their minimum
                                  sample abundance (number >1 for abundance
                                  counts: <1 for abundance fraction).

  -f, --p-filter-order [meta-filter|filter-meta]
                                  Order to apply the filters: 'filter-meta'
                                  first the prevalence/abundance and then
                                  based on variable; 'meta-filter' first based
                                  on variable and then the
                                  prevalence/abundance on the remaining.
                                  [default: meta-filter]

  -t, --p-ts INTEGER              Min, Max and Step for the `t` parameter.
  -d, --p-decays INTEGER          Min, Max and Step for the `decay` parameter.
  -k, --p-knns INTEGER            Min, Max and Step for the `knns` parameter.
  -n, --p-cpus INTEGER            Number of jobs.
  --verbose / --no-verbose
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```

### Bug Reports

contact `flejzerowicz@health.ucsd.edu`