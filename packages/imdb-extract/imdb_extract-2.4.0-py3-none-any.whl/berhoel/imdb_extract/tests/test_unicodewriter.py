"""Testing Unicode writer"""

import io

from berhoel.imdb_extract import unicodewriter


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
