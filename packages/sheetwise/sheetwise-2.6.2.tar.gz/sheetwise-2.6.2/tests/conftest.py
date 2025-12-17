"""Test configuration and fixtures."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    data = {
        "A": ["Header1", "Data1", "Data2", "", "Data3"],
        "B": ["Header2", 100, 200, "", 300],
        "C": ["Header3", "2023-01-01", "2023-01-02", "", "2023-01-03"],
        "D": ["", "", "", "", ""],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sparse_dataframe():
    """Create a sparse DataFrame for testing compression."""
    df = pd.DataFrame(index=range(20), columns=[f"Col_{i}" for i in range(10)])
    df = df.fillna("")

    # Add some data in specific regions
    df.iloc[0, 0] = "Title"
    df.iloc[2, 1] = "Revenue"
    df.iloc[2, 2] = 1000
    df.iloc[3, 1] = "Expenses"
    df.iloc[3, 2] = 800
    df.iloc[5, 5] = "Product A"
    df.iloc[5, 6] = "In Stock"

    return df


@pytest.fixture
def financial_dataframe():
    """Create a realistic financial DataFrame."""
    data = {
        "Metric": ["Revenue", "Expenses", "Profit", "Growth %"],
        "2020": [100.5, 80.2, 20.3, "15%"],
        "2021": [120.3, 85.1, 35.2, "20%"],
        "2022": [145.8, 95.4, 50.4, "18%"],
        "Total": [366.6, 260.7, 105.9, ""],
    }
    return pd.DataFrame(data)
