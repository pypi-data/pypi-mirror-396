import subprocess
import typer

app = typer.Typer()


@app.command()
def create(name):
    """Create a pyproject.toml for your package,
    Example:
    `python3 -m create create <project_name>` (project_name is required)
    """
    with open("pyproject.toml", "w") as file:
        file.write("[project]\nname = " + f'"{name}"')
@app.command()
def build():
    """Build the `pip` package easily using `twine`, but don't worry! It skips existing builds.
    Example:

    `python3 -m create build`
    """
    subprocess.run(["python -m build"], shell=True)


@app.command("version")
def version(version):
    """Create a new version!

    Example:

    `python3 -m create version <your_description>`
"""
    with open("pyproject.toml", "a") as file:
        file.write("\nversion = " + f'"{version}"')


@app.command()
def description(description):
    """
    Describe your project.
    """
    with open("pyproject.toml", "a") as file:
        file.write("\ndescription = " + f'"{description}"')


@app.command()
def upload():
    """Upload a project to PyPI (Requires API key)"""
    subprocess.run(["twine upload --skip-existing ./dist/*"], shell=True)

if __name__ == "__main__":
    app()
