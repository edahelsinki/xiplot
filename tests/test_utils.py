import pandas as pd

from xiplot.utils.components import ColumnDropdown


def test_add_matching_values():
    d = {"col1": [1, 2], "col2": [3.0, 4.0], "col3": ["a", "b"]}
    df = pd.DataFrame(data=d)
    assert ["col0", "col1", "col2", "col3"] == ColumnDropdown.get_columns(
        df, pd.DataFrame(), ["col0"]
    )
    assert ["col1", "col2"] == ColumnDropdown.get_columns(
        df, pd.DataFrame(), numeric=True
    )
    assert ["col1", "col3"] == ColumnDropdown.get_columns(
        df, pd.DataFrame(), category=True
    )
