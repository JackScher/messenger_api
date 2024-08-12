from .core import CoreSchema


class LoginRequestSchema(CoreSchema):
    email: str
    password: str


class RegisterRequestSchema(LoginRequestSchema):
    first_name: str | None
    last_name: str | None
    username: str


class LoginResponseSchema(CoreSchema):
    access_token: str


class RegisterResponseSchema(CoreSchema):
    username: str
    user_uuid: str
