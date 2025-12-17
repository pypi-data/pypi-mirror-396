# IMDBExtract

Download IMDB series information into a CSV file containing lines
formatted:

1.  *\<empty cell\>*
2.  Season
3.  Episode
4.  *\<empty cell\>*
5.  *\<empty cell\>*
6.  *\<empty cell\>*
7.  Episode title and URL to episode Web side on IMDb
8.  Episode description from IMDb

This format is used im OO.Calc file keeping trac or wached episodes.

## `imdb_extract` command

::: mkdocs-click
    :module: berhoel.imdb_extract
    :command: imdb_extract
    :depth: 2

.. sphinx_argparse_cli::
   :module: berhoel.imdb_extract
   :func: get_parser
   :prog: imdb_extract

## Documentation

Documentatation can be found
[here](https://python.höllmanns.de/IMDBExtract).

