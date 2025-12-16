from Osdental.Encryptor.Aes import AES
from Osdental.Grpc.Client.AuthGrpcClient import AuthGrpcClient
from Osdental.Grpc.Client.GrpcConnection import GrpcConnection
from Osdental.Grpc.Client.SharedLegacyGrpcClient import SharedLegacyGrpcClient
from Osdental.Grpc.Adapter.SharedLegacyGrpcAdapter import SharedLegacyGrpcAdapter
from Osdental.Shared.Config import Config

class Instance:

    grpc_security_conn = GrpcConnection(Config.SECURITY_GRPC_HOST)
    auth_client = AuthGrpcClient(grpc_security_conn)

    grpc_shared_conn = GrpcConnection(Config.SHARED_GRPC_HOST)
    grpc_shared_client = SharedLegacyGrpcClient(grpc_shared_conn)
    grpc_shared_adapter = SharedLegacyGrpcAdapter(grpc_shared_client)

    aes = AES()