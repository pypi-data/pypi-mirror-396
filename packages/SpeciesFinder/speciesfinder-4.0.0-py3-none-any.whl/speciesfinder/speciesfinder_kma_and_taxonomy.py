"""
Additional SpeciesFinder functions.
KMA execution,taxonomy process and json output code.
"""

import subprocess
import sys
import os
import logging
import csv
import json
from pathlib import Path
from datetime import datetime

def run_kma(input_list, db_list, kma_path, out_folder):
    """Run KMA tool for either single or paired reads"""

    if len(input_list)==2:
        logging.info(f"Paired end reads")
        for db in db_list:
            result_path = os.path.join(out_folder, "results")
            cmd = [kma_path, "-i"] + input_list + ["-o", result_path, "-t_db", db, "-mem_mode", "-na", "-nf", "-1t1"]

            logging.info(f"Running KMA with command: {' '.join(cmd)}")
            process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            if process.returncode != 0:
                logging.error(f"KMA failed with return code {process.returncode}")
                if err:
                    logging.error(f"KMA stderr:\n{err.decode()}")
            else:
                if out:
                    logging.info(f"KMA output:\n{out.decode()}")
                if err:
                    logging.info(f"KMA stderr:\n{err.decode()}")
    else:
        logging.info(f"Single end reads/Single fasta file")
        for input in input_list:
            for db in db_list:
                result_path = os.path.join(out_folder, "results")
                cmd = [kma_path, "-i", input, "-o", result_path, "-t_db", db, "-mem_mode", "-na", "-nf", "-1t1"]

                logging.info(f"Running KMA with command: {' '.join(cmd)}")
                process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = process.communicate()
                if process.returncode != 0:
                    logging.error(f"KMA failed with return code {process.returncode}")
                    if err:
                        logging.error(f"KMA stderr:\n{err.decode()}")
                else:
                    if out:
                        logging.info(f"KMA output:\n{out.decode()}")
                    if err:
                        logging.info(f"KMA stderr:\n{err.decode()}")

def process_taxonomy(args, out_folder):
    """Parse output from KMA (results.res) and append taxonomy information."""

    if args.tax is None:
        return  

    logging.info("Processing taxonomy data...")

    taxonomic_info={}

    try:
        with open(args.tax, newline="") as taxfile:
            reader = csv.reader(taxfile, delimiter="\t")
            for index_row, current_row in enumerate (reader):
                if not current_row:
                    continue
                accession = current_row[0].split(" ",1)[0]
                taxonomic_info[accession] = current_row[1:]
                if index_row == 1:
                    tax_field_count = len(current_row[1:])

    except IOError as err:
        logging.error(f"Can't open taxonomy file {err}")
        sys.exit(1)

    kma_res_file = Path(out_folder)/"results.res"
    extended_tax_output_file = Path(out_folder)/"results.txt"

    try:
        with open(kma_res_file, newline="") as infile, open (extended_tax_output_file, "w", newline="") as outfile:
            reader = csv.reader(infile, delimiter="\t")
            for line in reader:
                if not line:
                    continue

                if line[0].startswith("#"):
                    #Header line
                    header=line[1:]
                    tax_headers=["Accession Number", "Description", "TAXID", "Taxonomy", "TAXID", "Species"] 
                    new_header=["# Assembly"] + header + tax_headers
                    outfile.write("\t".join(new_header) + "\n")
                else:
                    #KMA info line
                    accession_and_description=line[0].split(" ", 1)
                    if len(accession_and_description)==2:
                        accession_id, accession_description=accession_and_description
                    else:
                        accession_id, accession_description=accession_and_description[0], "unknown"

                    kma_resistance_info=line[1:]

                    if accession_id in taxonomic_info:
                        all_taxonomic_data=taxonomic_info[accession_id]
                        assembly=all_taxonomic_data[0]
                        taxonomy_tree_info = all_taxonomic_data[1:]
                        results_tax = [assembly] + kma_resistance_info + [accession_id, accession_description] + taxonomy_tree_info
                    else:
                        unknown_fields = ["unknown"] * tax_field_count
                        results_tax = ["unknown"] + kma_resistance_info + [accession_id, accession_description] + unknown_fields

                    outfile.write("\t".join(map(str, results_tax)) + "\n")

    except IOError as err:
        logging.error(f"Can't open KMA results file: {err}")
        sys.exit(1)


def process_speciesfinder_results(result_file, extended_output=False):
    """Parse results from both normal and extended outputs."""
    try:
        with open(result_file, 'r') as res_or_txt:
            header, hits = [], {}

            for line in res_or_txt:
                if line.startswith('#'):
                    header = [h.strip().lstrip('#') for h in line.split('\t')]
                else:
                    lineSplit = [x.strip() for x in line.split('\t')]
                    hitDict = {header[i]: lineSplit[i] for i in range(len(lineSplit))}
                    assembly = lineSplit[0]  # always use Assembly as key
                    hits[assembly] = hitDict

            return hits

    except FileNotFoundError:
        logging.error(f"Results file not found: {result_file}")
        return {}
    except Exception as err:
        logging.error(f"Error while parsing results file: {err}")
        return {}

def generate_json_output(hits, args, out_folder, organism, kma_path, version, short_commit, full_commit):
    """Build and save the final JSON output."""

    extended = args.extended_output  

    output_data = {
        "type": "software_result",
        "databases": {
            f"Speciesfinder-{version}": {
                "type": "database",
                "database_name": f"Speciesfinder-{organism}",
                "database_version": version,
                "key": f"{organism}-local",
                "database_commit": "unknown"
            }
        },
        "seq_region": {},
        "software_executions": {
            "type": "software_exec",
            "command": " ".join(sys.argv),
        },
        "parameters": {
            "output": out_folder,
            "output_json": f"{out_folder}/data.json",
            "input": args.infile,
            "method": "kma",
            "kma": kma_path,
            "taxonomy_file": args.tax,
            "database_file": args.db_path,
            "extended_output": extended
        },
        "software_name": "Speciesfinder",
        "software_version": short_commit,
        "software_commit": full_commit,
        "run_date": datetime.now().strftime("%Y-%m-%d")
    }

    summary_species = []

    for assembly_id, hit in hits.items():
        if extended:
            # Extended: species + taxonomy info available
            name_field = hit.get("Species", assembly_id)
            tax = hit.get("Taxonomy", "")
            ref_acc = hit.get("Accession Number", "")
            summary_label = f'{name_field} ({float(hit.get("Query_Coverage", 0.0)):.1f}%)'
        else:
            # Non-extended: fall back to accession parsing
            name_field = assembly_id  
            tax = ""  
            ref_acc = assembly_id.split()[0] if assembly_id else "" 
            summary_label = f'{ref_acc} ({float(hit.get("Query_Coverage", 0.0)):.1f}%)'

        output_data["seq_region"][assembly_id] = {
            "type": "seq_region",
            "name": name_field,
            "tax": tax,
            "ref_acc": ref_acc,
            "score": int(hit.get("Score", 0)),
            "depth": float(hit.get("Depth", 0.0)),
            "query_coverage": float(hit.get("Query_Coverage", 0.0)),
            "template_length": int(hit.get("Template_length", 0)),
            "key": assembly_id,
            "template_coverage": float(hit.get("Template_Coverage", 0.0)),
            "ref_database": [f"{organism}-local"]
        }

        if float(hit.get("Query_Coverage", 0.0)) > 50.0:
            summary_species.append(summary_label)

    output_data["result_summary"] = summary_species if summary_species else "None"

    json_file = f"{out_folder}/data.json"
    with open(json_file, "w") as outfile:
        json.dump(output_data, outfile, indent=2)
    logging.info(f"JSON results saved to {json_file}")