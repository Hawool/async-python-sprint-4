from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from src.db.db import Base


class UrlModel(Base):
    __tablename__ = "url_model"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    url = Column(String(1024), nullable=False)
    number_of_transitions = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), index=True, server_default=func.now())
