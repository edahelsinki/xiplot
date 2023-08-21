import warnings

from xiplot.tabs.plugins import get_plugins_cached
from xiplot.utils.dataframe import read_functions, write_functions


def test_plugin():
    try:
        import xiplot_test_plugin  # noqa: F401
    except ModuleNotFoundError:
        warnings.warn(
            "The test plugin is not installed, skipping plugin tests"
        )
        return

    # Remember to update this test if anything is added to the test_plugin.
    try:
        from xiplot_test_plugin import (
            Plot,
            create_global,
            plugin_load,
            plugin_write,
            register_callbacks,
        )
    except ImportError:
        warnings.warn(
            "The test plugin needs to be updated: "
            "`pip install --upgrade ./test_plugin`"
        )
        raise

    # Writing
    assert any(
        plugin == plugin_load for (_, _, plugin) in get_plugins_cached("read")
    )
    assert any(ext == plugin_load()[1] for _, ext in read_functions())

    # Reading
    assert any(
        plugin == plugin_write
        for (_, _, plugin) in get_plugins_cached("write")
    )
    assert any(ext == plugin_write()[1] for _, ext, _ in write_functions())

    # Plotting
    assert any(plugin == Plot for (_, _, plugin) in get_plugins_cached("plot"))
    assert any(
        plot.name() == Plot.name()
        for (_, _, plot) in get_plugins_cached("plot")
    )

    # Globals
    assert any(
        plugin == create_global
        for (_, _, plugin) in get_plugins_cached("global")
    )
    text = create_global().children[1].id["type"]
    assert any(
        text in str(g().children) for (_, _, g) in get_plugins_cached("global")
    )

    # Callbacks
    assert any(
        plugin == register_callbacks
        for (_, _, plugin) in get_plugins_cached("callback")
    )
    assert any(
        cb.__module__ == "xiplot_test_plugin"
        for (_, _, cb) in get_plugins_cached("callback")
    )
