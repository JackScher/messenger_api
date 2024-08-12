from typing import Self
from sqlalchemy import Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import CoreModel
from api.banwords import BANWORDS


class Comment(CoreModel):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(Text)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    # Foreign Keys
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))
    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="comments",
    )
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="comments",
    )
    answers: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="parent_comment",
    )
    parent_comment: Mapped["Comment"] = relationship(
        "Comment",
        back_populates="answers",
        remote_side=[id],
    )

    def save(self, commit=True) -> Self:
        for word in BANWORDS:
            if word in self.body.lower():
                self.is_blocked=True
        return super().save(commit=True)
