class ServerSideStoreBackend:
    def __init__(self):
        self.store = dict()

    def get(self, key, ignore_expired=False):
        return self.store.get(key)

    def set(self, key, value):
        self.store[key] = value

    def has(self, key):
        return key in self.store
