def get_pca_columns(df, features):
    from sklearn.decomposition import PCA
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler

    x = df[features]
    x = StandardScaler().fit_transform(x)

    mean_imputer = SimpleImputer(strategy="mean")
    x = mean_imputer.fit_transform(x)

    pca = PCA(n_components=2)
    pca.fit(x)
    return pca.transform(x)


def add_pca_columns_to_df(df, pca_cols):
    if pca_cols and len(pca_cols) == df.shape[0]:
        pca1 = [row[0] for row in pca_cols]
        pca2 = [row[1] for row in pca_cols]

        df["Xiplot_PCA_1"] = pca1
        df["Xiplot_PCA_2"] = pca2

    return df
