from io import BytesIO


class FinallyCloseBytesIO:
    def __init__(self):
        self.bytes = NoCloseBytesIO()

    def __enter__(self):
        return self.bytes

    def __exit__(self, exc_type, exc_value, traceback):
        super(NoCloseBytesIO, self.bytes).close()


class NoCloseBytesIO(BytesIO):
    def close(self):
        pass
