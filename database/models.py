from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base, engine


class Access_token(Base):
    __tablename__ = 'access_token'

    id = Column(Integer, autoincrement=True, primary_key=True)
    access_token = Column(String, nullable=False)


class Refresh_token(Base):
    __tablename__ = 'refresh_token'

    id = Column(Integer, autoincrement=True, primary_key=True)
    refresh_token = Column(String, nullable=False)



