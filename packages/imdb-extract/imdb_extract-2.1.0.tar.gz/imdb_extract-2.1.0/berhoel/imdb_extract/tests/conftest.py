#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Pytest helper for IMDBExtract.
"""

# Standard library imports.
from pathlib import Path

# Third party library imports.
import tomli
import pytest

__date__ = "2022/08/15 16:56:19 Berthold Höllmann"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


@pytest.fixture
def base_path():
    "Return path to project base."
    res = Path(__file__).parent
    while not (res / "pyproject.toml").is_file():
        res = res.parent
    return res


@pytest.fixture
def py_project(base_path):
    "Return path of project `pyproject.toml`."
    return base_path / "pyproject.toml"


@pytest.fixture
def pyproject_inst(py_project):
    "Return `toml` instance of project `pyproject.toml`"
    return tomli.load(py_project.open("rb"))


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%Y/%02m/%02d %02H:%02M:%02S %L\""
# End:
