import os
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
    id = Column(String, primary_key=True)
    record_time = Column(DateTime)
    record_location_name = Column(String)
    record_location = Column(String)
    target_time = Column(DateTime)
    target_location_name = Column(String)
    target_location = Column(String)
    finish_time = Column(DateTime)
    wake_time = Column(DateTime)
    wake_location_name = Column(String)
    wake_location = Column(String)
    record_descrpt = Column(String, default="")
    record_status = Column(Boolean, default=0)
    image_descrpt = Column(String, default="")
    image_id = Column(String, default="")

    @staticmethod
    def set_default_id(mapper, connection, target):
        if target.id is None:
            target.id = get_key()  # python_get_now_timespan


event.listen(RecordItem, 'before_insert', RecordItem.set_default_id)


class RecordItemCreateSchema(BaseModel):
    record_time: datetime
    record_location_name: str
    record_location: str
    target_time: datetime
    target_location_name: str
    target_location: str
    finish_time: datetime
    wake_time: datetime
    wake_location_name: str
    wake_location: str
    record_descrpt: str
    record_status: bool
    image_descrpt: str
    image_id: str


class RecordItemUpdateSchema(BaseModel):
    record_time: datetime
    record_location_name: str
    record_location: str
    target_time: datetime
    target_location_name: str
    target_location: str
    finish_time: datetime
    wake_time: datetime
    wake_location_name: str
    wake_location: str
    record_descrpt: str
    record_status: bool
    image_descrpt: str
    image_id: str


class ImageItem(Base):
    __tablename__ = 'images'
    id = Column(String, primary_key=True)
    image_descrpt = Column(String, default="")
    image_code = Column(String, default="")

    @staticmethod
    def set_default_id(mapper, connection, target):
        if target.id is None:
            target.id = get_key()  # python_get_now_timespan


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


# 上传图片模型
class UploadImageItem(BaseModel):
    img_base64: str


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
