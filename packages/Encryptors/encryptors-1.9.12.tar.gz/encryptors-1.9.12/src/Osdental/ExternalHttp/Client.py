import json
import asyncio
import httpx
from datetime import datetime
from typing import Dict, Optional
from Osdental.Decorators.Retry import rest_retry
from Osdental.ServicesBus.TaskQueue import task_queue
from Osdental.Shared.Logger import logger
from Osdental.Shared.Enums.Constant import Constant
from Osdental.Shared.Config import Config

# Limita concurrencia hacia Service Bus (evita saturación)
_SERVICE_BUS_SEMAPHORE = asyncio.Semaphore(100)


class APIClient(httpx.AsyncClient):

    def __init__(self, **kwargs):
        timeout = httpx.Timeout(
            connect=5.0,
            read=10.0,
            write=10.0,
            pool=5.0
        )
        super().__init__(
            follow_redirects=True,
            timeout=timeout,
            **kwargs
        )


    @staticmethod
    def fire_and_forget(coro):
        task = asyncio.create_task(coro)

        def _callback(t: asyncio.Task):
            try:
                t.result()
            except Exception as e:
                logger.error(f"[APIClient] background task error: {e}")

        task.add_done_callback(_callback)
        return task


    def _handle_response(self, response: httpx.Response):
        response.raise_for_status()

        content_type = (response.headers.get("content-type") or "").lower()

        if "application/json" in content_type:
            return response.json()
        elif any(t in content_type for t in ("text/", "html", "xml")):
            return response.text
        else:
            return response.content


    @rest_retry
    async def rest_request(
        self,
        method: str,
        url: str,
        *args,
        **kwargs
    ):
        headers = kwargs.get("headers", {})

        APIClient.fire_and_forget(
            self.send_request_to_service_bus(
                endpoint=url,
                body=kwargs.get("body"),
                headers=headers,
                http_method=method
            )
        )

        response = await self.request(method, url, *args, **kwargs)

        APIClient.fire_and_forget(
            self.send_response_to_service_bus(response, headers)
        )

        return self._handle_response(response)


    @rest_retry
    async def graphql_request(
        self,
        url: str,
        query: str,
        variables: Dict,
        headers: Optional[Dict] = None
    ):
        headers = headers or {}

        APIClient.fire_and_forget(
            self.send_request_to_service_bus(
                endpoint=url,
                body=variables,
                headers=headers,
                http_method="POST"
            )
        )

        response = await self.post(
            url,
            json={"query": query, "variables": variables},
            headers=headers
        )

        APIClient.fire_and_forget(
            self.send_response_to_service_bus(response, headers)
        )

        return self._handle_response(response)


    @staticmethod
    async def send_request_to_service_bus(
        endpoint: str,
        body: Optional[Dict],
        headers: Dict,
        http_method: str = "POST"
    ) -> None:
        async with _SERVICE_BUS_SEMAPHORE:
            operation_name = "*"

            if isinstance(body, dict):
                operation_name = body.get("operationName", "*")
                message_in = json.dumps(body)
            elif body:
                message_in = str(body)
            else:
                message_in = "*"

            message_json = {
                "idMessageLog": headers.get("Idmessagelog"),
                "type": "REQUEST",
                "environment": Config.ENVIRONMENT,
                "dateExecution": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "header": json.dumps(dict(headers)),
                "microServiceUrl": endpoint,
                "microServiceName": Config.MICROSERVICE_NAME,
                "microServiceVersion": Config.MICROSERVICE_NAME,
                "serviceName": operation_name,
                "machineNameUser": headers.get("Machinenameuser"),
                "ipUser": headers.get("Ipuser"),
                "userName": headers.get("Username"),
                "localitation": headers.get("Localitation"),
                "httpMethod": http_method,
                "httpResponseCode": "*",
                "messageIn": message_in,
                "messageOut": "*",
                "errorProducer": "*",
                "auditLog": Constant.MESSAGE_LOG_EXTERNAL,
            }

            await task_queue.enqueue(message_json)


    @staticmethod
    async def send_response_to_service_bus(
        response: httpx.Response,
        headers: Dict
    ) -> None:
        async with _SERVICE_BUS_SEMAPHORE:
            try:
                message_out = response.json()
            except Exception:
                message_out = response.text

            message_json = {
                "idMessageLog": headers.get("Idmessagelog"),
                "type": "RESPONSE",
                "dateExecution": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "httpResponseCode": str(response.status_code),
                "messageOut": message_out,
                "auditLog": Constant.MESSAGE_LOG_EXTERNAL,
            }

            await task_queue.enqueue(message_json)
