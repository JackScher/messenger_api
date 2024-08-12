from .core import CoreSchema


class ResponseSchema(CoreSchema):
    title: str | None = None
    description: str | None = None
    body: str
    created_at: str
    uuid: str
