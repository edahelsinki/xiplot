import time

from dashapp.setup import setup_dash_app


def test_dash001_launch(dash_duo):
    driver = dash_duo.driver
    dash_duo.start_server(setup_dash_app())
    time.sleep(1)
    dash_duo.wait_for_page()

    assert dash_duo.get_logs() == [], "browser console should contain no error"
