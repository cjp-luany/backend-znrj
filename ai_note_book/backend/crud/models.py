import os
import uuid
from datetime import datetime
from typing import AsyncGenerator

from databases import Database
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, \
    Boolean, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from utils.random import get_key

CUR_DIR = os.path.realpath(os.path.dirname(__file__))
PARENT_DIR = os.path.dirname(CUR_DIR)
JOIN_DIR = os.path.join(PARENT_DIR, "sqlite.db")
DATABASE_URL = "sqlite+aiosqlite:///" + JOIN_DIR

database = Database(DATABASE_URL)  # https://pypi.org/project/databases/ 参考database的使用方法

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Database session dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


# Create tables before the app start
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


class Base(DeclarativeBase):
    pass


class RecordItem(Base):
    __tablename__ = 'record'
    record_id = Column(String, primary_key=True)
    record_time = Column(DateTime)
    record_location_name = Column(String)
    record_location = Column(String)
    record_cls = Column(String, nullable=True)
    target_time = Column(DateTime, nullable=True)
    finish_time = Column(DateTime, nullable=True)
    wake_time = Column(DateTime, nullable=True)
    record_descrpt = Column(String, default="")
    record_status = Column(String)
    image_descrpt = Column(String, default="", nullable=True)
    image_id = Column(String, default="", nullable=True)
    user_id = Column(String)

    @staticmethod
    def set_default(mapper, connection, target):
        if target.record_id is None:
            target.record_id = str(uuid.uuid4())  # python_get_now_timespan
        if target.finish_time == "":
            target.finish_time = None


event.listen(RecordItem, 'before_insert', RecordItem.set_default)


class RecordItemCreateSchema(BaseModel):
    record_time: datetime
    record_location_name: str
    record_location: str
    record_cls: str
    target_time: datetime
    finish_time: datetime | str
    wake_time: datetime
    record_descrpt: str
    record_status: str
    image_descrpt: str | None = None
    image_id: str | None = None
    user_id: str


class RecordItemUpdateSchema(BaseModel):
    record_time: datetime | None = None
    record_location_name: str | None = None
    record_location: str | None = None
    record_cls: str | None = None
    target_time: datetime | None = None
    finish_time: datetime | None = None
    wake_time: datetime | None = None
    record_descrpt: str | None = None
    record_status: str | None = None
    image_descrpt: str | None = None
    image_id: str | None = None
    user_id: str | None = None


class ImageItem(Base):
    __tablename__ = 'images'
    id = Column(String, primary_key=True)
    image_descrpt = Column(String, default="")
    image_code = Column(String, default="")

    @staticmethod
    def set_default_id(mapper, connection, target):
        if target.id is None:
            target.id = str(uuid.uuid4())  # python_get_now_timespan


event.listen(ImageItem, 'before_insert', ImageItem.set_default_id)


class ImageItemCreateSchema(BaseModel):
    id: str
    image_descrpt: str
    image_code: str

    def __init__(self, id: str, image_descrpt: str, image_code: str):
        super().__init__(id=id, image_descrpt=image_descrpt, image_code=image_code)


class ImageItemUpdateSchema(BaseModel):
    image_descrpt: str
    image_code: str



class UserItem(Base):
    __tablename__ = 'user_data'
    user_id = Column(String, primary_key=True)
    user_creation_time = Column(DateTime)
    user_name = Column(String)
    user_phone = Column(String)
    user_status = Column(Boolean)


class UserItemCreateSchema(BaseModel):
    user_id: str
    user_creation_time: datetime
    user_name: str
    user_phone: str
    user_status: bool


class UserItemUpdateSchema(BaseModel):
    user_id: str
    user_creation_time: datetime
    user_name: str
    user_phone: str
    user_status: bool
