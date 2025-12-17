#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testing Unicode writer
"""

# Standard library imports.
import io

# First party library imports.
from berhoel.imdb_extract import unicodewriter

__date__ = "2022/08/15 17:06:24 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2013 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


def test_writerow_1():
    out = io.StringIO()
    writer = unicodewriter.UnicodeWriter(out)
    writer.writerow((1, 2, 3))

    assert out.getvalue().strip() == "1,2,3"


def test_writerow_2():
    out = io.StringIO()
    writer = unicodewriter.UnicodeWriter(out)
    writer.writerow(("ä", "ö", "ü"))

    data = out.getvalue().strip()
    assert data == "ä,ö,ü"


# Local Variables:
# mode: python
# compile-command: "cd ../../../ && python setup.py test"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
