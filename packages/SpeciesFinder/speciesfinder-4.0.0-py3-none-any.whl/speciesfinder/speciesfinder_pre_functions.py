"""
Additional SpeciesFinder functions.
Initial check functions for SpeciesFinder
"""
import shutil
import logging
import sys
import os


def get_input_files(args):
    """Make input file list."""
    input_list = []
    if args.infile: 
        if len(args.infile) < 2:
            input_list.append("%s"%(args.infile[0]))
        else:
            multiple_infile = ' '.join(args.infile)
            input_list.append(multiple_infile) 
    else:
        logging.error("Error: Please specify input file(s)!")
        sys.exit(2)

    logging.info(f"Input files: {input_list}")
    return input_list


def kma_path_exec(args):
    """Check if method path is executable"""
    if args.kma_path:
        kma_path = args.kma_path  
    else:
        kma_path = shutil.which("kma")
        if kma_path is None:
            logging.error("Error: No valid path to a kma program was provided. Use the -kp flag to provide the path.")
            sys.exit(2)

    logging.info(f"Using KMA path: {kma_path}")
    return kma_path

def create_output(args):
    """Create (or reuse) output folder"""
    try:
       out_folder = args.output_folder
       os.makedirs(out_folder, exist_ok=True)
       logging.info(f"Output folder created or already exists: {out_folder}")
    except Exception as e:
       logging.exception("Failed to create output directory")
       sys.exit(2)
    return out_folder

def database(args):
    """Return list of database paths."""
    if not args.db_path:
        logging.error("Please specify a database!")
        sys.exit(2)

    logging.info(f"Databases to use: {[args.db_path]}")
    return [args.db_path]