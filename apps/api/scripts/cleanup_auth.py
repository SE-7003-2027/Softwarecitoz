import asyncio

from src import database
from src.auth.service import cleanup_expired


async def main() -> None:
    await database.connect()
    try:
        await cleanup_expired()
    finally:
        await database.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
