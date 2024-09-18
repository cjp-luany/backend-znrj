import os
from threading import Thread

from dotenv import dotenv_values
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastcrud import FastCRUD, crud_router

from backend.common.database import lifespan, RecordItem, ImageItem, get_session, RecordItemCreateSchema, \
    RecordItemUpdateSchema, ImageItemCreateSchema, ImageItemUpdateSchema

from backend.common.config import load_env, get_env_variable, read_yaml_files

"""
    main的主要作用：
        - 启动服务线程
        - 从环境配置获取服务的端口
        - 定义cors
        - 用fastcrud定义简单的基础接口
        - 提供api对象，给app下的python使用
        - 读取res下的资源文件，进行tests下的单元测试等
"""



# 加载服务1的环境配置
load_env(".env")

CUR_DIR = os.path.realpath(os.path.dirname(__file__))

api = FastAPI(lifespan=lifespan)


# 启动fastapi
def run_api():
    import uvicorn
    yaml_contents = read_yaml_files(CUR_DIR)

    port = 6202
    if "server" in yaml_contents and "port" in yaml_contents["server"]:
        port = yaml_contents["server"]["port"]

    uvicorn.run(api, host="0.0.0.0", port=port, loop="asyncio")


# cors名单
origins = [
    "*",
    "http://127.0.0.1:8102",
    "http://localhost:8102",
    "http://127.0.0.1:6102",
    "http://127.0.0.1:6201",
    "http://127.0.0.1:6200"
    "http://127.0.0.1:6103",
    "http://127.0.0.1:6202",
    "http://127.0.0.1:6203",
    "http://localhost:6102",
    "http://localhost:6103",
    "http://localhost:6202",
    "http://localhost:6203",
    "http://localhost:62065"
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

if __name__ == '__main__':
    thread_api = Thread(target=run_api)
    thread_api.start()
