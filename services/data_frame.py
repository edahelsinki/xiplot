import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from os.path import splitext


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
    file_extension = splitext(filename)[1]
    if file_extension == ".csv":
        data = pd.read_csv(f"data/{filename}")
    elif file_extension == ".json":
        data = pd.read_json(f"data/{filename}")
    else:
        return
    df = pd.DataFrame(data)
    return df


def modify_column_names(df: pd):
    """
        For now this function is unused.
    """
    df.columns = pd.array(["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration",
                           "model-year", "origin", "car-name"], dtype="U23")
    return df


def run_pca(df):
    """
        For now this function is unused.
    """
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
    """
        Function to read the file auto-mpg.data
    """
    widths = [7, 4, 10, 10, 11, 7, 4, 4, 30]
    data = pd.read_fwf(f"data/{filename}", widths=widths,
                       header=None, na_values=["?"])
    df = pd.DataFrame(data)
    df.columns = pd.array(["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration",
                           "model-year", "origin", "car-name"], dtype="U23")
    return df
