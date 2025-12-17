class IotamineAPIError(Exception):
    def __init__(self, status_code, message):
        super().__init__(f"Iotamine API Error {status_code}: {message}")
