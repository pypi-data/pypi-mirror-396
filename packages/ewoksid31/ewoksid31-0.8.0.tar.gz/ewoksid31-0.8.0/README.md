# ewoksid31

Data processing workflows for ID31.

## Getting started

Install requirements

```bash
pip install ewoksid31
```

## Documentation

- General documentation: [ewoksid31.readthedocs.io](https://ewoksid31.readthedocs.io/)
- GUI usage and reprocessing details: [Confluence - GUI for reprocessing XRPD data](https://confluence.esrf.fr/display/ID31KB/GUI+for+reprocessing+XRPD+data)
- [General contribution guide](https://gitlab.esrf.fr/dau/ci/pyci/-/blob/main/CONTRIBUTING.md)

## Reference environment

The ``requirements-lock.txt`` defines a set of Python packages with pinned versions required to run the ewoks worker and the reprocessing tools.
It does not include the ``ewoksid31`` package.

To create a conda environment with this reference set of packages, run:

```bash
conda create -n ewoksid31-env "python=3.12"
conda activate ewoksid31-env
python -m pip install -r requirements-lock.txt
pip install -e .
```
