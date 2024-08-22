import os
import time
import asyncio
import json
import httpx
import socket
from flask import Flask, render_template, send_from_directory
from threading import Thread

from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, AsyncGenerator

import nest_asyncio
from databases import Database
from fastapi.middleware.cors import CORSMiddleware
from fastcrud import crud_router, FastCRUD
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, desc, text, Column, Integer, String, BigInteger, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from fastapi import Depends, FastAPI, HTTPException, Request, Response
import requests

from api import run_fastapi2

# 加载当前目录下的 .env 文件
load_dotenv()
nest_asyncio.apply()


DEBUG = True
MAX_RESULT_SIZE = 1000
ROWS_PER_PAGE = 50
SECRET_KEY = '123456FLASK'

# 数据库连接
CUR_DIR = os.path.realpath(os.path.dirname(__file__))
JOIN_DIR = os.path.join(CUR_DIR, "sqlite.db")
DATABASE_URL = "sqlite:///" + JOIN_DIR  # 这里的路径应该是你的数据库文件的路径
# DATABASE_URL = "sqlite:///sqlite.db" # 这里的路径应该是你的数据库文件的路径

database = Database(DATABASE_URL)  # https://pypi.org/project/databases/ 参考database的使用方法

# engine = create_async_engine(DATABASE_URL, echo=True)
engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData()
metadata.create_all(engine)

api = FastAPI()



'''
    server url
    anything-llm token
    israg-workspace name
    norag-workspace name
'''
# SERVER_URL = "localhost"
SERVER_URL = "47.115.151.97"
# AnythingLLM_TOKEN = "7VAHKHX-N434531-P33SCGE-QBNHSGJ" # this is localhost anything llm token
AnythingLLM_TOKEN = "A6WW35F-A6RMWBH-PWRQJV3-5DT5DYS" # this is server anything llm token
ISRAG_WORKSPACE_NAME = "israg"
NORAG_WORKSPACE_NAME = "norag"





def python_get_now_timespan():
    return int(time.time())


# 数据库连接开启
@api.on_event("startup")
def startup():
    database.connect()


# 数据库连接关闭
@api.on_event("shutdown")
def shutdown():
    database.disconnect()


rec_data = Table("record", metadata, autoload_with=engine)

responses_query = {}


async def read_data_rec(query_msg:str):
    """
     # do sql select and upload to embed database
     # use anything llm api to query
     """

    """ ========== do sql select ========== """
    query = rec_data.select().order_by(desc(rec_data.c.id))
    result = await database.fetch_all(query)
    result = list(map(lambda x: {
        "id": x['id'],
        "rag_record": x['rag_record']
    }, result))

    """ ========== upload to embed database ========== """
    # 将列表转换为字符串，每个元素用逗号分隔
    list_str = json.dumps(result, indent=4)

    # 将字符串写入 TXT 文件
    with open('output.txt', 'w') as f:
        f.write(list_str)
    file_path = 'output.txt'

    # 设置目标 URL
    url = f'http://{SERVER_URL}:3001/api/v1/document/upload'

    # 设置请求头
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {AnythingLLM_TOKEN}'
    }

    # 设置要上传的文件
    file_path = 'output.txt'
    files = {
        'file': ('output.txt', open(file_path, 'rb'), 'text/plain')  # 模拟 curl 中的 -F 方式
    }
    file_server_location = ""

    # 发送 POST 请求
    try:
        response = requests.post(url, headers=headers, files=files)

        # 检查返回的状态
        if response.status_code == 200:
            print("文件上传成功:")
            print("服务器返回的响应:", response.json())  # 假设响应是 JSON 格式
            file_server_location = response.json()["documents"][0]["location"]
        else:
            print("文件上传失败，状态码:", response.status_code)
            print("响应内容:", response.text)

    except Exception as e:
        print("发生错误:", str(e))
    finally:
        # 确保在完成后关闭文件
        files['file'][1].close()

    if file_server_location :

        # 设置目标 URL
        url = f'http://{SERVER_URL}:3001/api/v1/workspace/{ISRAG_WORKSPACE_NAME}/update-embeddings'

        # 设置请求头
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {AnythingLLM_TOKEN}',
            'Content-Type': 'application/json'
        }

        # 设置要发送的数据
        data = {
            "adds": [
                file_server_location
            ]
        }

        # 发送 POST 请求
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))

            # 检查返回的状态
            if response.status_code == 200:
                print("更新嵌入成功:")
                print("服务器返回的响应:", response.json())  # 假设响应是 JSON 格式
            else:
                print("更新嵌入失败，状态码:", response.status_code)
                print("响应内容:", response.text)

        except requests.exceptions.RequestException as e:
            print("请求异常:", e)

    """ ==========  use anything llm api to query ========== """

    # 设置目标 URL
    url = f'http://{SERVER_URL}:3001/api/v1/workspace/{ISRAG_WORKSPACE_NAME}/chat'

    # 设置请求头
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {AnythingLLM_TOKEN}',
        'Content-Type': 'application/json'
    }

    # 设置要发送的数据
    data = {
        "message": query_msg,
        "mode": "query"
    }

    # 发送 POST 请求
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))

        # 检查返回的状态
        if response.status_code == 200:
            print("请求成功:")
            print("服务器返回的响应:", response.json())  # 假设响应是 JSON 格式
        else:
            print("请求失败，状态码:", response.status_code)
            print("响应内容:", response.text)

    except requests.exceptions.RequestException as e:
        print("请求异常:", e)


    # async with httpx.AsyncClient() as client_h:
    #     response = client_h.post(url, json=json_payload, headers=headers, timeout=None)

    # http://localhost:3001/api/v1/document/upload
    #   -H 'accept: application/json' \
    #   -H 'Authorization: Bearer 7VAHKHX-N434531-P33SCGE-QBNHSGJ' \
    #   -H 'Content-Type: multipart/form-data' \
    #   -F 'file=@output2.txt;type=text/plain'
    # {
    #     "success": true,
    #     "error": null,
    #     "documents": [
    #         {
    #             "id": "7de0d60e-ad4c-4f3e-8887-a8ac26e98fd1",
    #             "url": "file:///Users/us/Library/Application Support/anythingllm-desktop/storage/hotdir/output2.txt",
    #             "title": "output2.txt",
    #             "docAuthor": "Unknown",
    #             "description": "Unknown",
    #             "docSource": "a text file uploaded by the user.",
    #             "chunkSource": "",
    #             "published": "2024/8/8 01:07:14",
    #             "wordCount": 27,
    #             "pageContent": "[\n    {\n        \"id\": 1723039277,\n        \"rag_record\": \"string\"\n    }\n]",
    #             "token_count_estimate": 24,
    #             "location": "custom-documents/output2.txt-7de0d60e-ad4c-4f3e-8887-a8ac26e98fd1.json"
    #         }
    #     ]
    #
    # }
    #
    # http://localhost:3001/api/v1/workspace/is-rag/update-embeddings
    # {
    #     "adds": [
    #         "custom-documents/output2.txt-7de0d60e-ad4c-4f3e-8887-a8ac26e98fd1.json"
    #     ]
    # }





# 进行AI操作

client = OpenAI()


# Load the system message from a file
with open(os.path.join(CUR_DIR, "prompt/tools.txt"), 'r', encoding='utf-8') as file:
    system_message_content = file.read()


def chat(message_content, chat_history=[]):
    # query_during_chat() # 对话中查询，使用服务器rag


    message = {"role": "user", "content": message_content}
    chat_history.append(message)

    # 调用GPT-3模型
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=chat_history,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
        tools=[{
            "type": "function",
            "function": {
                "name": "http_query",
                "description": "use web interface to query some data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": f"""
                                    SQL insert for save user input.
                                    SQL should be written using this database schema:
                                    {database_schema_string}
                                    The insert should be returned in plain text, not in JSON.
                                    The insert should only contain grammars supported by SQLite.
                                    """,
                        }
                    },
                    "required": ["query"],
                }
            }
        }],
        # 返回消息的格式，text 或 json_object
        response_format={"type": "text"},
    )
    print(response.choices[0].message.content)
    chat_history.append(response.choices[0].message)

    # Check if 'record' is in user message
    if 'record' in message_content.lower():
        print("Record Function Called")
        record(message['content'])

    return chat_history


database_schema_string = "aaa"


def record(content):
    # 在此处进行你的记录功能
    print(f"Recording content: {content}")


def start_loop():

    # Example use
    chat_history_1 = [
        {"role": "system", "content": system_message_content},
    ]

    while True:
        user_input = input("Enter message: ")
        chat_history_1 = chat(user_input, chat_history_1)


def query_during_chat():
    """
    # do sql select and upload to embed database
    # use anything llm api to query
    """

    try:
        loop = asyncio.get_event_loop()
    except Exception:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    ret = loop.run_until_complete(read_data_rec("what is string id"))

    print(ret)
    return


    # try:
    #     loop = asyncio.get_event_loop()
    # except Exception:
    #     loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)

    # loop.run_until_complete(query_select(url_1))

    # url_1 = "http://localhost:6200/api/record/get_multi"
    # async with httpx.AsyncClient() as client:
    #     response_1 = client.post(url, json=json_payload, headers=headers, timeout=None)
    #
    #
    #
    # my_payload = {
    #     "conversation": {
    #         "agent": "Ai Helper",
    #         "user": "message.message"
    #     },
    #     "system": {
    #         "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #         "loc": "116.338611,39.992552"
    #     }
    # }
    # json_payload = {
    #     "message": json.dumps(my_payload),
    #     "mode": "chat"
    # }
    # url = "http://localhost:3001/api/v1/workspace/norag/chat"  # 替换为实际的目标URL
    # bearer_token: str = "WM4CRFV-GFPMZRE-GM9FD7E-RGPWXJN"
    # headers = {}
    # if bearer_token:
    #     headers["Authorization"] = f"Bearer {bearer_token}"
    #
    # async with httpx.AsyncClient() as client:
    #     response = client.post(url, json=json_payload, headers=headers, timeout=None)
    #
    # if response.status_code != 200:
    #     raise HTTPException(status_code=response.status_code, detail="Failed to send message")








# 启动fastapi
def run_fastapi():
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=6200, loop="asyncio")


# cors名单
origins = [
    "*",
    "http://127.0.0.1:8102",
    "http://localhost:8102",
    "http://127.0.0.1:6102",
    "http://127.0.0.1:6200"
    "http://127.0.0.1:6103",
    "http://127.0.0.1:6202",
    "http://127.0.0.1:6203",
    "http://localhost:6102",
    "http://localhost:6103",
    "http://localhost:6202",
    "http://localhost:6203"
]


# cors中间件
api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print('PyCharm')

    # 启动fastapi
    thread_fast = Thread(target=run_fastapi)
    thread_fast.start()

    thread_test = Thread(target=run_fastapi2)
    thread_test.start()

    # start_loop()


'''
是否使用flask
'''
# # 创建flask实例，指定静态文件夹
# app = Flask(__name__,
#             static_folder=os.path.join(CUR_DIR, 'static'),
#             template_folder=os.path.join(CUR_DIR, 'templates'))
# # 启动flask
# def run_flask():
#     app.run(host='0.0.0.0', port=6103)
#
# # 路由控制
# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def serve(path):
#     if path != "" and os.path.exists(app.static_folder + '/' + path):
#         return send_from_directory(app.static_folder, path)
#     else:
#         return send_from_directory(app.static_folder, 'index.html')