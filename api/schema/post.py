from .core import CoreSchema


class PostRequestSchema(CoreSchema):
    post_uuid: str


class AllPostsRequestSchema(CoreSchema):
    user_uuid: str | None = None


class PostCreateRequestSchema(CoreSchema):
    body: str
    title: str
    description: str


class PostUpdateRequestSchema(PostRequestSchema):
    body: str | None = None
    title: str | None = None
    description: str | None = None
