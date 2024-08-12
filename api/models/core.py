from typing import Self
from datetime import datetime, UTC
from sqlalchemy import DateTime, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from ..database import db
from ..utils import generate_uuid


class CoreModel(db.Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(
        String(36),
        default=generate_uuid,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC),
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    def __str__(self) -> str:
        return str(self.uuid)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.uuid}"

    def delete(self) -> None:
        if not self.is_deleted:
            self.is_deleted = True
            self.save()

    def restore(self) -> None:
        if self.is_deleted:
            self.is_deleted = False
            self.save()

    def save(self, commit=True) -> Self:
        db.session.add(self)
        if commit:
            db.session.commit()
        return self
