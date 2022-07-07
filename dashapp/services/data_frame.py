import os

import pandas as pd

from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans


def get_data_files():
    data_files = [
        f for f in os.listdir("data") if os.path.isfile(os.path.join("data", f))
    ]
    return data_files


def read_dataframe_with_extension(data, filename):
    """
    Read the given data and convert it to a pandas data frame

    Parameters
    ----------
        data: File name or File-like object
        filename: File name as a string

    Returns
    -------
        df: Pandas data frame
    """
    file_extension = os.path.splitext(filename)[1]
    if file_extension == ".csv":
        data = pd.read_csv(data)
    elif file_extension == ".json":
        data = pd.read_json(data)
    elif file_extension == ".pkl":
        data = pd.read_pickle(data)
    elif file_extension == ".ft":
        try:
            data = pd.read_feather(data)
        except ImportError:
            return None
    else:
        return None
    df = pd.DataFrame(data)
    return df


def read_data_file(filename):
    """
    Read the given data file and convert it to a pandas data frame

    Parameters
    ----------
        filename: File name as a string

    Returns
    -------
        df: Pandas data frame
    """
    if filename == "auto-mpg.data":
        return read_auto_mpg_file(filename)
    return read_dataframe_with_extension(f"data/{filename}", filename)


def read_auto_mpg_file(filename):
    widths = [7, 4, 10, 10, 11, 7, 4, 4, 30]
    data = pd.read_fwf(f"data/{filename}", widths=widths, header=None, na_values=["?"])
    df = pd.DataFrame(data)
    df.columns = pd.array(
        [
            "mpg",
            "cylinders",
            "displacement",
            "horsepower",
            "weight",
            "acceleration",
            "model-year",
            "origin",
            "car-name",
        ],
        dtype="U23",
    )

    features = pd.array(
        [
            "mpg",
            "cylinders",
            "displacement",
            "horsepower",
            "weight",
            "acceleration",
            "model-year",
            "origin",
        ],
        dtype="U23",
    )
    x = df.loc[:, features].values
    y = df.loc[:, ["car-name"]].values

    x = StandardScaler().fit_transform(x)

    # Fill NaN cells with the mean value of the column's values
    mean_imputer = SimpleImputer(strategy="mean")
    x = mean_imputer.fit_transform(x)

    # Create a PCA object and set 2 dimensions
    pca = PCA(n_components=2)
    principalComponens = pca.fit_transform(X=x)

    # Create a DataFrame object of the data that has been calculated with PCA
    pal_df = pd.DataFrame(data=principalComponens, columns=["PCA 1", "PCA 2"])

    # Concatenate
    final_df = pd.concat([pal_df, df], axis=1)
    return final_df


def get_kmean(df, k: int, features):
    scaler = StandardScaler()
    scale = scaler.fit_transform(df[features])
    km = KMeans(n_clusters=k).fit_predict(scale)

    return km


def get_cluster_centers(df, k, random_state=42):
    km = KMeans(k, random_state=random_state)
    km.fit(df)
    cluster_centers = km.cluster_centers_
    return cluster_centers
