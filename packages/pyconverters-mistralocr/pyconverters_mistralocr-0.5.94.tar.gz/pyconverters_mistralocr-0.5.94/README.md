# pyconverters_mistralocr

[![license](https://img.shields.io/github/license/oterrier/pyconverters_mistralocr)](https://github.com/oterrier/pyconverters_mistralocr/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyconverters_mistralocr/workflows/tests/badge.svg)](https://github.com/oterrier/pyconverters_mistralocr/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyconverters_mistralocr)](https://codecov.io/gh/oterrier/pyconverters_mistralocr)
[![docs](https://img.shields.io/readthedocs/pyconverters_mistralocr)](https://pyconverters_mistralocr.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyconverters_mistralocr)](https://pypi.org/project/pyconverters_mistralocr/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyconverters_mistralocr)](https://pypi.org/project/pyconverters_mistralocr/)

Convert PDF to structured text using [MistralOCR](https://github.com/kermitt2/mistralocr)

## Installation

You can simply `pip install pyconverters_mistralocr`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyconverters_mistralocr
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
