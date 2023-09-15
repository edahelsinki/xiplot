import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from xiplot.setup import setup_xiplot_dash_app


def start_server(dash_duo) -> WebDriver:
    dash_duo.start_server(setup_xiplot_dash_app(data_dir="data"))
    driver = dash_duo.driver
    driver.implicitly_wait(5)  # wait and repoll all `driver.find_element()`
    time.sleep(1)
    dash_duo.wait_for_page()
    time.sleep(0.1)
    return driver


def load_file(dash_duo, driver):
    time.sleep(0.1)
    data_files_dd = dash_duo.find_element("#data_files")
    data_files_dd.click()

    dd_input = driver.find_element(By.XPATH, "//input[@autocomplete='off']")

    dd_input.send_keys("autompg-df.csv")
    dd_input.send_keys(Keys.RETURN)
    time.sleep(0.5)

    load_button = dash_duo.find_element("#submit-button")
    load_button.click()


def render_plot(dash_duo, driver, plot_name):
    load_file(dash_duo, driver)

    plots_tab = driver.find_element(
        By.XPATH, "//div[@id='control-tabs']/div[2]"
    )
    plots_tab.click()

    plot_type_dd_input = driver.find_element(
        By.XPATH,
        (
            "//div[@id='plot_type']/div[1]/div[1]/div[1]"
            "/div[@class='Select-input']/input[1]"
        ),
    )
    plot_type_dd_input.send_keys(plot_name)
    plot_type_dd_input.send_keys(Keys.RETURN)
    time.sleep(0.5)

    plot_add = driver.find_element(By.ID, "new_plot-button")
    plot_add.click()


def select_dropdown(dropdown, input):
    dropdown.click()
    color = dropdown.find_element(
        By.XPATH, "//div[2]/div[1]/div[1]/div[1]/div[2]/input"
    )
    color.send_keys(input)
    color.send_keys(Keys.RETURN)
    time.sleep(0.5)


def click_pdf_button(driver):
    pdf = driver.find_element(By.CLASS_NAME, "pdf_button")
    driver.execute_script("arguments[0].click();", pdf)
    time.sleep(0.1)
