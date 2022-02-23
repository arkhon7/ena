import logging

from aiocache import Cache  # type: ignore
from aiocache.serializers import PickleSerializer  # type: ignore
from typing import Any

logging = logging.getLogger(__name__)  # type: ignore


class EnaCache:
    def __init__(self) -> None:
        self.cache_data = Cache(
            cache_class=Cache.MEMORY,
            serializer=PickleSerializer(),
            namespace="ena-expr",
        )

    async def put_cache(self, key: str, field_key: str, data_key: str, data: Any) -> Any:

        cache = await self.cache_data.get(key=key)
        if cache:
            """Updates cache if cache key exists"""

            logging.debug(f"cache detected with key '{key}'")
            try:
                cache[field_key][data_key] = data
                logging.debug(f"cache path {field_key}:{data_key} found, updated cache path instead.")
                await self.cache_data.set(key=key, value=cache, ttl=3600)

            except KeyError:
                cache[field_key] = dict()
                cache[field_key][data_key] = data
                logging.debug(f"cache path {field_key}:{data_key} not found, added cache path instead.")
                await self.cache_data.set(key=key, value=cache, ttl=3600)

        else:
            """adds new cache"""

            logging.debug(" got new data, adding to cache.")
            cache = {field_key: {data_key: data}}
            await self.cache_data.set(key=key, value=cache, ttl=3600)

        logging.debug(f" saved cache info: [{key}:{field_key}:{data_key}]")

        return data

    async def get_cache(self, key: str, field_key: str, data_key: str) -> Any:

        cache = await self.cache_data.get(key=key)

        try:
            data = cache[field_key][data_key]
            logging.debug(f" cache hit: [{key}:{field_key}:{data_key}]")
            return data

        except KeyError:
            logging.debug(f" cache miss: [{key}:{field_key}:{data_key}]")

        except TypeError:
            logging.debug(f" cache miss: [{key}:{field_key}:{data_key}]")

    async def is_cached(self, key: str, field_key: str, data_key: str) -> bool:
        if await self.get_cache(key=key, field_key=field_key, data_key=data_key):
            return True
        return False
