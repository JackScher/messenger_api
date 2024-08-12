from typing import Self
from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import CoreModel
from api.banwords import BANWORDS


class Post(CoreModel):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship( # type: ignore
        "User",
        back_populates="posts",
    )

    comments: Mapped[list["Comment"]] = relationship( # type: ignore
        "Comment",
        back_populates="post",
    )

    def save(self, commit=True) -> Self:
        for word in BANWORDS:
            if word in self.title.lower() or word in self.description.lower() or word in self.body.lower():
                self.is_deleted=True
        return super().save(commit=True)
