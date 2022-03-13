from common.db import configure_db
from common.logging.base import get_logger
from common.redis import get_client, get_from_cache, set_to_cache
from src.config import DATABASE_SETTINGS, REDIS_SETTINGS
from src.db.models import ImagesTable

from common.image_utils import avg_hash, p_hash, scale_image, image_sizes

LOGGER = get_logger()


async def upload(image_blob: bytes):
    p_hash_id = p_hash(image_blob)
    avg_hash_id = avg_hash(image_blob)

    db = await configure_db(DATABASE_SETTINGS)

    async with db.acquire() as conn:
        try:
            await conn.execute(ImagesTable.insert().values(p_hash=p_hash_id, avg_hash=avg_hash_id, image=image_blob))
        except Exception as e:
            if 'Duplicate entry' in str(e) and 'PRIMARY' in str(e):
                is_phash = True
            elif 'Duplicate entry' in str(e):
                is_phash = False
            else:
                LOGGER.error(str(e))
                return None, 'The server is temporarily unavailable'

            image = (
                await __get_image_by_id(p_hash_id)
                if is_phash
                else await __get_image_by_avg_hash_id(avg_hash_id)
            )

            h1, w1 = image_sizes(image)
            h2, w2 = image_sizes(image_blob)

            if is_phash:
                info = 'phashes were equal'
            else:
                info = 'avg hashes were equal'

            if h2 > h1 and w2 > w1:
                LOGGER.info(f'Updated image with id \'{p_hash_id}\' from ({h1}, {w1}) to ({h2}, {w2}). Reason: {info}')
                if is_phash:
                    await conn.execute(
                        ImagesTable.update().where(ImagesTable.c.p_hash == p_hash_id).values(image=image_blob)
                    )
                else:
                    await conn.execute(
                        ImagesTable.update().where(ImagesTable.c.avg_hash == avg_hash_id).values(image=image_blob)
                    )
                    p_hash_id = await __get_p_hash_by_avg_hash_id(avg_hash_id)

                await conn._commit_impl()

                client = await get_client(REDIS_SETTINGS)
                await set_to_cache(client, p_hash_id, image_blob)

            LOGGER.info(f'Image already exists and stored with id - \'{p_hash_id}\'. {info}')
            return p_hash_id, f'Image already exists and stored with id - \'{p_hash_id}\'.'

        await conn._commit_impl()

    return p_hash_id, None


async def __get_image_by_id(image_id: str):
    db = await configure_db(DATABASE_SETTINGS)

    async with db.acquire() as conn:
        async for row in await conn.execute(ImagesTable.select().where(ImagesTable.c.p_hash == image_id)):
            return row.image
        return None


async def __get_image_by_avg_hash_id(avg_hash_id: str):
    db = await configure_db(DATABASE_SETTINGS)

    async with db.acquire() as conn:
        async for row in await conn.execute(ImagesTable.select().where(ImagesTable.c.avg_hash == avg_hash_id)):
            return row.image
        return None


async def __get_p_hash_by_avg_hash_id(avg_hash_id: str):
    db = await configure_db(DATABASE_SETTINGS)

    async with db.acquire() as conn:
        async for row in await conn.execute(ImagesTable.select().where(ImagesTable.c.avg_hash == avg_hash_id)):
            return row.p_hash
        return None


async def get(image_id: str, scale: float):
    client = await get_client(REDIS_SETTINGS)

    image = await get_from_cache(client, image_id)

    if image is not None:
        LOGGER.debug(f'Image with id \'{image_id}\' is loaded from cache')
        return scale_image(image, scale)

    image = await __get_image_by_id(image_id)
    if image is None:
        return None

    LOGGER.debug(f'Image with id \'{image_id}\' is loaded from database')

    await set_to_cache(client, image_id, image)

    return scale_image(image, scale)
