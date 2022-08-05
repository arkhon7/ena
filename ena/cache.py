import logging

import typing as t
import aiocache

from aiocache.serializers import BaseSerializer
from aiocache.plugins import BasePlugin

logging = logging.getLogger(__name__)  # type: ignore


class EnaCache(aiocache.Cache.MEMORY):
    def __init__(
        self,
        serializer: t.Optional[BaseSerializer] = None,
        plugins: t.Optional[t.List[BasePlugin]] = None,
        namespace: t.Optional[str] = None,
        timeout: t.Union[int, float] = 5,
    ) -> None:

        super().__init__(
            serializer=serializer,
            plugins=plugins,
            namespace=namespace,
            timeout=timeout,
        )

    @staticmethod
    def create_cache_key(*args) -> str:
        key = ":".join([f"{arg}" for arg in args])
        return key
