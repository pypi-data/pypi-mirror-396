import httpx
from Osdental.Encryptor.Aes import AES
from Osdental.Grpc.Client.AuthGrpcClient import AuthGrpcClient
from Osdental.Grpc.Client.GrpcConnection import GrpcConnection
from Osdental.Grpc.Client.SharedLegacyGrpcClient import SharedLegacyGrpcClient
from Osdental.Grpc.Adapter.SharedLegacyGrpcAdapter import SharedLegacyGrpcAdapter
from Osdental.Shared.Config import Config

class Instance:

    # Grpc Security
    grpc_security_conn = GrpcConnection(Config.SECURITY_GRPC_HOST)
    auth_client = AuthGrpcClient(grpc_security_conn)

    # Grpc Shared Resources
    grpc_shared_conn = GrpcConnection(Config.SHARED_GRPC_HOST)
    grpc_shared_client = SharedLegacyGrpcClient(grpc_shared_conn)
    grpc_shared_adapter = SharedLegacyGrpcAdapter(grpc_shared_client)

    # AES Encryptor
    aes = AES()

    # http_client
    http_client = httpx.AsyncClient(
        httpx.Timeout(
            connect=5.0,
            read=10.0,
            write=10.0,
            pool=5.0
        )
    )
