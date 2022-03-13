from marshmallow import Schema, fields


class GetImageParamsSchema(Schema):
    id = fields.String(required=True)
    scale = fields.Float(required=False)


class UploadImageResultSchema(Schema):
    id = fields.String(required=True)
    message = fields.String(required=False)


class UploadImageBodySchema(Schema):
    image = fields.Raw(type='file')
