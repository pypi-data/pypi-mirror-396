import requests

class PragmaticLiveSession:
    BASE_URL = "https://games.pragmaticplaylive.net/api/ui"

    def __init__(self):
        self.session = requests.Session()
        self._configure_headers()

    def _configure_headers(self):
        self.session.headers.update({
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "pt-BR,pt;q=0.9",
        })

    def get(self, endpoint, params=None):
        url = f"{self.BASE_URL}/{endpoint}"
        return self.session.get(url, params=params)