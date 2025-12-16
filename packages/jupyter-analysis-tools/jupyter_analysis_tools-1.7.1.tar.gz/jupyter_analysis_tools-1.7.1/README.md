# Jupyter Analysis Tools (v1.7.1)

[![PyPI Package latest release](https://img.shields.io/pypi/v/jupyter-analysis-tools.svg)](https://pypi.org/project/jupyter-analysis-tools)
[![Commits since latest release](https://img.shields.io/github/commits-since/BAMresearch/jupyter-analysis-tools/v1.7.1.svg)](https://github.com/BAMresearch/jupyter-analysis-tools/compare/v1.7.1...main)
[![License](https://img.shields.io/pypi/l/jupyter-analysis-tools.svg)](https://en.wikipedia.org/wiki/MIT_license)
[![Supported versions](https://img.shields.io/pypi/pyversions/jupyter-analysis-tools.svg)](https://pypi.org/project/jupyter-analysis-tools)
[![PyPI Wheel](https://img.shields.io/pypi/wheel/jupyter-analysis-tools.svg)](https://pypi.org/project/jupyter-analysis-tools#files)
[![Weekly PyPI downloads](https://img.shields.io/pypi/dw/jupyter-analysis-tools.svg)](https://pypi.org/project/jupyter-analysis-tools/)
[![Continuous Integration and Deployment Status](https://github.com/BAMresearch/jupyter-analysis-tools/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/BAMresearch/jupyter-analysis-tools/actions/workflows/ci-cd.yml)
[![Coverage report](https://img.shields.io/endpoint?url=https://BAMresearch.github.io/jupyter-analysis-tools/coverage-report/cov.json)](https://BAMresearch.github.io/jupyter-analysis-tools/coverage-report/)

Yet another Python library with helpers and utilities for data analysis and processing.

## Installation

    pip install jupyter-analysis-tools

You can also install the in-development version with:

    pip install git+https://github.com/BAMresearch/jupyter-analysis-tools.git@main

## Documentation

https://BAMresearch.github.io/jupyter-analysis-tools

## Development

### Testing

See which tests are available (arguments after `--` get passed to *pytest* which runs the tests):

    tox -e py -- --co

Run a specific test only:

    tox -e py -- -k <test_name from listing before>

Run all tests with:

    tox -e py

### Package Version

Get the next version number and how the GIT history would be interpreted for that:

    pip install python-semantic-release
    semantic-release -v version --print

This prints its interpretation of the commits in detail. Make sure to supply the `--print`
argument to not raise the version number which is done automatically by the *release* job
of the GitHub Action Workflows.

### Project template

Update the project configuration from the *copier* template and make sure the required packages
are installed:

    pip install copier jinja2-time
    copier update --trust --skip-answered
