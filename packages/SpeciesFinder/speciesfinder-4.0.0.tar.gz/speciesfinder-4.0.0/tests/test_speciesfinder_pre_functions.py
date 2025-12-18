"""
Doctests for speciesfinder_pre_functions 

Testing `get_input_files()` function:

>>> from speciesfinder.speciesfinder_pre_functions import get_input_files

>>> # Single and double input files testing
>>> class Args: pass
>>> args = Args()
>>> args.infile = ["file1.fasta"]
>>> get_input_files(args)
['file1.fasta']
>>> args.infile = ["file1.fasta", "file2.fasta"]
>>> get_input_files(args)
['file1.fasta file2.fasta']


Testing `kma_path_exec()` function:

>>> from speciesfinder.speciesfinder_pre_functions import kma_path_exec

>>> # Provided kma path return testing
>>> args = Args()
>>> args.kma_path = "/usr/bin/kma"
>>> kma_path_exec(args)
'/usr/bin/kma'

Testing `create_output()` function:

>>> from speciesfinder.speciesfinder_pre_functions import create_output
>>> import tempfile, os

>>> # Create a temp output folder testing
>>> args = Args()
>>> args.output_folder = tempfile.mkdtemp()
>>> create_output(args) == args.output_folder
True

Testing `database()` function:

>>> from speciesfinder.speciesfinder_pre_functions import database

>>> # Return db as a list testing
>>> args = Args()
>>> args.db_path = "/path/to/db"
>>> database(args)
['/path/to/db']

"""
