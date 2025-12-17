import json
from Osdental.Grpc.Client.SharedLegacyGrpcClient import SharedLegacyGrpcClient
from Osdental.Exception.ControlledException import OSDException
from Osdental.Models.Legacy import Legacy

class SharedLegacyGrpcAdapter:

    def __init__(self, client: SharedLegacyGrpcClient):
        self.client = client


    async def get_shared_legacies(self, data: str) -> Legacy:
        response = await self.client.call_get_shared_legacies(data)
        if response.status != 200:
            raise OSDException(message=response.message, error=response.message)
        
        data_dict = json.loads(response.data)
        return Legacy(**data_dict)