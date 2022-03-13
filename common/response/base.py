import json

from aiohttp import web


def json_response(*args, **kwargs):
    kwargs['dumps'] = json.JSONEncoder(ensure_ascii=False).encode
    return web.json_response(*args, **kwargs)
