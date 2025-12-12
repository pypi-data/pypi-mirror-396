# pyprocessors_chunk_sentences

[![license](https://img.shields.io/github/license/oterrier/pyprocessors_chunk_sentences)](https://github.com/oterrier/pyprocessors_chunk_sentences/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyprocessors_chunk_sentences/workflows/tests/badge.svg)](https://github.com/oterrier/pyprocessors_chunk_sentences/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyprocessors_chunk_sentences)](https://codecov.io/gh/oterrier/pyprocessors_chunk_sentences)
[![docs](https://img.shields.io/readthedocs/pyprocessors_chunk_sentences)](https://pyprocessors_chunk_sentences.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyprocessors_chunk_sentences)](https://pypi.org/project/pyprocessors_chunk_sentences/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyprocessors_chunk_sentences)](https://pypi.org/project/pyprocessors_chunk_sentences/)

Create segments from annotations

## Installation

You can simply `pip install pyprocessors_chunk_sentences`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyprocessors_chunk_sentences
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
