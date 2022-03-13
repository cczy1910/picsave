from aiomysql.sa import create_engine

from common.exit_util import safe_exit

db = None


async def configure_db(cfg: dict[str]):
    global db
    if db is not None:
        return db

    try:
        db = await create_engine(**cfg)
        return db
    except Exception as e:
        safe_exit(f'Unable to connect to MySQL database: {str(e)}')
