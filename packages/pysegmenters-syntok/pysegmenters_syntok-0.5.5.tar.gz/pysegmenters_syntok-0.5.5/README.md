# pysegmenters_syntok

[![license](https://img.shields.io/github/license/oterrier/pysegmenters_syntok)](https://github.com/oterrier/pysegmenters_syntok/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pysegmenters_syntok/workflows/tests/badge.svg)](https://github.com/oterrier/pysegmenters_syntok/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pysegmenters_syntok)](https://codecov.io/gh/oterrier/pysegmenters_syntok)
[![docs](https://img.shields.io/readthedocs/pysegmenters_syntok)](https://pysegmenters_syntok.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pysegmenters_syntok)](https://pypi.org/project/pysegmenters_syntok/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pysegmenters_syntok)](https://pypi.org/project/pysegmenters_syntok/)

Rule based segmenter based on Spacy

## Installation

You can simply `pip install pysegmenters_syntok`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pysegmenters_syntok
```

### Running the test suite

You can run the full test suite against all supported versions of Python (3.8) with:

```
tox
```

### Building the documentation

You can build the HTML documentation with:

```
tox -e docs
```

The built documentation is available at `docs/_build/index.html.
