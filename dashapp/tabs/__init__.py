from abc import ABC, abstractstaticmethod


class Tab(ABC):
    def __init__(self):
        raise TypeError("Tabs should not be constructed")

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @abstractstaticmethod
    def register_callbacks(app, df_from_store, df_to_store):
        pass

    @abstractstaticmethod
    def create_layout():
        pass

    @abstractstaticmethod
    def create_layout_globals():
        pass
