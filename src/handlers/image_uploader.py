from aiohttp import web
from aiohttp_apispec import docs, querystring_schema, form_schema

from marshmallow import EXCLUDE
from marshmallow.exceptions import ValidationError

from common.consts.base import JPG_CONTENT_TYPE, FORM_DATA_CONTENT_TYPE, PLAIN_TEXT_CONTENT_TYPE
from common.image_utils import process_image_headers
from common.logging.base import get_logger
from common.response import json_response
from src.procedures import image_uploader
from src.handlers.schemas.image import GetImageParamsSchema, UploadImageResultSchema, UploadImageBodySchema

LOGGER = get_logger()


class IUCollection:
    @staticmethod
    @docs(
        tags=["uploader"],
        summary="Upload",
        description="Uploads provided JPG-image to the database",
        responses={
            200: {
                'schema': UploadImageResultSchema(),
                'description': 'Ok'
            },
            400: {
                'description': 'Bad Request'
            },
            401: {
                'description': 'Unauthorized'
            },
            403: {
                'description': 'Forbidden'
            },
            405: {
                'description': 'Method Not Allowed'
            },
            500: {
                'description': 'Server Error'
            }
        },
    )
    @form_schema(UploadImageBodySchema())
    async def upload(request: web.Request):
        if request.content_type not in (JPG_CONTENT_TYPE, FORM_DATA_CONTENT_TYPE, PLAIN_TEXT_CONTENT_TYPE):
            LOGGER.debug(f'Tried content type: {request.content_type}')
            return json_response(data={'status_code': 405, 'message': 'Only JPEG images are allowed'})

        image_blob = await request.read()
        if request.content_type != JPG_CONTENT_TYPE:
            image_blob = process_image_headers(image_blob)

        p_hash, message = await image_uploader.upload(bytes(image_blob))

        if p_hash is None:
            return json_response(data={'status_code': 500, 'message': message})
        elif message is not None:
            return json_response(
                data=UploadImageResultSchema().dump(
                    {
                        'id': str(p_hash),
                        'message': message,
                    }
                )
            )
        else:
            return json_response(
                data=UploadImageResultSchema().dump(
                    {
                        'id': str(p_hash),
                        'message': 'Ok',
                    }
                )
            )

    @staticmethod
    @docs(
        tags=["getter"],
        summary="Get",
        description="Get JPG-image by it's indentifier",
        responses={
            200: {
                'description': 'Ok'
            },
            400: {
                'description': 'Bad Request'
            },
            401: {
                'description': 'Unauthorized'
            },
            403: {
                'description': 'Forbidden'
            },
            405: {
                'description': 'Method Not Allowed'
            },
            500: {
                'description': 'Server Error'
            }
        },
    )
    @querystring_schema(GetImageParamsSchema())
    async def get(request: web.Request):
        try:
            params = GetImageParamsSchema().load(
                request.query, unknown=EXCLUDE
            )
        except ValidationError as e:
            return json_response(data={'status_code': 400, 'message': str(e)})

        image_id = params.get('id')
        scale = params.get('scale', 1)
        if scale <= 0:
            return json_response(data={'status_code': 400, 'message': 'Scale should be positive floating point number'})

        result = await image_uploader.get(image_id, scale)

        if result is None:
            return json_response(
                data={
                    'status_code': 404,
                    'message': f'Image with id equal to \'{image_id}\' was not found '
                               f'or could not be scaled because of too big scale'
                }
            )
        else:
            return web.Response(status=200, content_type=JPG_CONTENT_TYPE, body=result)
