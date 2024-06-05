# Author: ABHISHEK GUPTA <abhishek@quantgrade.com>

# Purpose: To test the create_pine_script function

# test_utils.py
import pytest
from src.utils import create_pine_script
import pandas as pd
from unit_tests.data import data_thirteen

@pytest.fixture
def sample_data():
    data = data_thirteen
    df = pd.DataFrame(data)
    float_cols = [x for x in df.columns if x not in ['ticker','datetime']]
    df[float_cols] = df[float_cols].astype(float)
    return df

def test_create_pine_script(sample_data):
    result = create_pine_script(sample_data)
    assert isinstance(result, str)
    assert 'QQQ' in result
