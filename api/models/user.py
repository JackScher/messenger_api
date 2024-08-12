from sqlalchemy import String, Boolean, Integer
from sqlalchemy. orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash

from .core import CoreModel


class User(CoreModel):
    __tablename__ = "users"

    first_name: Mapped[str | None] = mapped_column(String(64))
    last_name: Mapped[str | None] = mapped_column(String(64))
    username: Mapped[str] = mapped_column(String(64), unique=True)
    email: Mapped[str] = mapped_column(String(128), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256), default="")
    auto_reply_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_reply_delay: Mapped[int] = mapped_column(Integer, default=0) 

    # Relationships
    posts: Mapped[list["Post"]] = relationship( # type: ignore
        "Post",
        back_populates="user",
    )

    comments: Mapped[list["Comment"]] = relationship( # type: ignore
        "Comment",
        back_populates="user",
    )

    @property
    def password(self) -> None:
        return self.password_hash

    @password.setter
    def password(self, password) -> None:
        self.password_hash = generate_password_hash(password)
    
    def __repr__(self) -> str:
        return f"<{self.uuid}: {self.username}, {self.email}>"
    