import site
import subprocess
import sys
from pathlib import Path

import pytest

from xiplot.plugin import get_plugins_cached
from xiplot.utils.dataframe import read_functions, write_functions


@pytest.fixture(scope="session", autouse=True)
def install_the_test_plugin():
    try:
        # Remember to update this if anything new is added to the test_plugin
        from xiplot_test_plugin import (
            Plot,
            create_global,
            plugin_load,
            plugin_write,
        )
        from xiplot_test_plugin import register_callbacks as reg_cb

        assert any(
            plugin == Plot for (_, _, plugin) in get_plugins_cached("plot")
        )
        assert any(
            plugin == plugin_load
            for (_, _, plugin) in get_plugins_cached("read")
        )
        assert any(
            plugin == plugin_write
            for (_, _, plugin) in get_plugins_cached("write")
        )
        assert any(
            plugin == create_global
            for (_, _, plugin) in get_plugins_cached("global")
        )
        assert any(
            plugin == reg_cb
            for (_, _, plugin) in get_plugins_cached("callback")
        )
    except Exception:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-input",
                "--upgrade",
                "--editable",
                str(Path(__file__).parent.parent / "test_plugin"),
            ]
        )
        # Reload the path to make the new package available
        site.main()

        from importlib import reload

        import xiplot_test_plugin

        reload(xiplot_test_plugin)
        get_plugins_cached.cache = None


def test_read_plugin():
    assert any(ext == ".test" for _, ext in read_functions())


def test_write_plugin():
    assert any(ext == ".test" for _, ext, _ in write_functions())


def test_plot_plugin():
    assert any(
        plot.name() == "  TEST PLUGIN"
        for (_, _, plot) in get_plugins_cached("plot")
    )


def test_global_plugin():
    assert any(
        g().children == "TEST PLUGIN"
        for (_, _, g) in get_plugins_cached("global")
    )


def test_callback_plugin():
    assert any(
        cb.__module__ == "xiplot_test_plugin"
        for (_, _, cb) in get_plugins_cached("callback")
    )
