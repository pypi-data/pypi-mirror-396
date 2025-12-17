class Core:
    def __init__(self, client):
        self.client = client

    def list_os(self):
        return self.client.request("GET", "/os/")

    def list_pop(self):
        return self.client.request("GET", "/pop/")