from services.cmd_app import start
import services.cmd_app as cmd_app
import services.dash_app as dash_app
#from ui.cmd_renderer import get_app_selection

if __name__ == "__main__":
    """
        app_selection: User selects an app version. Either Dash app or commandline app.
    """
    dash_app.start()

    """app_selection = get_app_selection()
    if app_selection == "1":
        dash_app.start()
    else:
        cmd_app.start()"""
