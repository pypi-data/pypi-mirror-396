# ARTEFACTS Client

Python client and CLI for ARTEFACTS

[![Documentation](https://img.shields.io/badge/documentation-blue.svg?style=flat-square)](https://docs.artefacts.com/)
[![Ruff Style](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


## CLI

To install:
```
pip install --editable "."
```

Check configuration: after creating `project-name` from the web UI and getting an API key, try:

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

## Development

For the CLI dev environment:

```
pip install --editable ".[dev]"

# Or the extended version, with perhaps some goodies like ptw
pip install --editable ".[dev-extended]"
```

You can run the tests with:

```
pytest
```

If you need to change the API url, you can:

* Edit `~/.artefacts/config`, and add `apiurl = http://localhost:5000/api` in the `[DEFAULT]` section
* Using an environment variable, `ARTEFACTS_API_URL=http://localhost:5000/api artefacts hello [project-name]`

You can setup the pre-commit hooks with:
```
pre-commit install --install-hooks
```
This will automatically run the formatter and checker on the files staged for commit whenever you run `git commit`

## Localisation efforts

CLI uses Babel through PyBabel. Please note there is a significant limitation: We cannot use f-strings! We must use the `"this is a {s}".format(s="pen")` notation to get PyBabel to detect localised strings.


### _Note_ when using Docker to Run a Job Locally

When using the client/cli dev environment on your machine, but building and running a job through Docker, e.g
```
docker run --env ARTEFACTS_KEY=<ApiKey> --env ARTEFACTS_JOB_NAME=basic_tests --env ARTEFACTS_API_URL=<yourlocalhostUrl>  <tag>
```
(such as the Dockerfile in the [dolly-demo](https://github.com/art-e-fact/dolly-demo/blob/main/Dockerfile) repo)

You need to point the ARTEFACTS_API_URL back to your host machine which is `host.docker.internal` i.e `ARTEFACTS_API_URL=http://host.docker.internal:5000`

### Testing on Infra

See [here](./internal-docs/testing-on-infra.md)

## Release management

Releases are managed with Twine through the `bin/release` script. By default it releases to TestPyPi. Passing the `production` parameter releases to PyPi. Note the script currently requires a tag being issued (semver) to let a release proceed.

## User docs

You can serve docs locally using mkdocs:

```
mkdocs serve -a 127.0.0.1:7000
```

The docs are automatically deployed by the documentation workflow.
