# newpip

![newpip logo](Python-logo-notext.png)

This library is meant to simplify `pip` package creation.

## API

- `create`: Create a pyproject.toml for your package,

Example:

`python3 -m create create <project_name>` (project_name is required)

- `build`: Build the `pip` package easily using `twine`, but don't worry! It skips existing builds.

Example:

`python3 -m create build`

- `version`: Create a new version!

Example:

`python3 -m create version <your_description>`

- `upload`: Upload a project to PyPI (Requires API key)

- `description`: Describe your project.

## Requirements

You might need to edit information manually via text after you create your project

## Starting website documentation

`firefox path/to/newpip/index.html`

You might want to see where `newpip` is installed,