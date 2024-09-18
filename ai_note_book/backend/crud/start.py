import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastcrud import FastCRUD, crud_router
from sqlalchemy.ext.asyncio import AsyncSession

import service.calendar
import service.mllm
from crud.models import lifespan, RecordItem, ImageItem, get_session, RecordItemCreateSchema, \
    RecordItemUpdateSchema, ImageItemCreateSchema, ImageItemUpdateSchema
from utils.config import read_yaml_files

CUR_DIR = os.path.realpath(os.path.dirname(__file__))

api = FastAPI(lifespan=lifespan)

# cors名单
origins = [
    "*",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://127.0.0.1:6200",
    "http://localhost:6200"
]

# cors中间件
api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CRUD operations setup
crud_record = FastCRUD(RecordItem)
crud_image = FastCRUD(ImageItem)

# CRUD router setup
record_item_router = crud_router(
    session=get_session,
    model=RecordItem,
    create_schema=RecordItemCreateSchema,
    update_schema=RecordItemUpdateSchema,
    path="/api/record",
    tags=["RecordItem"]
)

api.include_router(record_item_router)

image_item_router = crud_router(
    session=get_session,
    model=ImageItem,
    create_schema=ImageItemCreateSchema,
    update_schema=ImageItemUpdateSchema,
    path="/api/image",
    tags=["ImageItem"]
)

api.include_router(image_item_router)


@api.get("/weekItems/")
async def week_items(db: AsyncSession = Depends(get_session)):
    return await service.calendar.week_items(db)


@api.get("/monthItems/{year_month}/")
async def month_items(year_month: str, db: AsyncSession = Depends(get_session)):
    return await service.calendar.month_items(year_month, db)


@api.get("/monthTodoItems/{year_month}/")
async def month_todo_items(year_month: str, db: AsyncSession = Depends(get_session)):
    return await service.calendar.month_items(year_month, db)


@api.post("/uploadOneImage/")
async def recognize_one_image(item: service.mllm.UploadImageItem, db: AsyncSession = Depends(get_session)):
    return await service.mllm.recognize_one_image(item, db)


@api.post("/speech_asr/")
async def speech_asr(item: service.mllm.SpeechAsrModel):
    return await service.mllm.speech_asr(item)


@api.get("/speech_tts/")
async def speech_tts(text: str, voice: str = "alloy"):
    return await service.mllm.speech_tts(text, voice)


# 启动fastapi
def start():
    import uvicorn
    yaml_contents = read_yaml_files(CUR_DIR)

    if "server" in yaml_contents and "port" in yaml_contents["server"]:
        port = yaml_contents["server"]["port"]
        uvicorn.run(api, host="0.0.0.0", port=port, loop="asyncio")
