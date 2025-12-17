import json
from Osdental.Grpc.Client.SharedResourcesGrpcClient import SharedResourcesGrpcClient
from Osdental.Exception.ControlledException import OSDException
from Osdental.Models.ShardResource import ShardResource


class SharedResourcesGrpcAdapter:

    def __init__(self, client: SharedResourcesGrpcClient):
        self.client = client


    async def get_shared_resources(self, id_external_enterprise: str, microservice_name: str) -> ShardResource:
        response = await self.client.call_get_shared_resources(id_external_enterprise, microservice_name)
        if response.status != 200:
            raise OSDException(message=response.message, error=response.message)
        
        data_dict = json.loads(response.data)
        return ShardResource(**data_dict)