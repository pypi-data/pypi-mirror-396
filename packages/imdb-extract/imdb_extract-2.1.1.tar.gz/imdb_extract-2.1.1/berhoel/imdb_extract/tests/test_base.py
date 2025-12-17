#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Basic tests for IMDBExtract.
"""

# First party library imports.
from berhoel import imdb_extract

__date__ = "2022/08/15 16:57:52 Berthold Höllmann"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


def test_version(pyproject_inst):
    "Test for consistent version numbers."
    assert imdb_extract.__version__ == pyproject_inst["tool"]["poetry"]["version"]


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%Y/%02m/%02d %02H:%02M:%02S %L\""
# End:
