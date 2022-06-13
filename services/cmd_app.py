from fileinput import fileno
from matplotlib.style import use
from sqlalchemy import true

from ui.cmd_renderer import *
from services.data_frame import *
from ui.cmd_renderer import *
import os

from ui.cmd_renderer import show_columns
from ui.cmd_renderer import file_not_found
from ui.cmd_renderer import file_not_given


def start():
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
                show_scatter(df, get_xaxis(), get_yaxis())
            except UnboundLocalError:
                file_not_given()
        elif user_command == "histogram":
            try:
                show_columns(df)
                show_histogram(df, get_xaxis())
            except UnboundLocalError:
                file_not_given()
        elif user_command == "exit":
            break
        else:
            show_help()
