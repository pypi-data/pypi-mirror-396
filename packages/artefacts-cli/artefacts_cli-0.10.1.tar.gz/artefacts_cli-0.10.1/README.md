# Artefacts CLI

CLI to the Artefacts platform.

[![Documentation](https://img.shields.io/badge/documentation-blue.svg?style=flat-square)](https://docs.artefacts.com/)
[![Ruff Style](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Requirements

* Currently working partially where Python can run.
* Fully working on ROS-compatible and ready environments. Notably need for packages like `ros-<dist>-rclpy` and `ros-<dist>-rosidl-runtime-py`.


## Usage

To install:
```
pip install artefacts-cli
```

Check configuration: After creating `project-name` from the web UI and getting an API key, try:

```
artefacts config add [project-name]
```

and enter you `API_KEY` for the project when prompted.

You can then do

```
artefacts hello [project-name]
```

alternatively, you can specify you API KEY via environment variable

```
ARTEFACTS_KEY=[your-key] artefacts hello [project-name]
```

To run a job locally, for example the turtlesim example (need ros2 installed).
First edit `artefacts.yaml` to change the project name, then:

```
cd examples/turtlesim
artefacts run basic_tests
```


## Configuration file syntax

See [the configuration syntax documentation](docs/configuration-syntax.md)


## User docs

You can serve docs locally using mkdocs:

```
mkdocs serve -a 127.0.0.1:7000
```

The docs are automatically deployed by the documentation workflow.

## Development notes

We use Pyre for static analysis. If it does not work out of the box, please consider adapting the `.pyre_configuration` file included with this repository. One assumption is that developers work in a virtual environment under `./venv`.
