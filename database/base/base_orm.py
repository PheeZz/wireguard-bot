from sqlalchemy.orm import DeclarativeBase


class BaseOrm(DeclarativeBase):
    # __table_args__ = {"schema": "public"}
    pass
