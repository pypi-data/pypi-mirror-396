import subprocess
# Build the python project
subprocess.run(["python -m build"])
# Upload to PyPI
subprocess.run(["twine upload --skip-existing ./dist/*"])