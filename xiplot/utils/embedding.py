from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer


def get_pca_columns(df, features):
    x = df[features]
    x = StandardScaler().fit_transform(x)

    mean_imputer = SimpleImputer(strategy="mean")
    x = mean_imputer.fit_transform(x)

    pca = PCA(n_components=2)
    pca.fit(x)
    return pca.transform(x)
