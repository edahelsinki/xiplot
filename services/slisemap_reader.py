from os import PathLike
from typing import Optional, Sequence, Union
import pandas as pd
import numpy as np


def slisemap_to_dataframe(
    path: Union[str, PathLike, "Slisemap"],
    variables: Optional[Sequence[str]] = None,
    targets: Union[str, Sequence[str], None] = None,
) -> pd.DataFrame:
    """Convert a ``Slisemap`` object to a ``pd.DataFrame``.
    Args:
        path (Union[str, PathLike, Slisemap]): Slisemap object or path to a saved slisemap object.
        variables (Optional[Sequence[str]], optional): List of variables names (columns in X). Defaults to None.
        targets (Union[str, Sequence[str], None], optional): List of target names (columns in Y). Defaults to None.
    Returns:
        pd.DataFrame: A dataframe containing the X, Y, Z, B matrices from the Slisemap object.
    """
    # importing slisemap inside the function so that installing slisemap
    # is not required if one is not loading slisemap
    from slisemap import Slisemap
    if isinstance(path, Slisemap):
        sm = path
    else:
        sm = Slisemap.load(path, "cpu")
    Z = sm.get_Z(rotate=True)
    X = sm.get_X(intercept=False)
    Y = sm.get_Y()
    B = sm.get_B()
    mat = np.concatenate((X, Y, Z, B), 1)
    # The following mess is just to enable optional variable and target names
    names = []
    if variables:
        assert len(variables) == X.shape[1]
        names += [f"X_{i}" for i in variables]
    else:
        names += [f"X_{i+1}" for i in range(X.shape[1])]
    if targets:
        if isinstance(targets, str):
            assert Y.shape[1] == 1
            targets = [targets]
        assert len(targets) == Y.shape[1]
        names += [f"Y_{i}" for i in targets]
    elif Y.shape[1] == 1:
        names.append("Y")
    else:
        names += [f"Y_{i+1}" for i in range(Y.shape[1])]
    names += [f"Z_{i+1}" for i in range(Z.shape[1])]
    if variables:
        if sm.intercept:
            variables = variables + ["B_Intercept"]
        if B.shape[1] == len(variables):
            names += [f"B_{i}" for i in variables]
        elif B.shape[1] % len(variables) == 0 and B.shape[1] % len(targets) == 0:
            variables = [f"{t}:{v}" for t in targets for v in variables]
            names += [f"B_{i}" for i in variables[: B.shape[1]]]
        else:
            names += [f"B_{i+1}" for i in range(X.shape[1])]
    else:
        if sm.intercept:
            names += [f"B_{i+1}" for i in range(B.shape[1] - 1)
                      ] + ["B_Intercept"]
        else:
            names += [f"B_{i+1}" for i in range(B.shape[1])]
    # Then we create a dataframe to return
    df = pd.DataFrame.from_records(mat, columns=names)
    return df


if __name__ == "__main__":

    print(slisemap_to_dataframe("data/Wang-Slisemap-PCA50.sm").shape)
