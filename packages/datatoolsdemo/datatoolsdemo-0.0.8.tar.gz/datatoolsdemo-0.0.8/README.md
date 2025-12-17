[![Coverage Status](https://coveralls.io/repos/github/Jyppara/python-dependabot-demo/badge.svg?branch=feature/add-coveralls)](https://coveralls.io/github/Jyppara/python-dependabot-demo?branch=feature/add-coveralls)
[![PyPI](https://img.shields.io/pypi/v/datatoolsdemo)](https://pypi.org/project/datatoolsdemo/)

# python-dependabot-demo

This repository is a lightweight practice project for experimenting with a  Python development workflow.
The goal is to demonstrate how dependency management, automated releases, and CI pipelines work together in a realistic setup.

The project includes:

- A Python package (AI-generated code: simple data utilities + tests)
- Poetry for dependency management and packaging
- Dependabot for automatic dependency update pull requests
- A CI pipeline (GitHub Actions) that:
    - runs tests on every branch
    - builds and publishes the package to PyPI when changes are merged into main
- Automatic version tagging and GitHub Releases on every successful publish
- A fully working PyPI release flow

All source code and tests were generated using AI to serve as a clean and minimal example of how to structure a Python package with automated tooling.
