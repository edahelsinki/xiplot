from typing import Tuple
import plotly.express as px


def show_help():
    """
    Shows valid user commands.
    """

    print(
        """
        Commands
        --------

        file: Give a filename in the directory "data"

        columns: Show all the columns of the data frame

        pca: Execute given data with PCA

        scatter: Show a scatter giving a xaxis and yaxis

        histogram: Show a histogram giving a xaxis

        select: Select a subset of scatter plot

        exit: exit from the app
    """
    )


def show_scatter(df, xaxis, yaxis):
    """
    Renders a scatter plot.

    Parameters
    ----------
        df: Data frame
        xaxis: Unit(Column) of x axis
        yaxis: -"- y axis
    """
    fig = px.scatter(data_frame=df, x=xaxis, y=yaxis)
    fig.show()


def show_histogram(df, xaxis):
    """
    Renders a histogram.

    Parameters
    ----------
        df: Data frame
        xaxis: Unit(Columns) of x axis
    """
    fig = px.histogram(df, xaxis)
    fig.show()


def show_selected_scatter(df, xaxis, yaxis, cdnts: Tuple):
    """
    Renders a subset of a scatter plot.

    Parameters
    ----------
        df: Data frame
        xaxis: Unit(Column) of x axis
        yaxis: -"- y axis
        cdnts: x and y ranges of the subset of the scatter plot
    """
    fig = px.scatter(
        df, xaxis, yaxis, range_x=[cdnts[0], cdnts[1]], range_y=[cdnts[2], cdnts[3]]
    )
    fig.show()


def show_start_screen():
    """
    Show a welcome message
    """
    print("Welcome to the app!")


def show_columns(df):
    """
    Show all columns of the given data

    Parameters
    ----------
        df: Data frame
    """
    print(
        f"""
        {df.columns.tolist()}
    """
    )


def get_user_command():
    """
    Returns a command input from the user

    Returns
    -------
        input(): User input as a string

    """
    return input("Select a command: ")


def get_app_selection():
    """
    Returns an input from the user, whether the user wants to use Dash or commandline version

    Returns
    -------
        input(): User input as a string
    """
    return input('Select the version to execute ("1": Dash, "2": Commandline): ')


def get_user_file():
    """
    Returns the name of a data file

    Returns
    -------
        input(): File name as a string

    """
    return input("Pick a data file: ")


def get_xaxis():
    """
    Returns an unit of the x axis of a histogram or a scatter

    Returns
    -------
        input(): Unit as a string
    """
    return input("Choose x axis: ")


def get_yaxis():
    """
    Returns an unit of the y axis of a scatter

    Returns
    -------
        input(): Unit as a string
    """
    return input("Choose y axis: ")


def get_coordinates():
    """
    Returns a tuple of ranges of the x and y axis to create a subset of a scatter

    Returns
    -------
        (x_min, x_max, y_min, y_max): Coordinates of the range of the x and y axis as a tuple
        None: If invalid input
    """
    try:
        x_min = int(input("Set smaller x value: "))
        x_max = int(input("Set greater x value: "))
        y_min = int(input("Set smaller y value: "))
        y_max = int(input("Set greater y value: "))
        if x_min < x_max and y_min < y_max:
            return (x_min, x_max, y_min, y_max)
    except ValueError:
        return


def file_not_found(filename):
    """
    Shows an error message that the given file was not found in the directory "data".

    Parameters
    ----------
        filename: file name as a string
    """
    print(
        f"""
        File "{filename}" was not found in the directory "data"
    """
    )


def file_not_given():
    """
    Shows an error message that any file has not been loaded yet.
    """
    print(
        """
        Pick first a data file
    """
    )


def invalid_column_name(xaxis, yaxis=None):
    """
    Shows an error message that the given name of x or y axis is not in the columns of the dataset.

    Parameters
    ----------
        xaxis: Name given as an input to the xaxis
        yaxis: -"-, None, if not given anything
    """
    if not yaxis:
        print(
            f"""
        Invalid column name "{xaxis}"    
    """
        )
    else:
        print(
            f"""
        Invalid column name "{xaxis}" or "{yaxis}"
    """
        )


def invalid_input(user_input=""):
    """
    Shows an error message that the given input was invaid

    Parameters
    ----------
        user_input: User input as a string
    """
    print(
        f"""
        Invalid input {user_input}
    """
    )
