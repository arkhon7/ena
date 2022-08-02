import nest_asyncio


import asyncio
import asyncpg
import os
import dotenv
import pytest
import logging

from ena.helpers import create_hash, parse_message_from_link
from ena.cache import clear_all

from plugins.react_role.models import EmojiRolePair, ActiveEmojiRolePair
from plugins.react_role.controller import (
    add_active_pair,
    add_pair,
    delete_active_pair,
    delete_pair,
    fetch_all_active_pairs_by_message,
    fetch_all_pairs,
    fetch_pair,
)


dotenv.load_dotenv()


GUILD_ID = 957116703374979093

GAMES_ROLE = 995564101902278736
ANIME_ROLE = 995335085698076732
MEMES_ROLE = 995335303927697510

# not animated
KOKO_SHY = "koko_shy", 957305862798594078
KOKO_FALLEN = "koko_fallen", 958034560564731954
KOKO_FRIGHT = "koko_fright", 957302949556678686

# animated
KOKO_RAGE = "koko_rage", 979224342762246184
KOKO_CHILL = "koko_chill", 979223909981356093
KOKO_PEEK = "koko_peek", 979226119104524338

MESSAGES = [
    parse_message_from_link("https://discord.com/channels/957116703374979093/1000311913663692840/1000322969458987048"),
    parse_message_from_link("https://discord.com/channels/957116703374979093/1000311913663692840/1000328944500879390"),
    parse_message_from_link("https://discord.com/channels/957116703374979093/1000311913663692840/1000723429428834335"),
    parse_message_from_link("https://discord.com/channels/957116703374979093/1000311913663692840/1001881451308003398"),
]

LOGGER = logging.getLogger(__name__)  # type:ignore


def get_mock_pair_list():
    PAIR_DATA: list[EmojiRolePair] = []

    not_animated = [KOKO_SHY, KOKO_FALLEN, KOKO_FRIGHT]
    animated = [KOKO_RAGE, KOKO_CHILL, KOKO_PEEK]
    roles = [MEMES_ROLE, GAMES_ROLE, ANIME_ROLE]

    for role in roles:
        for emoji in not_animated:
            PAIR_DATA.append(
                EmojiRolePair(
                    id=create_hash(role, emoji[0]),
                    role_id=role,
                    emoji_id=emoji[1],
                    emoji_name=emoji[0],
                    is_animated=False,
                    guild_id=GUILD_ID,
                )
            )

        for emoji in animated:
            PAIR_DATA.append(
                EmojiRolePair(
                    id=create_hash(role, emoji[0]),
                    role_id=role,
                    emoji_id=emoji[1],
                    emoji_name=emoji[0],
                    is_animated=True,
                    guild_id=GUILD_ID,
                )
            )

    return PAIR_DATA


def get_mock_active_pair_list():

    ACTIVE_PAIR_DATA: list[ActiveEmojiRolePair] = []

    for msg in MESSAGES:
        for erp in get_mock_pair_list():
            ACTIVE_PAIR_DATA.append(
                ActiveEmojiRolePair(
                    id=create_hash(
                        erp.role_id,
                        erp.emoji_name,
                        msg.message_id,
                    ),
                    role_id=erp.role_id,
                    emoji_id=erp.emoji_id,
                    emoji_name=erp.emoji_name,
                    is_animated=erp.is_animated,
                    message_id=msg.message_id,
                    channel_id=msg.channel_id,
                    guild_id=msg.guild_id,
                )
            )

    return ACTIVE_PAIR_DATA


async def test_setup(pool: asyncpg.Pool):
    conn: asyncpg.Connection
    async with pool.acquire() as conn:

        with open("db/schema.psql") as schema:
            await conn.execute(schema.read())

            await conn.execute("INSERT INTO guilds VALUES ($1) ON CONFLICT DO NOTHING", GUILD_ID)


@pytest.fixture
def event_loop():
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    res = policy.new_event_loop()
    asyncio.set_event_loop(res)
    res._close = res.close
    res.close = lambda: None

    nest_asyncio.apply(res)

    yield res

    res._close()


@pytest.fixture
def pool(event_loop: asyncio.AbstractEventLoop):
    async def get_pool():
        pool = await asyncpg.create_pool(os.getenv("TEST_DB_STRING"))
        return pool

    pool = event_loop.run_until_complete(get_pool())
    event_loop.close()

    return pool


@pytest.fixture
async def aio_benchmark(benchmark, event_loop):
    def _wrapper(func, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):

            @benchmark
            def _():

                return event_loop.run_until_complete(func(*args, **kwargs))

        else:
            benchmark(func, *args, **kwargs)

    return _wrapper


# TESTS ON REACTION ROLE PLUGIN CONTROLLERS


@pytest.fixture
def setup_method(pool: asyncpg.Pool, event_loop):
    async def _setup():

        await test_setup(pool)
        await clear_all()

    event_loop.run_until_complete(_setup())
    yield

    event_loop.run_until_complete(pool.close())


@pytest.mark.asyncio
async def test_fetch_all_pairs(pool):
    # INSERTION OF DATA
    mock = get_mock_pair_list()
    for pair in mock:

        await add_pair(
            pool,
            pair.id,
            pair.role_id,
            pair.emoji_id,
            pair.emoji_name,
            pair.is_animated,
            pair.guild_id,
        )

    # FETCH
    records = await fetch_all_pairs(pool, GUILD_ID)

    assert len(records) == len(mock)


@pytest.mark.asyncio
async def test_fetch_pair(pool):
    # INSERTION OF DATA
    mock = get_mock_pair_list()
    for pair in mock:

        await add_pair(
            pool,
            pair.id,
            pair.role_id,
            pair.emoji_id,
            pair.emoji_name,
            pair.is_animated,
            pair.guild_id,
        )

        # FETCH

        record = await fetch_pair(pool, pair.id, GUILD_ID)

        erp = EmojiRolePair.from_dict(record)

        assert erp.id == pair.id


@pytest.mark.asyncio
async def test_add_pair(pool):
    for pair in get_mock_pair_list():

        await add_pair(
            pool,
            pair.id,
            pair.role_id,
            pair.emoji_id,
            pair.emoji_name,
            pair.is_animated,
            pair.guild_id,
        )


@pytest.mark.asyncio
async def test_add_pair_duplication_error(pool):
    for pair in get_mock_pair_list():

        await add_pair(
            pool,
            pair.id,
            pair.role_id,
            pair.emoji_id,
            pair.emoji_name,
            pair.is_animated,
            pair.guild_id,
        )

    for pair in get_mock_pair_list():
        with pytest.raises(asyncpg.UniqueViolationError):
            await add_pair(
                pool,
                pair.id,
                pair.role_id,
                pair.emoji_id,
                pair.emoji_name,
                pair.is_animated,
                pair.guild_id,
            )


@pytest.mark.asyncio
async def test_delete_pair(pool):
    # INSERTING DATA
    for pair in get_mock_pair_list():

        await add_pair(
            pool,
            pair.id,
            pair.role_id,
            pair.emoji_id,
            pair.emoji_name,
            pair.is_animated,
            pair.guild_id,
        )

    # DELETING DATA
    for pair in get_mock_pair_list():

        await delete_pair(pool, pair.id, GUILD_ID)


# @pytest.mark.asyncio
# async def test_fetch_all_active_pairs(pool):

#     aerp_mock = get_mock_active_pair_list()
#     erp_mock = get_mock_pair_list()

#     # Insert pair data
#     for erp in erp_mock:

#         await add_pair(
#             pool,
#             erp.id,
#             erp.role_id,
#             erp.emoji_id,
#             erp.emoji_name,
#             erp.is_animated,
#             erp.guild_id,
#         )

#     # Insert active pair data
#     for aerp in aerp_mock:
#         pair_id = create_hash(
#             aerp.role_id,
#             aerp.emoji_name,
#         )

#         await add_active_pair(
#             pool,
#             aerp.id,
#             pair_id,
#             aerp.message_id,
#             aerp.channel_id,
#             aerp.guild_id,
#         )

#     records = await fetch_all_active_pairs(pool, GUILD_ID)

#     assert len(records) == len(aerp_mock)


@pytest.mark.asyncio
async def test_fetch_all_active_pairs_by_message(pool):
    aerp_mock = get_mock_active_pair_list()
    erp_mock = get_mock_pair_list()

    # Insert pair data
    for erp in erp_mock:

        await add_pair(
            pool,
            erp.id,
            erp.role_id,
            erp.emoji_id,
            erp.emoji_name,
            erp.is_animated,
            erp.guild_id,
        )

    # Insert active pair data
    for aerp in aerp_mock:
        pair_id = create_hash(
            aerp.role_id,
            aerp.emoji_name,
        )

        await add_active_pair(
            pool,
            aerp.id,
            pair_id,
            aerp.message_id,
            aerp.channel_id,
            aerp.guild_id,
        )

    records = await fetch_all_active_pairs_by_message(pool, aerp_mock[0].message_id, aerp_mock[0].guild_id)

    assert len(records) == (len(aerp_mock) / len(MESSAGES))


# @pytest.mark.asyncio
# async def test_fetch_active_pair(pool):
#     aerp_mock = get_mock_active_pair_list()
#     erp_mock = get_mock_pair_list()

#     # Insert pair data
#     for erp in erp_mock:

#         await add_pair(
#             pool,
#             erp.id,
#             erp.role_id,
#             erp.emoji_id,
#             erp.emoji_name,
#             erp.is_animated,
#             erp.guild_id,
#         )

#     # Insert active pair data
#     for aerp in aerp_mock:
#         pair_id = create_hash(
#             aerp.role_id,
#             aerp.emoji_name,
#         )

#         await add_active_pair(
#             pool,
#             aerp.id,
#             pair_id,
#             aerp.message_id,
#             aerp.channel_id,
#             aerp.guild_id,
#         )

#     record = await fetch_active_pair(pool, aerp_mock[0].id, GUILD_ID)
#     active_pair = ActiveEmojiRolePair.from_dict(record)

#     assert isinstance(active_pair.id, str)
#     assert isinstance(active_pair.role_id, int)
#     assert isinstance(active_pair.emoji_id, int)
#     assert isinstance(active_pair.emoji_name, str)
#     assert isinstance(active_pair.message_id, int)
#     assert isinstance(active_pair.channel_id, int)
#     assert isinstance(active_pair.guild_id, int)


# @pytest.mark.asyncio
# async def test_delete_active_pair(pool):

#     aerp_mock = get_mock_active_pair_list()
#     erp_mock = get_mock_pair_list()

#     # Insert pair data
#     for erp in erp_mock:

#         await add_pair(
#             pool,
#             erp.id,
#             erp.role_id,
#             erp.emoji_id,
#             erp.emoji_name,
#             erp.is_animated,
#             erp.guild_id,
#         )

#     # Insert active pair data
#     for aerp in aerp_mock:
#         pair_id = create_hash(
#             aerp.role_id,
#             aerp.emoji_name,
#         )

#         await add_active_pair(
#             pool,
#             aerp.id,
#             pair_id,
#             aerp.message_id,
#             aerp.channel_id,
#             aerp.guild_id,
#         )

#     for aerp in aerp_mock:
#         pair_id = create_hash(
#             aerp.role_id,
#             aerp.emoji_name,
#         )

#         await delete_active_pair(
#             pool,
#             aerp.id,
#             aerp.message_id,
#             aerp.channel_id,
#             aerp.guild_id,
#         )

#     records = await fetch_all_active_pairs(pool, GUILD_ID)
#     assert len(records) == 0


@pytest.mark.asyncio
async def test_caching_fetched_pairs(pool, aio_benchmark):
    # Insert pair data
    erp_mock = get_mock_pair_list()

    for erp in erp_mock:

        await add_pair(
            pool,
            erp.id,
            erp.role_id,
            erp.emoji_id,
            erp.emoji_name,
            erp.is_animated,
            erp.guild_id,
        )

    @aio_benchmark
    async def _benchmarks():
        for _ in range(1000):
            await fetch_all_pairs(pool, GUILD_ID)

        for _ in range(1000):
            await fetch_pair(pool, erp_mock[0].id, GUILD_ID)


@pytest.mark.asyncio
async def test_caching_fetched_active_pairs(pool, aio_benchmark):
    erp_mock = get_mock_pair_list()
    aerp_mock = get_mock_active_pair_list()

    for erp in erp_mock:

        await add_pair(
            pool,
            erp.id,
            erp.role_id,
            erp.emoji_id,
            erp.emoji_name,
            erp.is_animated,
            erp.guild_id,
        )

    # Insert active pair data
    for aerp in aerp_mock:
        pair_id = create_hash(
            aerp.role_id,
            aerp.emoji_name,
        )

        await add_active_pair(
            pool,
            aerp.id,
            pair_id,
            aerp.message_id,
            aerp.channel_id,
            aerp.guild_id,
        )

    @aio_benchmark
    async def _benchmarks():
        for _ in range(1000):
            await fetch_all_active_pairs_by_message(pool, aerp_mock[0].message_id, GUILD_ID)
