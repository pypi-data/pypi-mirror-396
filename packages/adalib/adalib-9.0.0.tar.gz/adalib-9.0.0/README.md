# adalib

This repository contains the source code of `adalib`, the Python library to interact with the AdaLab platform.

## Installation

`adalib` can be installed from PyPI or a `devpi` index:

```sh
# PyPI
pip install adalib
# devpi
pip install --extra-index-url <devpi_index_url> adalib
```

In order to add it to the dependencies of a Python project using `poetry` use:

```sh
poetry source add --priority=supplemental <repo_name> <devpi_index_url>
poetry source add --priority=primary PyPI
poetry add --source <repo_name> adalib
```

## Usage

See the [package documentation](https://adalib.adamatics.com/docs/latest/), as well as the [example Notebooks](https://github.com/adamatics/adalib_example_notebooks).

## Contributing

See the [contributor's guide](CONTRIBUTING.md).
