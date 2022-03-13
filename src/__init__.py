from aiohttp import web

from common.apispec.base import setup_aiohttp_apispec
from common.db import configure_db
from common.redis import get_client

from src.handlers.image_uploader import IUCollection
from src.handlers.infra import InfraCollection
from migrations.create_tables import IMAGES_QUERY

from .config import SERVER, DATABASE_SETTINGS, REDIS_SETTINGS

__all__ = ['run_server']


def run_server():
    async def _setup_db():
        db = await configure_db(DATABASE_SETTINGS)
        await get_client(REDIS_SETTINGS)

        async with db.acquire() as conn:
            await conn.execute(IMAGES_QUERY)

        return await _setup()

    async def _setup():
        return await setup_app()

    web.run_app(_setup_db(), port=SERVER['IU_SERVER_PORT'], host=SERVER['IU_SERVER_HOST'])


async def setup_app() -> web.Application:
    app = web.Application()

    infra_handlers = InfraCollection()

    app.add_routes(
        [
            web.get('/ping', infra_handlers.ping, allow_head=False),
        ]
    )

    app.add_subapp('/api/', await setup_api_app())

    setup_aiohttp_apispec(
        app=app,
        title="Image Uploader API",
        version="v1",
        url="/docs/swagger.json",
        swagger_path="/docs",
    )

    return app


async def setup_api_app() -> web.Application:
    api = web.Application()

    iu_handlers = IUCollection()

    api.add_routes(
        [
            web.post('/upload', iu_handlers.upload),
            web.get('/get', iu_handlers.get, allow_head=True)
        ]
    )

    return api
