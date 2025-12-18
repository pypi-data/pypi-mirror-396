"""
Main SpeciesFinder script.
Calls all the basic functions of the tool.
"""

import os
import time
import logging
import subprocess

from speciesfinder.speciesfinder_args_functions import parse_arguments
from speciesfinder.speciesfinder_pre_functions import get_input_files, kma_path_exec, create_output, database
from speciesfinder.speciesfinder_kma_and_taxonomy import run_kma, process_taxonomy, process_speciesfinder_results, generate_json_output

def speciesfinder():

    start_time=time.time()
    logging.info("Starting SpeciesFinder")

    #Parse arguments
    args=parse_arguments()
    logging.info("Arguments parsed successfully")

    #Make input file list
    input_list=get_input_files(args)

    #Collect input file(s)
    infile=[]    
    for input_f in input_list:
        infile.extend(input_f.split())

    #Check if extended output was given
    extended_output=args.extended_output if args.extended_output is not None else False

    #Check if method path is executable
    kma_path=kma_path_exec(args)
      
    #Create output folder
    out_folder=create_output(args)

    #Get database(s)
    db_list=database(args)

    #Get taxonomy class of database used
    organism=os.path.basename(args.db_path).split(".")[0]

    #Execute KMA on input
    run_kma(infile, db_list, kma_path, out_folder)
    logging.info("KMA finished")
    logging.info("Time used to run KMA: {:.3f} s".format(time.time() - start_time))

    #If option for extended taxonomy info is chosen and taxonomy file is given, create results file with additional taxonomic info on the hits of KMA, else create default output
    process_taxonomy(args, out_folder)
    logging.info("Taxonomy processing completed")

    #Process db hits and prepare result file(s)
    result_file = os.path.join(out_folder, "results.txt" if extended_output else "results.res")
    hits=process_speciesfinder_results(result_file)
    logging.info("Processed SpeciesFinder results")

    #Read the version from the VERSION file
    with open('src/speciesfinder/__init__.py', 'r') as version_file:
        version = version_file.read().strip()

    #Get the current Git commit hashes using one-liners
    try:
        short_commit_hash = subprocess.check_output(
            ['git', 'log', '--pretty=format:%h', '-n', '1'],
            stderr=subprocess.DEVNULL  
        ).decode().strip()
        full_commit_hash = subprocess.check_output(
            ['git', 'log', '--pretty=format:%H', '-n', '1'],
            stderr=subprocess.DEVNULL  
        ).decode().strip()

        # In case the repo is empty
        if not short_hash or not full_hash:
            raise ValueError("No commits yet")

    except Exception:
        short_commit_hash = full_commit_hash = "unknown"

        logging.warning("Git commit hash not found (not a git repository?)")


    #Create json file with run info
    generate_json_output(hits, args, out_folder, organism, kma_path, version, short_commit_hash, full_commit_hash)

    #Execution time info
    logging.info(f"Total runtime for SpeciesFinder: {time.time() - start_time:.2f}s")
    print(f"SpeciesFinder run completed...")
    print(f"Total runtime for SpeciesFinder: {time.time() - start_time:.2f}s")
