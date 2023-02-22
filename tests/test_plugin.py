import pytest
import subprocess
import sys
from pathlib import Path
import site

from xiplot.utils.dataframe import load_plugins_read


@pytest.fixture(scope="session", autouse=True)
def install_the_test_plugin():
    # This function is called by pytest before running any test
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


def test_load_plugin() -> None:
    print(load_plugins_read())
    assert any(ext == ".test" for _, ext in load_plugins_read())
