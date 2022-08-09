from __future__ import annotations

import logging
import typing as t

from aiocache import Cache
from aiocache.plugins import BasePlugin
from aiocache.serializers import BaseSerializer


logging = logging.getLogger(__name__)  # type: ignore


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

    @staticmethod
    def create_cache_key(*args) -> str:
        key = ":".join([f"{arg}" for arg in args])
        return key


# class EnaCacheHandler:
#     def __init__(self, cache: EnaCache) -> None:
#         self.cache: EnaCache = cache

#     async def set(self, key: t.Any, value: t.Any, ttl: t.Optional[float] = None) -> None:


#         await self.cache.set(key, value, ttl)


#     async def get(self, key: t.Any, slice_key: t.Optional[t.Any] = None) -> t.Any:
#         cache_slice: dict = await self.cache.get(key=key)

#         if cache_slice:

#             if cached := cache_slice.get(slice_key):

#                 return cached

#             else:

#                 cache_slice[slice_key] = value

#                 await self.cache.set(key=key, value=cache_slice, ttl=ttl)

#         else:
