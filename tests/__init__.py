from ena.database import EnaDatabase
import asyncio

enadb = EnaDatabase(dsn="postgresql://postgres:jmapb0111@localhost:5432/enabot2", schema="db/schema.psql")


async def main():

    await enadb.connect()

    await enadb.fetch("SELECT * FROM emoji_role_pairs")


asyncio.run(main())
