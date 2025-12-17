import json
import asyncio
from typing import Dict, Any
from Osdental.InternalHttp.Response import CustomResponse
from Osdental.Encryptor.Rsa import RSAEncryptor
from Osdental.Exception.ControlledException import RSAEncryptException, AESEncryptException
from Osdental.Shared.Logger import logger
from Osdental.Shared.Config import Config
from Osdental.Shared.Instance import Instance


class AuditLogHelper:

    _GRPC_LEGACY_CACHE = {"value": None, "timestamp": 0}
    _GRPC_LOCK = asyncio.Lock()
    
    @staticmethod
    async def get_cached_legacy():
        """Cache the legacy for X seconds to avoid GRPC calls on every resolver."""
        

        if AuditLogHelper._GRPC_LEGACY_CACHE["value"] is not None:
            return AuditLogHelper._GRPC_LEGACY_CACHE["value"]

        async with AuditLogHelper._GRPC_LOCK:
            if AuditLogHelper._GRPC_LEGACY_CACHE["value"] is not None:
                return AuditLogHelper._GRPC_LEGACY_CACHE["value"]

            legacy = await Instance.grpc_shared_adapter.get_shared_legacies(Config.LEGACY_NAME)
            AuditLogHelper._GRPC_LEGACY_CACHE["value"] = legacy
            return legacy

    @staticmethod
    def fire_and_forget(coro):
        """Centralized task handler to avoid silent errors."""
        task = asyncio.create_task(coro)

        def _callback(t: asyncio.Task):
            try:
                t.result()
            except Exception as e:
                logger.error(f"[fire_and_forget] Unhandled task error: {e}")

        task.add_done_callback(_callback)
        return task

    @staticmethod
    def try_decrypt_or_return_raw(data: str, private_key_rsa: str, aes_key: str) -> str:
        try:
            return RSAEncryptor.decrypt(data, private_key_rsa, silent=True)
        except RSAEncryptException:
            try:
                return Instance.aes.decrypt(aes_key, data, silent=True)
            except AESEncryptException:
                return data

    @staticmethod
    def enqueue_response(data: Any, batch: int, headers: Dict[str,str], msg_info: str = None):
        """Fully async-safe and error-traced enqueue."""
        content = None

        if isinstance(data, list) and data:
            if batch > 0 and len(data) > batch:
                batches = [data[i:i + batch] for i in range(0, len(data), batch)]
                for idx, b in enumerate(batches, start=1):
                    AuditLogHelper.fire_and_forget(CustomResponse(
                        content=json.dumps(b),
                        headers=headers,
                        batch=idx
                    ).send_to_service_bus())
                return

            content = json.dumps(data)
        else:
            content = json.dumps(data) if isinstance(data, dict) else msg_info

        AuditLogHelper.fire_and_forget(CustomResponse(content=content, headers=headers).send_to_service_bus())