from .modules.devices import DevicesAPI
from .modules.orgs import OrgsAPI


class ConnectClient:
    def __init__(self, **config):
        self.api_version = config.get("api_version", "v4")
        self.api_url = f"{config.get('base_url')}/api/{self.api_version}"

        token = config.get("token")
        if not token or not isinstance(token, str) or not token.strip():
            raise ValueError("Token must be provided as a non-empty string")

        self.token = token.strip()

        # Resource Classes
        self.devices = DevicesAPI(self)
        self.orgs = OrgsAPI(self)
