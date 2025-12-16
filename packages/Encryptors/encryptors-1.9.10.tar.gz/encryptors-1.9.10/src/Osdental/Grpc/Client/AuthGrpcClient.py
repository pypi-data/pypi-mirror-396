from Osdental.Grpc.Dtos.GrpcResponse import GrpcResponse
from Osdental.Grpc.Client.GrpcConnection import GrpcConnection
from Osdental.Decorators.Retry import grpc_retry
from Osdental.Grpc.Generated import Common_pb2
from Osdental.Grpc.Generated import Auth_pb2_grpc


class AuthGrpcClient:

    def __init__(self, connection: GrpcConnection):
        self.connection = connection
        self.stub = None

    async def _ensure_stub(self):
        if not self.stub:
            channel = await self.connection.connect()
            self.stub = Auth_pb2_grpc.AuthStub(channel)


    @grpc_retry
    async def validate_auth_token(self, request) -> GrpcResponse:
        await self._ensure_stub()
        request = Common_pb2.Request(data=request)
        response = await self.stub.ValidateAuthToken(request)
        return GrpcResponse(
            status=response.status, 
            message=response.message, 
            data=response.data
        )
