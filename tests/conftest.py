import os
from pathlib import Path

from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def pytest_configure(config):
    # wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add  # noqa: E501
    # echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list  # noqa: E501
    # sudo apt-get update
    # sudo apt-get install libnss3-dev
    # sudo apt-get install google-chrome-stable

    webdriver = ChromeDriverManager().install()
    os.environ["PATH"] = (
        str(Path(webdriver).parent) + os.pathsep + os.environ["PATH"]
    )

    config.option.webdriver = "Chrome"
    config.option.headless = True


def pytest_setup_options():
    options = Options()
    options.add_argument("--disable-gpu")
    return options
