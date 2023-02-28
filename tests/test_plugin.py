import pytest
import subprocess
import sys
from pathlib import Path
import site

from xiplot.plugin import get_plugins_cached
from xiplot.utils.dataframe import load_plugins_read


@pytest.fixture(scope="session", autouse=True)
def install_the_test_plugin():
    try:
        # Remember to update this if anything new is added to the test_plugin
        from xiplot_test_plugin import (
            Plot,
            plugin_load,
            create_global,
            register_callbacks,
        )

        assert any(plot == Plot for plot in get_plugins_cached("plot"))
        assert any(plot == plugin_load for plot in get_plugins_cached("read"))
        assert any(plot == create_global for plot in get_plugins_cached("global"))
        assert any(
            plot == register_callbacks for plot in get_plugins_cached("callback")
        )
    except:
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
        site.main()  # Reload the path to make the new package available


def test_read_plugin():
    assert any(ext == ".test" for _, ext in load_plugins_read())


def test_plot_plugin():
    assert any(plot.name() == "  TEST PLUGIN" for plot in get_plugins_cached("plot"))


def test_global_plugin():
    assert any(g().children == "TEST PLUGIN" for g in get_plugins_cached("global"))


def test_callback_plugin():
    assert any(
        cb.__module__ == "xiplot_test_plugin" for cb in get_plugins_cached("callback")
    )
