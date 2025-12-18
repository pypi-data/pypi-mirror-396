"""
Doctests for speciesfinder_args_functions

Testing `parse_arguments()` function:

>>> from speciesfinder.speciesfinder_args_functions import parse_arguments
>>> import sys

>>> # basic usage: fasta input + extended output with tax file
>>> sys.argv = ["prog", "-i", "file.fasta", "-db", "mydb.db",  "-x", "-tax", "taxfile.txt"]
>>> args = parse_arguments()
>>> args.infile
['file.fasta']
>>> args.db_path
'mydb.db'
>>> args.extended_output
True
>>> args.tax
'taxfile.txt'

>>> # extended_output without tax (should trigger error)
>>> sys.argv = ["prog", "-i", "file.fasta", "-x"]
>>> try:
...     parse_arguments()
... except SystemExit as e:
...     e.code
2

>>> # tax provided without -x (parser sets extended_output automatically)
>>> sys.argv = ["prog", "-i", "file.fasta", "-db", "mydb.db", "-tax", "taxfile.txt"]
>>> args = parse_arguments()
>>> args.extended_output
True
>>> args.tax
'taxfile.txt'

"""
