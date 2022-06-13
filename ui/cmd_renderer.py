import plotly.express as px


def show_help():
    print("""
        Commands
        --------

        file: Give a filename in the directory "data"

        pca: Execute given data with PCA

        scatter: Show a scatter giving a xaxis and yaxis

        histogram: Show a histogram giving a xaxis

        exit: exit from the app
    """)


def show_scatter(df, xaxis, yaxis):
    fig = px.scatter(data_frame=df, x=xaxis,
                     y=yaxis)
    fig.show()


def show_histogram(df, xaxis):
    fig = px.histogram(df, xaxis)
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


def file_not_found(filename):
    print(f"""
        File "{filename}" was not found in the directory "data"
    """)


def file_not_given():
    print("""
        Pick first a data file
    """)
