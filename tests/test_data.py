from io import BytesIO

import numpy as np
import pandas as pd

from xiplot.utils.dataframe import read_only_dataframe, write_functions


def test_read_write():
    orig = pd.DataFrame(
        dict(
            x=np.arange(5),
            y=[f"a{i}" for i in range(5)],
            b=np.arange(5) > 2,
            c=np.arange(1, 6),
        )
    )

    def write(fn, df=orig):
        bytes = BytesIO()
        fn(orig, bytes)
        return BytesIO(bytes.getvalue())

    for fn, ext, mime in write_functions():
        bytes1 = write(fn)
        try:
            read1 = read_only_dataframe(bytes1, "a" + ext)
        except Exception:
            print("Error when reading:", ext)
            raise
        if "example" not in mime:
            assert orig.equals(read1), "Could not handle: " + ext
        bytes2 = write(fn, read1)
        read2 = read_only_dataframe(bytes2, "b" + ext)
        assert read1.equals(read2), "Is not consistent: " + ext
