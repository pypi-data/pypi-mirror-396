# Lima2 Client

![pypi badge](https://badge.fury.io/py/lima2.client.svg?icon=si%3Apython)
![pipeline badge](https://gitlab.esrf.fr/limagroup/lima2-client/badges/main/pipeline.svg)
![coverage badge](https://gitlab.esrf.fr/limagroup/lima2-client/badges/main/coverage.svg?min_good=90&min_acceptable=80&min_medium=75)

This repo contains source code for the Lima2 Conductor, an orchestration module
for the Lima2 acquisition system, and its python client library, the
`lima2.client` package.

Install the lima2-client package:

```sh
pip install lima2-client
```

## Quickstart

A minimal setup for running Lima2 requires:

- The [`lima2`](https://anaconda.org/esrf-bcu/lima2) conda package
- The [`lima2-client`](https://pypi.org/project/lima2-client/) python package
- A tango server, e.g. [`nosqltangodb`](https://pypi.org/project/nosqltangodb/)

> **_NOTE:_** In a bliss environment, the tango server comes with `bliss-demo-servers`,
> so `nosqltangodb` is not required.

Install everything into a new conda environment:

```sh
conda create -n lima2 "python==3.10"
conda activate lima2
conda install -c esrf-bcu lima2
pip install lima2-client[conductor,shell] nosqltangodb
```

The first step is to start the tango server. For `nosqltangodb`, example config
files can be found in the repo's
[`tests/integration/tango_db/`](https://gitlab.esrf.fr/limagroup/lima2-client/-/tree/main/tests/integration/tango_db)
directory. Fetch it into the current directory with:

```sh
wget -qO- https://gitlab.esrf.fr/limagroup/lima2-client/-/archive/main/lima2-client-main.tar.gz?path=tests/integration/tango_db | tar -xz --strip-components=1
```

Start the tango server:

```sh
NosqlTangoDB --port 10000 --db_access yaml:tests/integration/tango_db/ 2
```

Start the Lima2 devices (one control, two receivers):

```sh
export TANGO_HOST="localhost:10000"
mpiexec -n 1 lima2_tango simulator_ctl : \
        -n 1 lima2_tango simulator_rcv1 : \
        -n 1 lima2_tango simulator_rcv2
```

Start the Lima2 Conductor, which listens on port 58712 by default:

```sh
lima2-conductor start \
                localhost:10000 \
                round_robin \
                id00/limacontrol/simulator \
                id00/limareceiver/simulator1 \
                id00/limareceiver/simulator2
```

With all parts online, a client can now make requests to the conductor to
interact with the acquisition system.

The quickest way to start is inside the interactive session (requires the
`lima2-client[shell]` extra dependencies):

```sh
lima2-shell
```

```py
In [1]: run_acquisition(nb_frames=120, expo_time=0.02)  # Should take 2.4 seconds
In [2]: pipeline.progress()
Out[2]: 120
```

In the shell, the entire API of the conductor is exposed via the following
namespaces:

- `acquisition`: direct commands (prepare, start, stop, reset), system state and
  progress
- `detector`: detector information, commands, capabilities and real-time status
- `pipeline`: data access (reduced data streams, frames) and detailed processing
  progress

For more details, the [lima2-shell doc](https://limagroup.gitlab-pages.esrf.fr/lima2-client/shell/) and the
[API reference](https://limagroup.gitlab-pages.esrf.fr/lima2-client/reference/)
should be useful.

## Description

This repo is organized as follows:

```sh
lima2-client
├── conda          # Conda build configuration
├── docs           # Documentation sources
├── scripts        # Auxiliary scripts
├── src/lima2
│   ├── client     # Conductor client-side library
│   ├── conductor  # Conductor server code
│   └── common     # Shared definitions
└── tests
    ├── integration
    └── unit
        ├── client
        ├── conductor
        └── common
```

The project is composed of three main python packages.

### `lima2.client`

The conductor's client-side library, meant to be imported from a control
application or a data consumer. In this package, the conductor webapp's API
endpoints are wrapped into python functions. The docs contain a complete [API
reference](https://limagroup.gitlab-pages.esrf.fr/lima2-client/reference/).

### `lima2.conductor`

Implements the [Lima2
Conductor](https://limagroup.gitlab-pages.esrf.fr/lima2-client/dev/conductor_requirements/),
the orchestration process for distributed acquisitions.

Its central class is the
[`AcquisitionSystem`](https://limagroup.gitlab-pages.esrf.fr/lima2-client/dev/conductor_design/#acquisition-system),
which encapsulates the Lima2 acquisition, detector and processing systems.

This package also contains the `lima2.conductor.webservice` subpackage: the
conductor web server, which provides HTTP endpoints to interact with the
conductor remotely.

### `lima2.common`

Contains type definitions and utilities meant to be imported from
`lima2.client`, `lima2.conductor`, and directly from client apps.

## Development environment

The `dev` optional dependencies contains tools necessary for development and testing.

### uv

Install all dependencies into a local venv:

```sh
uv sync --extra dev
```

Commands can be run with `uv run`:

```sh
uv run lima2-conductor --help
uv run lima2-shell --help
```

> **_NOTE:_** lima2-conductor has a `dev` command, which enables live code reloading
> on save.

### conda

Create a new conda environment with python > 3.9:

```sh
conda create -n lima2-client "python==3.10"
conda activate lima2-client
pip install -e .[dev]
```

Execute commands directly:

```sh
lima2-conductor --help
lima2-shell --help
```

## Tests

Unit and integration tests can be run locally. All dependencies for unit tests should be in the optional `dev` dependencies, and the `pyproject.toml` defines common `pytest` parameters.

After setting up your [dev environment](#development-environment), run the unit tests (prepend `uv run` if using uv):

```sh
pytest tests/unit
# Compute coverage and output the coverage report to htmlcov/
pytest --cov lima2.client --cov lima2.conductor --cov-report html tests/unit/
```

Integration tests require the Lima2 server, available via conda (see [install with conda](#conda)):

```sh
conda activate lima2-client
conda install -c esrf-bcu lima2
pytest tests/integration
```

## Documentation

The repo's [pages](https://limagroup.gitlab-pages.esrf.fr/lima2-client/) contain
user guides, an API reference and design docs. Source files used to build the
documentation are located in the `docs/` directory.

The docs are written in markdown and rendered by
[`mkdocs`](https://www.mkdocs.org/).

### Build the docs (uv)

```sh
uv sync --extra docs
uv run mkdocs serve  # Start the dev server at localhost:8000
uv run mkdocs build  # Render HTML pages to ./site/
```

### Build the docs (conda/pip)

```sh
pip install .[docs]
mkdocs serve  # Start the dev server at localhost:8000
mkdocs build  # Render HTML pages to ./site/
```
