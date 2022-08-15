import time

from dashapp.setup import setup_dash_app
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def load_file(dash_duo, driver):
    data_files_dd = dash_duo.find_element("#data_files")
    load_button = dash_duo.find_element("#submit-button")

    data_files_dd.click()

    driver.implicitly_wait(1)

    dd_input = driver.find_element(By.XPATH, "//input[@autocomplete='off']")

    dd_input.send_keys("autompg-df.csv")
    dd_input.send_keys(Keys.RETURN)

    driver.implicitly_wait(1)

    load_button.click()


def render_histogram(dash_duo, driver):
    load_file(dash_duo, driver)

    plots_tab = driver.find_element(By.XPATH, "//div[@id='control-tabs']/div[2]")
    plots_tab.click()

    plot_type_dd_input = driver.find_element(
        By.XPATH,
        "//div[@id='plot_type']/div[1]/div[1]/div[1]/div[@class='Select-input']/input[1]",
    )
    plot_type_dd_input.send_keys("Histogram")
    plot_type_dd_input.send_keys(Keys.RETURN)

    driver.implicitly_wait(1)

    plot_add = driver.find_element(By.ID, "new_plot-button")
    plot_add.click()

    time.sleep(1)


def test_tehi001_render_histogram(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_histogram(dash_duo, driver)

    plot = driver.find_element(By.CLASS_NAME, "dash-graph")

    assert "histogram" in plot.get_attribute("outerHTML")

    driver.close()


def test_tehi002_set_axis(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_histogram(dash_duo, driver)

    driver.find_element(By.CLASS_NAME, "dd-single").click()

    x = driver.find_element(
        By.XPATH,
        "//div[@class='dd-single']/div[2]/div[1]/div[1]/div[1]/div[2]/input",
    )

    x.send_keys("mpg")
    x.send_keys(Keys.RETURN)

    time.sleep(1)

    driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]",
    ).click()

    ActionChains(driver).key_down(Keys.RETURN).key_up(Keys.RETURN)

    assert "mpg" in driver.find_element(By.CLASS_NAME, "xtitle").text


def test_tehi003_clear_clusters(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_histogram(dash_duo, driver)

    cluster_dd = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[3]/div[2]/div[1]/div[1]/span[1]",
    )
    cluster_dd.click()

    assert "Select..." in driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[3]/div[2]/div[1]/div[1]",
    ).get_attribute("outerHTML")
