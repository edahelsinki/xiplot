from dashapp.setup import setup_dash_app
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


"""def test_teac001_load_data_file(dash_duo):
    # TODO investigate how to implement dash testing
    dash_duo.start_server(setup_dash_app())

    dash_duo.wait_for_page()

    data_files_dd = dash_duo.driver.find_element(By.ID, "data_files")
    load_button = dash_duo.driver.find_element(By.ID, "submit-button")

    dash_duo.multiple_click(load_button, 1)

    ActionChains(dash_duo.driver).click(data_files_dd).key_down(Keys.DOWN).key_up(
        Keys.DOWN
    ).key_down(Keys.DOWN).key_up(Keys.DOWN).key_down(Keys.ENTER).key_up(
        Keys.ENTER
    ).click(
        load_button
    )

    message = dash_duo.driver.find_element(
        By.ID, "data-tab-upload-notify-container"
    ).text

    print(message)

    assert "The data file auto-mpg.csv was loaded successfully!" in message

    dash_duo.driver.close()
"""
