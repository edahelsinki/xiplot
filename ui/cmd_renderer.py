import plotly.express as px


def show_help():
    print("""
        Commands
        --------

        file: Give a filename in the directory "data"

        pca: Execute given data with PCA

        scatter: Show a scatter giving a xaxis and yaxis

        histogram: Show a histogram giving a xaxis

        select: Select a subset of scatter plot

        exit: exit from the app
    """)


def show_scatter(df, xaxis, yaxis):
    fig = px.scatter(data_frame=df, x=xaxis,
                     y=yaxis)
    fig.show()


def show_histogram(df, xaxis):
    fig = px.histogram(df, xaxis)
    fig.show()


def show_selected_scatter(df, xaxis, yaxis, cdnts):
    fig = px.scatter(df, xaxis, yaxis, range_x=[
                     cdnts[0], cdnts[1]], range_y=[cdnts[2], cdnts[3]])
    fig.show()


def show_start_screen():
    print("Welcome to the app!")


def show_columns(df):
    print(f"""
        {df.columns.tolist()}
    """)


def get_user_command():
    return input("Select a command: ")


def get_user_file():
    return input("Pick a data file: ")


def get_xaxis():
    return input("Choose x axis: ")


def get_yaxis():
    return input("Choose y axis: ")


def get_coordinates():
    x_min = int(input("Set smaller x value: "))
    x_max = int(input("Set greater x value: "))
    y_min = int(input("Set smaller y value: "))
    y_max = int(input("Set greater y value: "))
    if x_min < x_max and y_min < y_max:
        return (x_min, x_max, y_min, y_max)


def file_not_found(filename):
    print(f"""
        File "{filename}" was not found in the directory "data"
    """)


def file_not_given():
    print("""
        Pick first a data file
    """)


def invalid_column_name(xaxis, yaxis=None):
    if not yaxis:
        print(f"""
        Invalid column name "{xaxis}"    
    """)
    else:
        print(f"""
        Invalid column name "{xaxis}" or "{yaxis}"
    """)


def invalid_input(user_input=""):
    print(f"""
        Invalid input {user_input}
    """)
