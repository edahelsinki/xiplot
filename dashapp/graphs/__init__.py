from abc import ABC, abstractstaticmethod


class Graph(ABC):
    def __init__(self):
        raise TypeError("Graphs should not be constructed")

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @abstractstaticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        pass

    @abstractstaticmethod
    def create_new_layout(index, df, columns):
        pass
