from . import base

class POSextract(base.Base):
    def __init__(self, service_uri, api_key, _timeout):
        super().__init__(service_uri, api_key, _timeout)
        self._type = 'POS'