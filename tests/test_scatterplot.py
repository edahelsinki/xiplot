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


def render_scatterplot(dash_duo, driver):
    load_file(dash_duo, driver)

    plots_tab = driver.find_element(By.XPATH, "//div[@id='control-tabs']/div[2]")
    plots_tab.click()

    plot_type_dd_input = driver.find_element(
        By.XPATH,
        "//div[@id='plot_type']/div[1]/div[1]/div[1]/div[@class='Select-input']/input[1]",
    )
    plot_type_dd_input.send_keys("Scatterplot")
    plot_type_dd_input.send_keys(Keys.RETURN)

    driver.implicitly_wait(1)

    plot_add = driver.find_element(By.ID, "new_plot-button")
    plot_add.click()

    driver.implicitly_wait(3)


def test_tesc001_render_scatterplot(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_scatterplot(dash_duo, driver)

    plot = driver.find_element(By.CLASS_NAME, "dash-graph")

    assert "scatterplot" in plot.get_attribute("outerHTML")

    driver.close()


def test_tesc002_change_axis_value(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_scatterplot(dash_duo, driver)

    driver.find_element(By.CLASS_NAME, "dd-double-left").click()

    x = driver.find_element(
        By.XPATH,
        "//div[@class='dd-double-left']/div[2]/div[1]/div[1]/div[1]/div[2]/input",
    )

    x.send_keys("mpg")
    x.send_keys(Keys.RETURN)

    driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[5]/div[2]/div[1]/div[1]/div[1]",
    ).click()

    ActionChains(driver).key_down(Keys.RETURN).key_up(Keys.RETURN)

    assert "mpg" in driver.find_element(By.CLASS_NAME, "xtitle").text

    driver.close()


def test_tesc002_target_setting(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_scatterplot(dash_duo, driver)

    color = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[3]/div[2]/div[1]/div[1]/div[1]/div[2]/input",
    )

    color.send_keys("PCA 1")
    color.send_keys(Keys.RETURN)

    symbol = driver.find_element(
        By.XPATH,
        "//div[@class='plots']/div[5]/div[2]/div[1]/div[1]/div[1]/div[2]/input",
    )

    symbol.send_keys("Clusters")
    symbol.send_keys(Keys.RETURN)

    assert dash_duo.get_logs() == [], "browser console should contain no error"


def test_tesc003_jitter_setting(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    render_scatterplot(dash_duo, driver)

    jitter_value = driver.find_element(By.CLASS_NAME, "rc-slider-handle")

    jitter_slider = driver.find_element(By.CLASS_NAME, "rc-slider-step")
    jitter_slider.click()

    assert "0.23" in jitter_value.get_attribute("outerHTML")
