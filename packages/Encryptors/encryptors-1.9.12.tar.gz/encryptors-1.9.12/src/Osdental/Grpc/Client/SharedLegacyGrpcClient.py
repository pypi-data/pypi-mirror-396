from Osdental.Grpc.Client.GrpcConnection import GrpcConnection
from Osdental.Grpc.Generated import Shared_pb2_grpc, Shared_pb2
from Osdental.Grpc.Dtos.GrpcResponse import GrpcResponse


class SharedLegacyGrpcClient:
    
    def __init__(self, connection: GrpcConnection):
        self.connection = connection
        self.stub = None

    async def _ensure_stub(self):
        if not self.stub:
            channel = await self.connection.connect()
            self.stub = Shared_pb2_grpc.ShardResourceStub(channel)


    async def call_get_shared_legacies(self, data: str) -> GrpcResponse:
        await self._ensure_stub()
        request = Shared_pb2.SetKeyPortal(data=data)
        response = await self.stub.GetShardLegacy(request)
        return GrpcResponse(
            status=response.status, 
            message=response.message, 
            data=response.data
        )