#!/usr/bin/env python3

"""
Entry point for SpeciesFinder.
Configures logging and delegates execution to SpeciesFinder().
"""

from speciesfinder.speciesfinder_run import speciesfinder
import logging
import sys

#Logging config
logging.basicConfig(
    filename="speciesfinder.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.INFO,
    force=True)

# Initial log message
logging.info("###############################################################")
logging.info("###############################################################")
logging.info("########################NEW SPECIESFINDER RUN#####################")

def main():

    try:
        return speciesfinder()
    except Exception:
        logging.exception(f"Fatal error in SpeciesFinder")
        return 1

if __name__=="__main__":
    sys.exit(main())
