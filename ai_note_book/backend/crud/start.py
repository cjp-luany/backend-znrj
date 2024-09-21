import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastcrud import FastCRUD, crud_router
from sqlalchemy.ext.asyncio import AsyncSession

import service.calendar
import service.chat
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

""" RECORD MODEL """
# CRUD operations setup
crud_record = FastCRUD(RecordItem)

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

""" IMAGE MODEL """
crud_image = FastCRUD(ImageItem)

image_item_router = crud_router(
    session=get_session,
    model=ImageItem,
    create_schema=ImageItemCreateSchema,
    update_schema=ImageItemUpdateSchema,
    path="/api/image",
    tags=["ImageItem"]
)

api.include_router(image_item_router)

""" customize async methods """


@api.get("/weekItems", summary="获取一周内每一天的任务数据", tags=["Calendar"])
async def week_items(db: AsyncSession = Depends(get_session)):
    return await service.calendar.week_items(db)


@api.get("/monthItems/{year_month}", summary="获取一月内每一天的任务数据", tags=["Calendar"])
async def month_items(year_month: str, db: AsyncSession = Depends(get_session)):
    return await service.calendar.month_items(year_month, db)


@api.get("/monthTodoItems/{year_month}", summary="获取所有任务数据", tags=["Calendar"])
async def month_todo_items(year_month: str, db: AsyncSession = Depends(get_session)):
    return await service.calendar.month_todo_items(year_month, db)


@api.post("/uploadOneImage", summary="图像识别，输入图像，输出图像的文字描述，并保存图片", tags=["Mllm"])
async def recognize_one_image(item: service.mllm.UploadImageItem, db: AsyncSession = Depends(get_session)):
    return await service.mllm.recognize_one_image(item, db)


@api.post("/speech_asr", summary="语音识别，输入音频文件，输出文字描述", tags=["Mllm"])
async def speech_asr(item: service.mllm.SpeechAsrModel):
    return await service.mllm.speech_asr(item)


@api.get("/speech_tts", summary="语音合成，输入文字描述，输出语音文件", tags=["Mllm"])
async def speech_tts(text: str, voice: str = "alloy"):
    return await service.mllm.speech_tts(text, voice)


""" customize sync methods """


@api.post("/query", summary="大模型对话接口，输入文字描述，输出大模型回复", tags=["Chat"])
def start_loop(query_value: service.chat.Query):
    return service.chat.start_loop(query_value)


@api.get("/get_lat_longit", summary="获取全局变量中储存的经纬度", tags=["Chat"])
def get_lat_longit_value():
    return service.chat.get_lat_longit_value()


@api.get("/get_user_id", summary="获取全局变量中储存的用户ID", tags=["Chat"])
def get_user_id():
    return service.chat.get_user_id()


# 启动fastapi
def start():
    import uvicorn
    yaml_contents = read_yaml_files(CUR_DIR)

    if "server" in yaml_contents and "port" in yaml_contents["server"]:
        port = yaml_contents["server"]["port"]
        uvicorn.run(api, host="0.0.0.0", port=port, loop="asyncio")
