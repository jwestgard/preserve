# Development Setup

## Introduction

This page describes how to set up a development environment, and other
information useful for developers to be aware of.

## Prerequisites

The following instructions assume that "pyenv" and "pyenv-virtualenv" are
installed to enable the setup of an isolated Python environment.

See the following for setup instructions:

* <https://github.com/pyenv/pyenv>
* <https://github.com/pyenv/pyenv-virtualenv>

Once "pyenv" and "pyenv-virtualenv" have been installed, install Python 3.7.10:

```
> pyenv install 3.7.10
```

## Installation for development

1) Clone the "preserve" Git repository:

```
> git clone git@github.com:umd-lib/preserve.git
```

2) Switch to the "preserve" directory:

```
> cd preserve
```

3) Set up the virtual environment:

```
> pyenv virtualenv 3.7.10 preserve
> pyenv shell preserve
```

4) Run "pip install", including the "dev" and "test" dependencies:

```
> pip install -e .[dev,test]
```

## Running the tests

To run the tests:

```
> pytest
```

## Code Style

Application code style should generally conform to the guidelines in
[PEP 8](https://www.python.org/dev/peps/pep-0008/). The "pycodestyle" tool
to check compliance with the guidelines can be run using:

```
> pycodestyle .
```
