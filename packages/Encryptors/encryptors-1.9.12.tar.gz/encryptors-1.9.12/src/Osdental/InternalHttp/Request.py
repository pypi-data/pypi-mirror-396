import json
from datetime import datetime, timezone
from fastapi import Request
from Osdental.ServicesBus.TaskQueue import task_queue
from Osdental.Shared.Enums.Constant import Constant
from Osdental.Shared.Config import Config
from Osdental.Helpers.RequestHelper import RequestHelper

class CustomRequest:

    def __init__(self, request: Request, aes_key_user: str):
        self.request = request
        self.aes_key_user = aes_key_user
        

    async def send_to_service_bus(self) -> None:
        try:
            message_in = await self.request.json()
        except Exception:
            message_in = {}

        request_data = RequestHelper._extract_data(message_in, self.aes_key_user)
        user_ip = RequestHelper._get_user_ip(self.request)
        location = await RequestHelper._get_location_cached(user_ip)
        id_user =RequestHelper._get_user_id(self.request, self.aes_key_user, Config.JWT_USER_KEY)

        message_json = {
            'idMessageLog': self.request.headers.get('Idmessagelog'),
            'type': Constant.RESPONSE_TYPE_REQUEST,
            'environment': Config.ENVIRONMENT,
            'dateExecution': datetime.now(timezone.utc).isoformat(),
            'header': json.dumps(dict(self.request.headers)),
            'microServiceUrl': str(self.request.url),
            'microServiceName': Config.MICROSERVICE_NAME,
            'microServiceVersion': Config.MICROSERVICE_VERSION,
            'serviceName': message_in.get('operationName'),
            'machineNameUser': self.request.headers.get('Machinenameuser', Constant.DEFAULT_EMPTY_VALUE),
            'ipUser': user_ip or Constant.DEFAULT_EMPTY_VALUE,
            'userName': self.request.headers.get('Username', Constant.DEFAULT_EMPTY_VALUE),
            'localitation': location or Constant.DEFAULT_EMPTY_VALUE,
            'httpMethod': self.request.method,
            'httpResponseCode': Constant.DEFAULT_EMPTY_VALUE,
            'messageIn': request_data,
            'messageOut': Constant.DEFAULT_EMPTY_VALUE,
            'errorProducer': Constant.DEFAULT_EMPTY_VALUE,
            'auditLog': Constant.MESSAGE_LOG_INTERNAL,
            'batch': Constant.DEFAULT_EMPTY_VALUE,
            'idUser': id_user
        }
        await task_queue.enqueue(message_json)