import asyncio
import asyncpg
import os
import dotenv
import pytest
import logging

from ena.helpers import create_hash
from ena.cache import clear_all

from plugins.react_role.models import EmojiRolePair
from plugins.react_role.controller import add_pair, delete_pair, fetch_all_pairs_by_guild, fetch_pair

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


@pytest.fixture
def event_loop():
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    res = policy.new_event_loop()
    asyncio.set_event_loop(res)
    res._close = res.close
    res.close = lambda: None

    yield res

    res._close()


@pytest.fixture
def pool(event_loop):
    async def get_pool():
        pool = await asyncpg.create_pool(os.getenv("TEST_DB_STRING"))
        return pool

    return event_loop.run_until_complete(get_pool())


@pytest.mark.asyncio
async def test_create_schema(pool):

    conn: asyncpg.Connection

    async with pool.acquire() as conn:

        with open("db/schema.psql", "r") as schema:

            await conn.execute(schema.read())


@pytest.mark.asyncio
async def test_setup(pool):

    conn: asyncpg.Connection
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO guilds VALUES ($1) ON CONFLICT DO NOTHING", GUILD_ID)


# TESTS ON REACTION ROLE PLUGIN CONTROLLERS


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
async def test_fetch_all_pairs(pool):

    pairs = await fetch_all_pairs_by_guild(pool, GUILD_ID)

    assert len(pairs) == 18

    assert len([pair for pair in pairs if pair["emoji_name"] == "koko_shy"]) == 3
    assert len([pair for pair in pairs if pair["emoji_name"] == "koko_fallen"]) == 3
    assert len([pair for pair in pairs if pair["emoji_name"] == "koko_fright"]) == 3

    assert len([pair for pair in pairs if pair["emoji_name"] == "koko_rage"]) == 3
    assert len([pair for pair in pairs if pair["emoji_name"] == "koko_chill"]) == 3
    assert len([pair for pair in pairs if pair["emoji_name"] == "koko_peek"]) == 3

    assert len([pair for pair in pairs if pair["is_animated"] is True]) == 9
    assert len([pair for pair in pairs if pair["is_animated"] is False]) == 9


@pytest.mark.asyncio
async def test_cache(pool):
    await clear_all()  # clear all cache

    pairs = await fetch_all_pairs_by_guild(pool, GUILD_ID)

    assert len(pairs) == 18

    sample_row = get_mock_pair_list()[0]

    await delete_pair(pool, id=sample_row.id, guild_id=GUILD_ID)  # delete a single item to trigger evict method

    pairs = await fetch_all_pairs_by_guild(pool, GUILD_ID)

    assert len(pairs) == 17

    await add_pair(
        pool,
        sample_row.id,
        sample_row.role_id,
        sample_row.emoji_id,
        sample_row.emoji_name,
        sample_row.is_animated,
        sample_row.guild_id,
    )

    pairs = await fetch_all_pairs_by_guild(pool, GUILD_ID)
    assert len(pairs) == 18


@pytest.mark.asyncio
async def test_duplicate_pair(pool):
    for erp in get_mock_pair_list():

        with pytest.raises(asyncpg.exceptions.UniqueViolationError):
            await add_pair(
                pool,
                erp.id,
                erp.role_id,
                erp.emoji_id,
                erp.emoji_name,
                erp.is_animated,
                erp.guild_id,
            )


@pytest.mark.asyncio
async def test_delete_pair(pool):

    await clear_all()

    pairs = await fetch_all_pairs_by_guild(pool, GUILD_ID)
    assert len(pairs) == 18

    sample_row = get_mock_pair_list()[0]

    await delete_pair(pool, id=sample_row.id, guild_id=GUILD_ID)
    pairs = await fetch_all_pairs_by_guild(pool, GUILD_ID)

    assert len(pairs) == 17


@pytest.mark.asyncio
async def test_fetch_pair(pool):
    await clear_all()
    mock_pair = get_mock_pair_list()[15]

    record = await fetch_pair(pool, mock_pair.id, mock_pair.guild_id)

    erp = EmojiRolePair.from_dict(record)

    assert isinstance(erp.id, str)
    assert isinstance(erp.role_id, int)
    assert isinstance(erp.emoji_id, int)
    assert isinstance(erp.emoji_name, str)
    assert isinstance(erp.is_animated, bool)
    assert isinstance(erp.guild_id, int)
