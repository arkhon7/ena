from __future__ import annotations

import logging
import typing as t


from aiocache import Cache
from aiocache.plugins import BasePlugin
from aiocache.serializers import BaseSerializer


logging = logging.getLogger(__name__)  # type: ignore


T = t.TypeVar("T")


class EnaCache(Cache.MEMORY):
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
