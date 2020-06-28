# datasette-init

[![PyPI](https://img.shields.io/pypi/v/datasette-init.svg)](https://pypi.org/project/datasette-init/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-init?label=changelog)](https://github.com/simonw/datasette-init/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-init/blob/master/LICENSE)

Ensure specific tables and views exist on startup

## Installation

Install this plugin in the same environment as Datasette.

    $ pip install datasette-init

## Usage

This plugin is configured using `metadata.json` (or `metadata.yaml`). Add a block like this that specifies the tables you would like to ensure exist:

```json
{
  "plugins": {
    "datasette-init": {
      "my_database": {
        "tables": {
          "dogs": {
            "columns": {
              "id": "integer",
              "name": "text",
              "age": "integer",
              "weight": "float",
            },
            "pk": "id"
          }
        }
      }
    }
  }
}
```

Any tables that do not create will be created when Datasette first starts.

Valid column types are `"integer"`, `"text"`, `"float"` and `"blob"`. The `"pk"` is optional.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-init
    python3 -mvenv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and tests:

    pip install -e '.[test]'

To run the tests:

    pytest
