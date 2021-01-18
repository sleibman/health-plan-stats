
"""Tests the outermost level of code, confirming properly formatted output.

This code is most easily invoked using pytest.

  cd <health-plan-stats>
  pytest
"""

import os

def test_script():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    sample_data_dir = os.path.join(os.path.dirname(test_dir), 'sample_data')
    import process_plan_rates
    slcsp_file = os.path.join(sample_data_dir, 'slcsp.csv')
    plans_file = os.path.join(sample_data_dir, 'plans.csv')
    zips_file = os.path.join(sample_data_dir, 'zips.csv')
    result_csv_string = process_plan_rates.load_and_process_csv(slcsp_file, plans_file, zips_file)
    expected_csv_string = open(os.path.join(test_dir, 'expected_result.csv')).read()
    assert result_csv_string == expected_csv_string
