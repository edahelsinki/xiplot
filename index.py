from services.cmd_app import start
import services.cmd_app as cmd_app
import services.dash_app as dash_app
from ui.cmd_renderer import get_user_command

if __name__ == "__main__":
    if get_user_command == "1":
        dash_app.start()
    else:
        cmd_app.start()
