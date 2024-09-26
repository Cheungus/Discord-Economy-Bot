from Bot import client
from db.database import create_pool
from logs.logs import setup_logging
from keys.apikeys import BOTTOKEN
from rate_limit.rate_limit_func import check_rate_limit
import logging
import asyncio

async def main():
    await create_pool()
    await client.start(BOTTOKEN)

if __name__ == '__main__':
    setup_logging()
    try:
        asyncio.run(main())
        asyncio.run(check_rate_limit())
    except Exception as e:
        logging.exception("An error occured while running the bot.")

