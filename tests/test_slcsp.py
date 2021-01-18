
"""Tests the logic in slcsp, specific to the task of finding the second lowest cost silver plan.

This code is most easily invoked using pytest.

  cd <health-plan-stats>
  pytest
"""


import pytest
from healthplans import slcsp
import pandas as pd
import numpy as np


@pytest.fixture
def desired_zipcodes_df():
    return pd.DataFrame({'zipcode': ['64148', '40813', '54923'], 'rate': np.nan})


@pytest.fixture
def zips_df():
    return pd.DataFrame(
        [['64148', 'MO', '29095', 'Jackson', 3],
         ['40813', 'KY', '21013', 'Bell', 8],
         ['54923', 'WI', '55139', 'Winnebago', 15]],
        columns=['zipcode', 'state', 'county_code', 'name', 'rate_area']
    )


@pytest.fixture
def plans_df():
    some_mo_plans_df = pd.DataFrame({'plan_id': ['78421VV7272023', '35866RG6997149', '28850TB6621800', '53546TY7687603',
                                                 '26631YR3384683', '03665WJ8941702', '02345TB1383341', '40205HK1927400',
                                                 '57237RP9645446', '64618UJ3132146', '43868JA2737085', '44945VH6426537',
                                                 '39063JC7040427'],
                                     'state': ['MO', 'MO', 'MO', 'MO', 'MO', 'MO', 'MO', 'MO', 'MO', 'MO', 'MO', 'MO',
                                               'MO'],
                                     'metal_level': ['Silver', 'Silver', 'Silver', 'Silver', 'Silver', 'Silver',
                                                     'Silver', 'Silver',
                                                     'Silver', 'Silver', 'Silver', 'Silver', 'Silver'],
                                     'rate': [290.05, 234.6, 265.82, 251.08, 351.6, 312.06, 245.2, 265.25, 253.65,
                                              319.57, 271.64,
                                              298.87, 341.24], 'rate_area': [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]})
    some_wi_plans_df = pd.DataFrame(
        {'plan_id': ['23018XQ8604367', '28341FR8516247'], 'state': ['WI', 'WI'], 'metal_level': ['Silver', 'Silver'],
         'rate': [326.7, 410.74], 'rate_area': [15, 15]})
    return pd.concat([some_mo_plans_df, some_wi_plans_df])


@pytest.fixture
def basic_expected_df(desired_zipcodes_df):
    expected_df = desired_zipcodes_df.copy()
    expected_df.loc[expected_df.zipcode == '64148', 'rate'] = 245.2
    expected_df.loc[expected_df.zipcode == '54923', 'rate'] = 410.74
    return expected_df

def test_something():
    assert 2 == 2

def test_basic(desired_zipcodes_df, plans_df, zips_df, basic_expected_df):
    results_df = slcsp.process_rates(desired_zipcodes_df, plans_df, zips_df)
    assert results_df.equals(basic_expected_df)

def test_multiple_rate_area(desired_zipcodes_df, plans_df, zips_df, basic_expected_df):
    # If there is more than one rate area for a given ZIP, the result is undefined and should be NaN in the
    # results DataFrame, blank in the final output.
    zips_multiple_rate_area_df = pd.concat([zips_df, pd.DataFrame(
        {'zipcode': ['54923', '54923'], 'state': ['WI', 'WI'], 'county_code': ['55047', '55137'],
         'name': ['Green Lake', 'Waushara'], 'rate_area': [15, 11]})])
    results_df = slcsp.process_rates(desired_zipcodes_df, plans_df, zips_multiple_rate_area_df)
    expected_df = basic_expected_df.copy()
    expected_df.loc[expected_df.zipcode == '54923', 'rate'] = np.nan
    assert results_df.equals(expected_df)

def test_no_rate_area(plans_df, zips_df):
    # The desired behavior has not been specified for the case in which no rate areas are defined for a given ZIP.
    # We alert the user by raising an exception. See comment in code for a more thorough consideration.
    desired_zips_no_rate_df = pd.DataFrame({'zipcode': ['64148', '40813', '99999'], 'rate': np.nan})
    with pytest.raises(KeyError):
        slcsp.process_rates(desired_zips_no_rate_df, plans_df, zips_df)

def test_lowest_rate_tie(zips_df):
    """
    Per spec: 'if a rate area had silver plans with rates of [197.3, 197.3, 201.1, 305.4, 306.7, 411.24], the
    SLCSP for that rate area would be 201.1, since it's the second lowest rate in that rate area.'
    """

    desired_zipcodes_df = pd.DataFrame({'zipcode': ['64148', '40813'], 'rate': np.nan})
    plans_with_rate_tie_df = pd.DataFrame(
        {'plan_id': ['A', 'B', 'C', 'D', 'E', 'F'],
         'state': ['MO', 'MO', 'MO', 'MO', 'MO', 'MO'],
         'metal_level': ['Silver', 'Silver', 'Silver', 'Silver', 'Silver', 'Silver'],
         'rate': [197.3, 197.3, 201.1, 305.4, 306.7, 411.24],
         'rate_area': [3, 3, 3, 3, 3, 3]})
    results_df = slcsp.process_rates(desired_zipcodes_df, plans_with_rate_tie_df, zips_df)
    expected_df = desired_zipcodes_df.copy()
    expected_df.loc[expected_df.zipcode == '64148', 'rate'] = 201.1
    assert results_df.equals(expected_df)
