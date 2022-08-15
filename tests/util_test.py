import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


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


def render_plot(dash_duo, driver, plot_name):
    load_file(dash_duo, driver)

    plots_tab = driver.find_element(By.XPATH, "//div[@id='control-tabs']/div[2]")
    plots_tab.click()

    plot_type_dd_input = driver.find_element(
        By.XPATH,
        "//div[@id='plot_type']/div[1]/div[1]/div[1]/div[@class='Select-input']/input[1]",
    )
    plot_type_dd_input.send_keys(plot_name)
    plot_type_dd_input.send_keys(Keys.RETURN)

    driver.implicitly_wait(1)

    plot_add = driver.find_element(By.ID, "new_plot-button")
    plot_add.click()

    time.sleep(1)
