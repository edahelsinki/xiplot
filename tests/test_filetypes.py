from io import BytesIO

import pandas as pd

try:
    from xiplot_filetypes import (
        read_feather,
        read_parquet,
        write_feather,
        write_parquet,
    )
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(
        0, str(Path(__file__).parent.parent / "plugin_xiplot_filetypes")
    )
    from xiplot_filetypes import (
        read_feather,
        read_parquet,
        write_feather,
        write_parquet,
    )


def test_feather():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["a", "b", "c"]})
    io = BytesIO()
    write_feather()[0](df, io)
    df2 = read_feather()[0](io)
    assert df.equals(df2)


def test_parquet():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["a", "b", "c"]})
    io = BytesIO()
    write_parquet()[0](df, io)
    df2 = read_parquet()[0](io)
    assert df.equals(df2)
