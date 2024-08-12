from .core import CoreSchema


class BaseCommentRequestSchema(CoreSchema):
    comment_uuid: str
    

class CommentCreateRequestSchema(CoreSchema):
    body: str
    parent_uuid: str | None = None
    post_uuid: str | None = None


class CommentUpdateSchema(CoreSchema):
    body: str
    comment_uuid: str


class CommentsRequestSchema(CoreSchema):
    user_uuid: str | None = None
    post_uuid: str | None = None
    comment_uuid: str | None = None


class CommentsDailyBreakdownRequestSchema(CoreSchema):
    date_from: str
    date_to: str


class CommentsDailyBreakdownResponseSchema(CoreSchema):
    created: int
    blocked: int
