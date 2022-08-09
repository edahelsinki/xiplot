from dashapp.setup import setup_dash_app

def test_dash001_launch(dash_duo):
    dash_duo.start_server(setup_dash_app())

    dash_duo.wait_for_page()
    
    assert dash_duo.get_logs() == [], "browser console should contain no error"
