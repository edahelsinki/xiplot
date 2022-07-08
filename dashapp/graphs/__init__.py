from abc import ABC, abstractstaticmethod


class Graph(ABC):
    def __init__(self):
        raise TypeError("Graphs should not be constructed")

    @abstractstaticmethod
    def name() -> str:
        pass

    @abstractstaticmethod
    def register_callbacks(app):
        pass

    @abstractstaticmethod
    def create_new_layout(index, df, columns):
        pass
