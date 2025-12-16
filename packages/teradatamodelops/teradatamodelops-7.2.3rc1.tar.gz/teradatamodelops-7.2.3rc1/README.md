# Teradata ModelOps Python Client
[![Build Status](https://github.com/Teradata-PE/avmo-ModelOpsPythonSDK/actions/workflows/python_test.yml/badge.svg)](https://github.com/Teradata-PE/avmo-ModelOpsPythonSDK/actions/workflows/python_test.yml)
[![Coverage](https://sonarqube.labsteradata.net/api/project_badges/measure?project=avmo-ModelOpsPythonSDK&metric=coverage&token=sqb_c33f9ec757640efbdf4593cd3d91677c5c2504c0)](https://sonarqube.td.teradata.com/dashboard?id=avmo-ModelOpsPythonSDK)
[![Quality Gate Status](https://sonarqube.labsteradata.net/api/project_badges/measure?project=avmo-ModelOpsPythonSDK&metric=alert_status&token=sqb_c33f9ec757640efbdf4593cd3d91677c5c2504c0)](https://sonarqube.td.teradata.com/dashboard?id=avmo-ModelOpsPythonSDK)
![PyPI](https://img.shields.io/pypi/v/teradatamodelops)

Python client for Teradata ModelOps. It is composed of both a client API implementation to access the ModelOps backend APIs and a command line interface (cli) tool which can be used for many common tasks. 


## Requirements

Python >= 3.10


## Usage

See the pypi [guide](./docs/pypi.md) for some usage notes. 


## Installation

To install the latest release, just do

```bash
pip install teradatamodelops
```

To build from source, it is advisable to create a Python venv or a Conda environment 

Python venv:
```bash
python -m venv tmo_python_env
source tmo_python_env/bin/activate
```

Install library from local folder using pip:

```bash
pip install . --use-feature=in-tree-build
```

Install library from package file

```bash
# first install required dependencies for building
python -m pip install --user --upgrade setuptools wheel "twine>=5.1.0" build

# then create the package
python -m build

# and install using pip
pip install dist/*.whl
```

## Development

To install the development version, clone the repository and run:

```bash
pip install -e .
```

## Code Style

```bash
pip install -r dev_requirements.txt
python -m black tmo/* aoa/* tests/* tmo/examples/*.ipynb -t py310 -t py311 -t py312 -t py313
```

## Testing

```bash
pip install -r dev_requirements.txt
python -m pytest
```

For local tests make sure you have `VMO_CONN_*` and `VMO_API_*` env variables defined:
```bash
export VMO_CONN_HOST=10.27.160.139
export VMO_CONN_USERNAME=td_modelops
export VMO_CONN_PASSWORD=*****
export VMO_URL=https://vmo.local/core
export VMO_API_AUTH_MODE=client_credentials
export VMO_API_AUTH_CLIENT_ID=modelops-cli
export VMO_API_AUTH_CLIENT_SECRET=******
export VMO_SSL_VERIFY=false
```

To run selected tests use `-k` parameter:
```bash
python -m pytest -k "test_train"
```

### Generate Licenses

We have added ability to generate third party licenses file. First install the required package `pip install third-party-license-file-generator`. Pin all dependencies in requirements to a specific version or it won't work. Then run the following to generate the file:

```shell
python -m third_party_license_file_generator -c \
    -r requirements.txt \
    -p $(which python3) \
    -o LICENSE-3RD-PARTY.txt
```

Finally, restore the original requirements file, and the file `LICENSE-3RD-PARTY.txt` will be generated and can be found at the root folder.

## Building and releasing 

Assuming PyPi credentials are configured in  `~/.pypirc`
```bash
python -m pip install --user --upgrade setuptools wheel "twine>=5.1.0" build

rm -rf dist/ 

python -m build

twine upload dist/*
```

---

_Copyright 2025 Teradata. All Rights Reserved._
