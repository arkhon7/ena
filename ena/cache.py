from __future__ import annotations

import asyncio
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

    async def _get_item(self, identifier: t.Union[str, list]):

        if isinstance(identifier, list):
            cache: t.Optional[t.Dict[str, t.Dict]] = await self.get(identifier[0])

            if cache:
                identifier.pop(0)

                for key in identifier:
                    try:
                        cache = cache[key]

                    except KeyError:
                        logging.debug("key '{}' does not exist.".format(key))

                        return None

                return cache

        else:
            cache = await self.get(identifier)
            return cache

    async def _set_item(self, identifier: t.Union[str, list], value: t.Any, ttl: int = 60):

        if isinstance(identifier, list):

            main_key = identifier.pop(0)
            cache: t.Dict[str, t.Any] = {}

            for key in identifier[:-1]:
                cache = cache.setdefault(key, {})

            cache[identifier[-1]] = value

            await self.set(main_key, cache, ttl=ttl)

        else:
            await self.set(identifier, value, ttl=ttl)

    def cached(self, identifier: t.Union[str, list], callback: t.Callable[..., T], ttl=60) -> t.Callable[..., T]:
        async def _async_cached(*args, **kwargs):

            if cached := await self._get_item(identifier):

                return cached

            if asyncio.iscoroutinefunction(callback):

                async_result = await callback(*args, **kwargs)
                await self._set_item(identifier, value=async_result, ttl=ttl)

                return async_result

            else:

                result = callback(*args, **kwargs)
                await self._set_item(identifier, value=result, ttl=ttl)

                return result

        return _async_cached
