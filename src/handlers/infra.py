from aiohttp import web
from aiohttp_apispec import docs

from common.response import json_response


class InfraCollection:
    @staticmethod
    @docs(
        tags=["infra"],
        summary="Ping",
        description="Returns ok status if server is alive",
        responses={
            200: {
                'description': 'Ok'
            }
        }
    )
    async def ping(request: web.Request) -> web.Response:
        return json_response({'status': 'ok'})
