#!/usr/bin/env python3

"""Executable script for computing the Second Lowest Cost Silver Plan (SLCSP).

This code implements the assignment described at https://homework.adhoc.team/slcsp/
For a complete description of this implementation, see https://github.com/sleibman/health-plan-stats

  Typical usage example:
    ./process_plan_rates.py

Log messages are written to stderr. Since the specified behavior mandates that the results be sent to stdout, it may be
helpful to redirect stderr to a file, via:
    ./process_plan_rates.py 2> slcsp.log

"""

import logging
import pandas as pd

from healthplans import slcsp

def load_and_process_csv(slcsp_file, plans_file, zips_file):
    """Reads input csv files into pandas DataFrames and executes core SLCSP logic.

    Example input files can be found at https://github.com/sleibman/health-plan-stats/sample_data

    Args:
        slcsp_file (str): Path and filename for slcsp.csv
        plans_file (str): Path and filename for plans.csv
        zips_file (str): Path and filename for zips.csv

    Returns:
        str: A string in csv format, suitable for writing to stdout or a csv file.
    """
    desired_zipcodes_df = pd.read_csv(slcsp_file, dtype={'zipcode': 'str'})
    plans_df = pd.read_csv(plans_file, dtype={'plan_id': 'str'})
    zips_df = pd.read_csv(zips_file, dtype={'zipcode': 'str', 'county_code': 'str'})

    results_df = slcsp.process_rates(desired_zipcodes_df, plans_df, zips_df)
    return results_df.to_csv(index=False, float_format='%.2f')

if __name__ == "__main__":
    # TODO: In a more complete application, logging would be made easily configurable. In this case, the log level is
    #  hardcoded, and log output goes to stderr.
    logging.basicConfig(level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # TODO: Provide the ability to override input file paths on the command line or via config file.

    # Notice that we force ZIP codes to be treated as non-numeric strings, because they are identifiers with things like
    # leading zeros and no meaningful numeric operations. Same with county codes, which happen to be FIPS codes with
    # properties similar to ZIPs.
    # We allow the plan rates to be represented as floats, even though they are currency values. If the application
    # were extended to manipulate these values in any way, this would merit some care in order to ensure the desired
    # rounding behavior.
    print(load_and_process_csv('sample_data/slcsp.csv', 'sample_data/plans.csv', 'sample_data/zips.csv'))
