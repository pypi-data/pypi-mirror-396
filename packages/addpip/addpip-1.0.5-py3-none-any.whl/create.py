import subprocess
import typer

app = typer.Typer()


@app.command()
def create(name):
    with open("pyproject.toml", "w") as file:
        file.write("[project]\nname = " + f'"{name}"')
@app.command()
def build():
    subprocess.run(["python -m build"], shell=True)


@app.command("version")
def version(version):
    with open("pyproject.toml", "a") as file:
        file.write("\nversion = " + f'"{version}"')


@app.command()
def description(description):
    with open("pyproject.toml", "a") as file:
        file.write("\ndescription = " + f'"{description}"')


@app.command()
def upload():
    subprocess.run(["twine upload --skip-existing ./dist/*"], shell=True)


if __name__ == "__main__":
    app()
