# Scientiflow

## Setting the ENV variables

```
# When developing on Windows, run:
$env:API_BASE="SCIENTIFLOW_BACKEND_URL"     # Set the base URL of the Scientiflow backend
$env:AUTH_TOKEN="SOME_AUTH_TOKEN"           # Set the AUTH token that you get after logging in
$env:SCFLOW_DEBUG=1                         # Run in debug mode, using some dummy data

# on Linux, run:
export API_BASE="SCIENTIFLOW_BACKEND_URL"   # Set the base URL of the Scientiflow backend
export AUTH_TOKEN="SOME_AUTH_TOKEN"         # Set the AUTH token that you get after logging in
export SCFLOW_DEBUG=1                       # Run in debug mode, using some dummy data
```

## Building and installing the python package

```bash
poetry build
pip install dist/scientiflow_cli-0.1.0-py3-none-any.whl --force-reinstall

# Now you can run it as:
python -m scientiflow_cli --help
```

> Note: The `--force-reinstall` flag is used as a sage-guard, in case an already exising version of the package is installed.

## For the devs

> Note
> If you need to add a dependency, which this project depends on, use the command `poetry add` instead of doing a pip install. This will ensure that the `pyproject.toml` file is updated with the new dependency, and all the other devs have the same dependencies and dependencies versions.

```bash
# Activate a poetry shell, and install dependencies
poetry shell

# Install the dependencies if it's your first time working on the project, using:
# poetry install
```

```bash
# In order to run the package without building, you can do:
poetry run python -m scientiflow_cli.main --help
```
