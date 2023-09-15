import pandas as pd

from xiplot.utils.auxiliary import decode_aux, encode_aux, toggle_selected
from xiplot.utils.components import ColumnDropdown
from xiplot.utils.regex import dropdown_regex, get_columns_by_regex


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


def test_regex():
    options, selected, hits = dropdown_regex(
        ["asd", "bsd", "csd", "dsd"], ["asd", "bs (regex)"], "cs"
    )
    assert options == ["asd", "bs (regex: 1)", "cs (regex: 1)", "dsd"]
    assert options[:-1] == selected
    assert hits == 1

    cols = get_columns_by_regex(
        ["asd", "bsd", "csd", "dsd"], ["asd", "(b|c)sd (regex)"]
    )
    assert cols == ["asd", "bsd", "csd"]


def test_aux():
    df = pd.DataFrame(index=range(4))
    assert df.equals(decode_aux(encode_aux(df)))
    df = pd.DataFrame(
        {"a": [1, 2, 3], "b": [1.0, 2.3, 3.2], "c": ["a", "b", "a"]}
    )
    assert df.equals(decode_aux(encode_aux(df)))
    df = toggle_selected(df, [])
    assert df.equals(toggle_selected(toggle_selected(df, 1), [1]))
