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


# cache: EnaCache = Cache(EnaCache)


# async def Fibonacci(n: int):

#     if n < 0:
#         print("Incorrect input")

#     elif n == 0:
#         return 0

#     elif n == 1 or n == 2:
#         return 1

#     else:
#         # return await cached_fib(n - 1) + await cached_fib(n - 2)
#         return await Fibonacci(n - 1) + await Fibonacci(n - 2)


# async def main():

# cached_fib = cache.cached_async(("fib", 35), Fibonacci)

# print(await cached_fib(35))
# print(await cached_fib(35))
# print(await cached_fib(35))

#     await cache.set("aiocache1", Cache(EnaCache), ttl=9)

#     aiocache1: Cache.MEMORY = await cache.get("aiocache1")

#     print("testing sub cache")
#     await aiocache1.set("aiocache2", Cache(EnaCache), ttl=4)

#     print(await aiocache1.get("aiocache2"))

#     await asyncio.sleep(5)
#     print(await aiocache1.get("aiocache2"))

#     await asyncio.sleep(10)
#     print(await cache.get("aiocache1"))


# asyncio.run(main())


# cache: EnaCache = Cache(EnaCache)


# sample = {
#     "a": {
#         "a.a": {
#             "a.a.a": "gg",
#         },
#     },
#     "b": {"b.a": {"b.a.a": "wp"}},
# }

# print(cache.set_item(["a", "a.a", "a.a.b"], sample, value="python"))
# print(cache.get_item(["a", "a.a", "a.a.b"], sample))


# sample = [1, 3, 5, 7, 9]

# print(sample.pop(0))

# print(sample[-1])
