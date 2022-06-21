import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from sklearn import preprocessing


def get_data_files():
    data_files = [f for f in os.listdir(
        "data") if os.path.isfile(os.path.join("data", f))]
    return data_files


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
    file_extension = os.path.splitext(filename)[1]
    if file_extension == ".csv":
        data = pd.read_csv(f"data/{filename}")
    elif file_extension == ".json":
        data = pd.read_json(f"data/{filename}")
    else:
        return
    df = pd.DataFrame(data)
    return df


def read_auto_mpg_file(filename):
    widths = [7, 4, 10, 10, 11, 7, 4, 4, 30]
    data = pd.read_fwf(f"data/{filename}", widths=widths,
                       header=None, na_values=["?"])
    df = pd.DataFrame(data)
    df.columns = pd.array(["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration",
                           "model-year", "origin", "car-name"], dtype="U23")

    features = pd.array(["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration",
                         "model-year", "origin"], dtype="U23")
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
    pal_df = pd.DataFrame(data=principalComponens, columns=[
        "PCA 1", "PCA 2"])

    # Concatenate
    final_df = pd.concat(
        [pal_df, df], axis=1)
    return final_df


def get_kmean(df, k: int, x_axis, y_axis):
    scaler = MinMaxScaler()
    scale = scaler.fit_transform(df[[x_axis, y_axis]])
    df_scale = pd.DataFrame(scale, columns=[x_axis, y_axis])
    km = KMeans(n_clusters=k)
    y_predicted = km.fit_predict(df[[x_axis, y_axis]])
    df["Clusters"] = km.labels_

    return df


"""def modify_column_names(df: pd):
    df.columns = pd.array(["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration",
                           "model-year", "origin", "car-name"], dtype="U23")
    return df


def run_pca(df):
    features = pd.array(["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration",
                         "model-year", "origin"], dtype="U23")
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
    pal_df = pd.DataFrame(data=principalComponens, columns=[
        "principal component 1", "principal component 2"])

    # Concatenate
    final_df = pd.concat(
        [pal_df, df], axis=1)
    return final_df


def load_auto_mpg(filename):
    widths = [7, 4, 10, 10, 11, 7, 4, 4, 30]
    data = pd.read_fwf(f"data/{filename}", widths=widths,
                       header=None, na_values=["?"])
    df = pd.DataFrame(data)
    df.columns = pd.array(["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration",
                           "model-year", "origin", "car-name"], dtype="U23")
    return df
"""
