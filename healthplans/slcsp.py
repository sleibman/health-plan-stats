
"""Core logic for SLCSP code.

Typical entrypoint is the process_rates() function, which in turn calls slcsp once for each zip code in the requested
set of output results.

"""

import logging
import numpy as np
import pandas as pd


def slcsp_from_fips(fips, plans_df, zips_df):
    matching_rows = zips_df.loc[:, 'county_code'] == fips
    if not matching_rows.any():
        raise KeyError
    matching_fips_df = zips_df.loc[matching_rows, :]
    rate_area = matching_fips_df.rate_area.iloc[0]
    if not (rate_area == matching_fips_df.rate_area).all():
        logging.info(f"fips {fips}: More than one rate area matches; SLCSP is ambiguous.")
        return np.nan
    state = matching_fips_df.state.iloc[0]
    if not (state == matching_fips_df.state).all():
        logging.info(f"fips {fips}: Spans more than one state.")
    rates = plans_df.loc[(plans_df['state'] == state) & (plans_df['rate_area'] == rate_area) & (
            plans_df['metal_level'] == 'Silver'), 'rate']
    unique_rates = rates.unique()
    unique_rates.sort()
    if len(unique_rates) < 2:
        logging.info(f"Not enough rates in fips code {fips} to define a second lowest cost rate.")
        return np.nan
    return unique_rates[1]


def process_rates(plans_df, zips_df):
    """Reads input csv files into pandas DataFrames and executes core SLCSP logic.

    Example input files can be found at https://github.com/sleibman/health-plan-stats/sample_data

    Args:
        desired_zipcodes_df (pandas.DataFrame): Column 'zipcode' and 'rate', which may be empty or NaN values
        plans_df (pandas.DataFrame): plan information with columns 'plan_id','state','metal_level','rate','rate_area'
        zips_df (pandas.DataFrame): zip data with columns 'zipcode','state','county_code','name','rate_area'

    Returns:
        pandas.DataFrame: A copy of desired_zipcodes_df with the 'rate' column populated with results.
    """

    # howzabout all counties
    all_fips = pd.Series(zips_df.county_code.unique())
    logging.info(f'len of all_zips: {len(all_fips)}')
    expected_time = .008 * len(all_fips)
    logging.info(f'expected time: {expected_time} seconds')
    rates = all_fips.map(lambda fips: slcsp_from_fips(fips, plans_df, zips_df))

    results_df = pd.DataFrame({'fips': all_fips, 'rate': rates})
    return results_df
