import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer


def read_data_file(filename):
    widths = [7, 4, 10, 10, 11, 7, 4, 4, 30]
    data = pd.read_fwf(f"data/{filename}", widths=widths,
                       header=None, na_values=["?"])
    df = pd.DataFrame(data)
    return modify_column_names(df)


def modify_column_names(df: pd):
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