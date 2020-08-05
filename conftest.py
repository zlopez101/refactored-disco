import pytest


@pytest.fixture(scope="module")
def sample_data(old_df):
    import pandas as pd
    import numpy as np

    df = pd.DataFrame(index=old_df.index)
