
"""Core logic for SLCSP code.

Typical entrypoint is the process_rates() function, which in turn calls slcsp once for each zip code in the requested
set of output results.

"""

import logging
import numpy as np
import pandas as pd
import timeit

def fips(zipcode, plans_df, zips_df):
    """Reads input csv files into pandas DataFrames and executes core SLCSP logic.

    Example input files can be found at https://github.com/sleibman/health-plan-stats/sample_data

    Args:
        zipcode (str): ZIP code for which the SLCSP should be determined
        plans_df (pandas.DataFrame): plan information with columns 'plan_id','state','metal_level','rate','rate_area'
        zips_df (pandas.DataFrame): zip data with columns 'zipcode','state','county_code','name','rate_area'

    Returns:
        float: The SLCSP rate for the specified ZIP code. NaN if undefined.
    """
    #starttime = timeit.default_timer()
    # pandas Series with boolean values indicating rows where the value of the 'zipcode' column matches `zip`
    matching_rows = zips_df.loc[:, 'zipcode'] == zipcode
    if not matching_rows.any():
        # The zips_df DataFrame (by default this would typically come from `zips.csv`) does not have any entries
        # defining rate area for the given ZIP code. The specification does not indicate what should be done in this
        # scenario (and the sample files do not contain this scenario), so we throw an exception under the assumption
        # that the user should be alerted and not silently fail to populate a value. A future enhancement to be to
        # allow a configuration parameter that leaves data blank and continues, as is already the desired behavior
        # for cases where the ZIP code is in more than one rate area.
        raise KeyError(f"ZIP {zipcode}: No rate areas defined.")

    # Small dataframe with [zipcode, state, county_code, name, rate_area] for a single zip code.
    # Often just one row, but may have multiple rows if the zip code spans counties or rate areas.
    matching_zips_df = zips_df.loc[matching_rows, :]

    rate_area = matching_zips_df.rate_area.iloc[0]
    if not (rate_area == matching_zips_df.rate_area).all():
        logging.info(f"ZIP {zipcode}: More than one rate area matches; SLCSP is ambiguous.")
        return np.nan

    county_code = matching_zips_df.county_code.iloc[0]

    return county_code


def slcsp(zipcode, plans_df, zips_df):
    """Reads input csv files into pandas DataFrames and executes core SLCSP logic.

    Example input files can be found at https://github.com/sleibman/health-plan-stats/sample_data

    Args:
        zipcode (str): ZIP code for which the SLCSP should be determined
        plans_df (pandas.DataFrame): plan information with columns 'plan_id','state','metal_level','rate','rate_area'
        zips_df (pandas.DataFrame): zip data with columns 'zipcode','state','county_code','name','rate_area'

    Returns:
        float: The SLCSP rate for the specified ZIP code. NaN if undefined.
    """
    #starttime = timeit.default_timer()
    # pandas Series with boolean values indicating rows where the value of the 'zipcode' column matches `zip`
    matching_rows = zips_df.loc[:, 'zipcode'] == zipcode
    if not matching_rows.any():
        # The zips_df DataFrame (by default this would typically come from `zips.csv`) does not have any entries
        # defining rate area for the given ZIP code. The specification does not indicate what should be done in this
        # scenario (and the sample files do not contain this scenario), so we throw an exception under the assumption
        # that the user should be alerted and not silently fail to populate a value. A future enhancement to be to
        # allow a configuration parameter that leaves data blank and continues, as is already the desired behavior
        # for cases where the ZIP code is in more than one rate area.
        raise KeyError(f"ZIP {zipcode}: No rate areas defined.")

    # Small dataframe with [zipcode, state, county_code, name, rate_area] for a single zip code.
    # Often just one row, but may have multiple rows if the zip code spans counties or rate areas.
    matching_zips_df = zips_df.loc[matching_rows, :]

    rate_area = matching_zips_df.rate_area.iloc[0]
    if not (rate_area == matching_zips_df.rate_area).all():
        logging.info(f"ZIP {zipcode}: More than one rate area matches; SLCSP is ambiguous.")
        return np.nan

    state = matching_zips_df.state.iloc[0]
    if not (state == matching_zips_df.state).all():
        # TODO: Ask the partner what the desired behavior is. ZIP codes that span multiple states are unusual,
        #  but do exist (example: 42223 is US Army Fort Campbell, spanning the KY-TN state line). The code as
        #  currently written would pick the first of multiple matching states and limit itself to the rate area
        #  definitions found there. Given more time for a real application we would ask (because the number of edge
        #  cases are small), and propose that in the absence of other insight, we'd handle it by looking for rate
        #  areas in all applicable states and then applying the usual logic.
        logging.info(f"ZIP {zipcode}: Spans more than one state.")

    rates = plans_df.loc[(plans_df['state'] == state) & (plans_df['rate_area'] == rate_area) & (
            plans_df['metal_level'] == 'Silver'), 'rate']

    # Per the specification, when computing "second lowest cost", we only consider unique rates.
    # "For example, if a rate area had silver plans with rates of [197.3, 197.3, 201.1, 305.4, 306.7, 411.24],
    # the SLCSP for that rate area would be 201.1"
    unique_rates = rates.unique()

    unique_rates.sort()  # sorts in place, mutating the unique_rates array

    if len(unique_rates) < 2:
        logging.info(f"Not enough rates in ZIP code {zipcode} to define a second lowest cost rate.")
        return np.nan
    #print("The time difference is :", timeit.default_timer() - starttime)
    return unique_rates[1]


def process_rates(desired_zipcodes_df, plans_df, zips_df):
    """Reads input csv files into pandas DataFrames and executes core SLCSP logic.

    Example input files can be found at https://github.com/sleibman/health-plan-stats/sample_data

    Args:
        desired_zipcodes_df (pandas.DataFrame): Column 'zipcode' and 'rate', which may be empty or NaN values
        plans_df (pandas.DataFrame): plan information with columns 'plan_id','state','metal_level','rate','rate_area'
        zips_df (pandas.DataFrame): zip data with columns 'zipcode','state','county_code','name','rate_area'

    Returns:
        pandas.DataFrame: A copy of desired_zipcodes_df with the 'rate' column populated with results.
    """

    # howzabout all zip codes
    all_zips = pd.Series(zips_df.zipcode.unique())  # .head()
    #all_zips = desired_zipcodes_df.loc[:, 'zipcode']
    print(f'len of all_zips: {len(all_zips)}')
    expected_time = .01 * len(all_zips)
    print(f'expected time: {expected_time} seconds')

    rates = all_zips.map(lambda zip: slcsp(zip, plans_df, zips_df))

    fips_list = all_zips.map(lambda zip: fips(zip, plans_df, zips_df))

    #results_df = desired_zipcodes_df.copy()
    #results_df.loc[:, 'rate'] = rates
    #results_df.loc[:, 'fips'] = fips_list

    results_df = pd.DataFrame({'fips': fips_list, 'rate': rates})
    return results_df
