from ui.cmd_renderer import *
from services.data_frame import *


def start():
    """
        Main function of the commandline app
    """
    show_start_screen()
    while True:
        user_command = get_user_command()
        if user_command == "file":
            filename = get_user_file()
            try:
                df = read_data_file(filename)
            except FileNotFoundError:
                file_not_found(filename)
        elif user_command == "columns":
            try:
                show_columns(df)
            except UnboundLocalError:
                file_not_given()
        elif user_command == "pca":
            try:
                df = run_pca(df)
            except UnboundLocalError:
                file_not_given()
        elif user_command == "scatter":
            try:
                show_columns(df)
                xaxis = get_xaxis()
                yaxis = get_yaxis()
                try:
                    show_scatter(df, xaxis, yaxis)
                except ValueError:
                    invalid_column_name(xaxis, yaxis)
            except UnboundLocalError:
                file_not_given()
        elif user_command == "histogram":
            try:
                show_columns(df)
                xaxis = get_xaxis()
                try:
                    show_histogram(df, xaxis)
                except ValueError:
                    invalid_column_name(xaxis)
            except UnboundLocalError:
                file_not_given()
        elif user_command == "select":
            try:
                show_columns(df)
                xaxis = get_xaxis()
                yaxis = get_yaxis()
                coordinates = get_coordinates()
                if not coordinates:
                    invalid_input()
                    continue
                try:
                    show_selected_scatter(df, xaxis, yaxis, coordinates)
                except ValueError:
                    invalid_column_name(xaxis, yaxis)
            except UnboundLocalError:
                file_not_given()
        elif user_command == "exit":
            break
        else:
            show_help()
