# Plugin documentation

Check out the example plugin package [`test_plugin`](../../test_plugin/) for getting a better grasp of creating your own plugin packages.

## Package: Read unsupported file extension

A plugin package for reading data file with unsupported extensions. ([example](../../test_plugin/xiplot_test_plugin/__init__.py#L5-L10))

### API requirements

The plugin API requires a function returning two items. The first item must be a function that returns a pandas dataframe. The second item must be the new file extension as a string.

### Registeration to &chi;iplot

There are few steps to register a plugin package for reading unsupported data file extensions.

1. Create a pyproject.toml file into your package and include the following code

    ```
        [project]
        name = "__plugin_package_name__"
        version = "xxx"

        dependencies = [xxx]

        [build-system]
        requires = ["setuptools>=42", "wheel"]
        build-backend = "setuptools.build_meta"

        [tool.setuptools.packages.find]
        where = ["."]
        include = ["__plugin_package_name__"]
        exclude = []
        namespaces = true

        [project.entry-points."xiplot.plugin.read"]
        __entry_point_name__ = "__plugin_package_name__:__plugin_read_function__"

    ```

    Replace

    - `xxx` depending on your needs
    - `__plugin_package_name__` with your own package name
    - `__entry_point_name__` with an arbitrary entry point name
    - `__plugin_read_function__` with your read function of your package

2. Run your pyproject.toml with `pip install __plugin_package_name__` or if you have your package in the &chi;iplot package, run `pip install __plugin_package_directory_name__/`.

3. Run &chi;iplot normally with `python3 -m xiplot` and you are able to render your data file with the new file extension by uploading the file or by putting the file to `data` directory.


## Package: Write unsupported data file extension

A plugin package for writing and downloading unsupported file extensions. ([example](../../test_plugin/xiplot_test_plugin/__init__.py#L13-L17))

### API requirements

The plugin API requires a function returning three items.

- The first item must be a function that writes the dataframe to bytes. The function must have two parameters: pandas dataframe and a file name as a string. 

- The second item must be the the new file extension as a string that matches the written data.

- The third item must be the MIME type of the data as a string.

### Registeration to &chi;iplot

The registeration steps are similar to the registeration of the previous plugin package.

1. Create a pyproject.toml file into your package and include the following code

    ```
        [project]
        name = "__plugin_package_name__"
        version = "xxx"

        dependencies = [xxx]

        [build-system]
        requires = ["setuptools>=42", "wheel"]
        build-backend = "setuptools.build_meta"

        [tool.setuptools.packages.find]
        where = ["."]
        include = ["__plugin_package_name__"]
        exclude = []
        namespaces = true

        [project.entry-points."xiplot.plugin.write"]
        __entry_point_name__ = "__plugin_package_name__:__plugin_write_function__"

    ```

    Replace

    - `xxx` depending on your needs
    - `__plugin_package_name__` with your own package name
    - `__entry_point_name__` with an arbitrary entry point name
    - `__plugin_write_function__` with your write function of your package

2. Run your pyproject.toml with `pip install __plugin_package_name__` or if you have your package in the &chi;iplot package, run `pip install __plugin_package_directory_name__/`.

3. Run &chi;iplot normally with `python3 -m xiplot` and you are able to download the loaded data into the data file with your new extension.


## Package: New plot type

A plugin package for rendering a new plot type. ([example](../../test_plugin/xiplot_test_plugin/__init__.py#L45-L72))

### API requirements

The plugin API requires a class with a classmethod `name` and two static methods `register_callbacks` and `create_new_layout`.

- `name` method takes a class as a parameter and returns the name of it. 

- `register_callbacks` method requires three parameters: `app`, `df_from_store` and `df_to_store`.
    
    - `app` is an instance of the `dash.Dash` class, which is the main object that runs the application.

    - `df_from_store` is a function that transforms `dcc.Store` data into a pandas dataframe.

    - `df_to_store` is a function that transforms a dataframe to `dcc.Store` data.

    The purpose of the methods `df_from_store` and `df_to_store` are to reduce the time cost that occurs in a `Dash` app when every time a plot is been updated, the dataframe is been transferred from the server to the browser.

- Add @app.callback decorators from `dash.Dash` instance `app` inside the `register_callbacks` method

- `register_callback` does not require to return anything

- `create_new_layout` method requires four parameters: `index`, `df`, `columns` and `config`.
    
    - `index` is the index of the plot.

    - `df` is a pandas dataframe.

    - `columns` is a list of columns from the dataframe to use in the plot.

    - `config` is the configuration dictionary of the plot. This is used when the user wants to save the rendered plots. Defaults to dict().

- `create_new_layout` requires to return a Dash HTML Components module (`dash.html`)


### Registeration to &chi;iplot


1. Create a pyproject.toml file into your package and include the following code

    ```
        [project]
        name = "__plugin_package_name__"
        version = "xxx"

        dependencies = [xxx]

        [build-system]
        requires = ["setuptools>=42", "wheel"]
        build-backend = "setuptools.build_meta"

        [tool.setuptools.packages.find]
        where = ["."]
        include = ["__plugin_package_name__"]
        exclude = []
        namespaces = true

        [project.entry-points."xiplot.plugin.plot"]
        __entry_point_name__ = "__plugin_package_name__:__plugin_plot_class__"

    ```

    Replace

    - `xxx` depending on your needs
    - `__plugin_package_name__` with your own package name
    - `__entry_point_name__` with an arbitrary entry point name
    - `__plugin_plot_class__` with your plot class name of your package

2. Run your pyproject.toml with `pip install __plugin_package_name__` or if you have your package in the &chi;iplot package, run `pip install __plugin_package_directory_name__/`.

3. Run &chi;iplot normally with `python3 -m xiplot` and you are able to download the loaded data into the data file with your new extension.


## Package: Add a html component to the global layout

A plugin package for adding new html component to the global layout on &chi;iplot. ([example](../../test_plugin/xiplot_test_plugin/__init__.py#L20-L31))

### API requirements

The plugin API requires a function returning a Dash HTML Components module (`dash.html`).

### Registeration to &chi;iplot

The registeration steps are similar to the registeration of the previous plugin package.

1. Create a pyproject.toml file into your package and include the following code

    ```
        [project]
        name = "__plugin_package_name__"
        version = "xxx"

        dependencies = [xxx]

        [build-system]
        requires = ["setuptools>=42", "wheel"]
        build-backend = "setuptools.build_meta"

        [tool.setuptools.packages.find]
        where = ["."]
        include = ["__plugin_package_name__"]
        exclude = []
        namespaces = true

        [project.entry-points."xiplot.plugin.global"]
        __entry_point_name__ = "__plugin_package_name__:__plugin_create_global_function__"

    ```

    Replace

    - `xxx` depending on your needs
    - `__plugin_package_name__` with your own package name
    - `__entry_point_name__` with an arbitrary entry point name
    - `__plugin_create_global_function__` with your function of your package that returns Dash HTML Component module

2. Run your pyproject.toml with `pip install __plugin_package_name__` or if you have your package in the &chi;iplot package, run `pip install __plugin_package_directory_name__/`.

3. Run &chi;iplot normally with `python3 -m xiplot` and you are able to download the loaded data into the data file with your new extension.


## Package: Add @app.callback decorators

A plugin package for adding @app.callback decorators of `dash.Dash` instance. The main use case would be to add user interactive actions, which are not inside of plots' instances. ([example](../../test_plugin/xiplot_test_plugin/__init__.py#L34-L42))

### API requirements

The plugin API requires a function returning a Dash HTML Components module (`dash.html`). This function is the same as the [`register_callbacks`](#api-requirements-2) method of a plot class of the plugin package.

### Registeration to &chi;iplot

The registeration steps are similar to the registeration of the previous plugin package.

1. Create a pyproject.toml file into your package and include the following code

    ```
        [project]
        name = "__plugin_package_name__"
        version = "xxx"

        dependencies = [xxx]

        [build-system]
        requires = ["setuptools>=42", "wheel"]
        build-backend = "setuptools.build_meta"

        [tool.setuptools.packages.find]
        where = ["."]
        include = ["__plugin_package_name__"]
        exclude = []
        namespaces = true

        [project.entry-points."xiplot.plugin.callback"]
        __entry_point_name__ = "__plugin_package_name__:__plugin_register_callbacks_function__"

    ```

    Replace

    - `xxx` depending on your needs
    - `__plugin_package_name__` with your own package name
    - `__entry_point_name__` with an arbitrary entry point name
    - `__plugin_register_callbacks_function__` with your function of your package that returns Dash HTML Component module

2. Run your pyproject.toml with `pip install __plugin_package_name__` or if you have your package in the &chi;iplot package, run `pip install __plugin_package_directory_name__/`.

3. Run &chi;iplot normally with `python3 -m xiplot` and you are able to download the loaded data into the data file with your new extension.
