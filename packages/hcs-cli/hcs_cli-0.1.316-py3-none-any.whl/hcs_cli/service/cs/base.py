from hcs_core.sglib.client_util import regional_service_client


class ConnectionService:
    """Connection Service Client for HCS CLI"""

    def __init__(self, region: str):
        self.client = regional_service_client("connection-service", region=region)

    def keys(self):
        return self.client.get("/core/v1/.well-known/jwks.json")


def region(region: str) -> ConnectionService:
    return ConnectionService(region)
