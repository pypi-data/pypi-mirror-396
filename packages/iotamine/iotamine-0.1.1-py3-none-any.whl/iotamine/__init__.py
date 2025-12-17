from .client import IotamineClient
from .vm import VM
from .core import Core

class Iotamine:
    def __init__(self, api_key):
        self.client = IotamineClient(api_key)
        self.vm = VM(self.client)
        self.core = Core(self.client)
