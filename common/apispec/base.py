from aiohttp import web
from aiohttp_apispec import AiohttpApiSpec


def enum_to_properties(self, field, **kwargs):
    import marshmallow_enum
    if isinstance(field, marshmallow_enum.EnumField):
        return {'type': 'string', 'enum': [m.name for m in field.enum]}
    return {}


def setup_aiohttp_apispec(
        app: web.Application,
        *,
        title: str = "API documentation",
        version: str = "0.0.1",
        url: str = "/api/docs/swagger.json",
        request_data_name: str = "data",
        swagger_path: str = None,
        static_path: str = '/static/swagger',
        error_callback=None,
        in_place: bool = False,
        prefix: str = '',
        **kwargs
) -> None:
    spec = AiohttpApiSpec(
        url,
        app,
        request_data_name,
        title=title,
        version=version,
        swagger_path=swagger_path,
        static_path=static_path,
        error_callback=error_callback,
        in_place=in_place,
        prefix=prefix,
        **kwargs
    )
    spec.plugin.converter.add_attribute_function(enum_to_properties)
