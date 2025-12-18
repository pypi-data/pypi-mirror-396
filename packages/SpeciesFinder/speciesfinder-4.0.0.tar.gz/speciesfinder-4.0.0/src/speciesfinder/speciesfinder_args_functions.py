"""
Additional SpeciesFinder functions.
Defines and parses CLI arguments for the SpeciesFinder tool
"""

import argparse
import logging

def parse_arguments():
    """Argument Parser"""
    parser = argparse.ArgumentParser(description="The SpeciesFinder service is used to find the best match (species identification) to the reads in one or more fastq files or one fasta file in a database produced using the KMA program")
    parser.add_argument('-i', '--infile',  required=True, help="FASTA(.gz) or FASTQ(.gz) file(s) to run SpeciesFinder on.", nargs='+')
    parser.add_argument('-o', '--output_folder',  help="folder to store the output", default='output')
    parser.add_argument('-db', '--db_path',  required=True, help="path to database and database file") 
    parser.add_argument('-tax', '--tax',  help="taxonomy file with additional data for each template in all databases (family, taxid and organism)")
    parser.add_argument("-x", "--extended_output",  help="Give extented output with taxonomy information - Needs the -tax flag to run", action="store_true")
    parser.add_argument("-kp", "--kma_path",    help="Path to kma program")


    args = parser.parse_args()

    if args.tax:
        args.extended_output = True
    elif args.extended_output:
        parser.error("--extended_output (-x) requires --tax (-tax) to be set.")

    return args
