from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base
import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    refresh_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
