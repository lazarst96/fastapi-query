from datetime import datetime
from typing import Optional, List

from sqlalchemy import Table, Column, ForeignKey, func, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )


user_tag_association_table = Table(
    "users__tags",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("users.id"),
        primary_key=True
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id"),
        primary_key=True
    ),
)

paper_tag_association_table = Table(
    "paper__tags",
    Base.metadata,
    Column(
        "paper_id",
        ForeignKey("papers.id"),
        primary_key=True
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id"),
        primary_key=True
    ),
)


class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    papers: Mapped[List['Paper']] = relationship(
        secondary=paper_tag_association_table,
        lazy="noload",
        back_populates='tags'
    )


class Address(Base):
    __tablename__ = 'addresses'
    id: Mapped[int] = mapped_column(primary_key=True)
    line_1: Mapped[str]
    line_2: Mapped[Optional[str]]
    city: Mapped[str]
    state: Mapped[Optional[str]]
    country: Mapped[str]
    zip_code: Mapped[str]


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]

    shipping_address_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("addresses.id")
    )

    billing_address_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("addresses.id")
    )

    tags: Mapped[List[Tag]] = relationship(
        secondary=user_tag_association_table,
        lazy="noload"
    )

    papers: Mapped[List['Paper']] = relationship(
        lazy="noload",
        back_populates='author'
    )

    shipping_address: Mapped[Optional[Address]] = relationship(
        foreign_keys=[shipping_address_id]
    )

    billing_address: Mapped[Optional[Address]] = relationship(
        foreign_keys=[billing_address_id]
    )

    @hybrid_property
    def full_name(self) -> str:
        return self.first_name + " " + self.last_name

    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted_at != None  # noqa


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="users.id",
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        index=True
    )

    author: Mapped[User] = relationship(
        lazy='noload',
        back_populates='papers'
    )

    tags: Mapped[List[Tag]] = relationship(
        secondary=paper_tag_association_table,
        lazy="noload",
        back_populates='papers'
    )
