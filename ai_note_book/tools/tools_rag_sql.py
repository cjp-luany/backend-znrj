import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import requests
import json
from typing import List, Dict
from api import RecordItem, run_fastapi2
from fastapi import Depends, FastAPI, HTTPException, Request, Response
# from geoalchemy2 import Geometry

# 数据库连接
# CUR_DIR = os.path.realpath(os.path.dirname(__file__))
# PARENT_DIR = os.path.dirname(CUR_DIR)
# JOIN_DIR = os.path.join(CUR_DIR, "sqlite.db")
# DATABASE_URL = "sqlite:///" + JOIN_DIR  # 这里的路径应该是你的数据库文件的路径
DATABASE_URL = "sqlite:///C://Users//Administrator//Desktop//ai_note_book//sqlite.db"
SERVER_URL = "47.115.151.97"
ANYTHINGLLM_TOKEN = "A6WW35F-A6RMWBH-PWRQJV3-5DT5DYS"  # this is server anything llm token
ISRAG_WORKSPACE_NAME = "israg"
NORAG_WORKSPACE_NAME = "norag"

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)
# 创建会话
Session = sessionmaker(bind=engine)
session = Session()
api = FastAPI()

# ========================数据库结构========================
database_schema_string = """
CREATE TABLE record (
    id STR PRIMARY KEY NOT NULL, -- 键值，11位大小写字母数字组成
    record_time DATETIME, -- [记录时间],格式为YYYY-MM-DD hh:mm:ss
    record_location_name STR, -- [记录地点],格式为STR
    record_location String, -- [记录坐标],格式为String:经度,纬度
    target_time DATETIME, -- [目标时间],格式为YYYY-MM-DD hh:mm:ss
    target_location_name STR, -- [目标地点],格式为STR
    target_location String, -- [目标坐标],格式为String:经度,纬度 
    finish_time DATETIME, -- [结束时间],格式为YYYY-MM-DD hh:mm:ss
    wake_time DATETIME, -- [提醒时间],格式为YYYY-MM-DD hh:mm:ss
    wake_location_name String, -- [提醒地点],格式为STR
    wake_location String, -- [提醒坐标],格式为String:经度,纬度 
    record_descrpt STR , -- [事件总结]
    record_status BOOLEAN -- [事件状态]，0为未完成，1为完成
    image_descrpt STR -- [图片描述]，如用户未提及则为Null
    image_id STR -- [图片ID]，如用户未提及则为Null
);
"""


# ========================rag工具========================
def fetch_all_records():
    """
    查询所有数据
    :return:
    """

    results = session.query(RecordItem).all()
    data_list = [record.__dict__ for record in results]
    return data_list


def save_data_to_file(data: List[Dict], filename: str) -> str:
    """将数据保存到文件中"""
    # 处理并筛选数据
    result = list(map(lambda x: {
        # "record_time": x['record_time'],
        "record_descrpt": x['record_descrpt']
    }, data))

    # 将结果转换为 JSON 字符串
    try:
        list_str = json.dumps(result, indent=4, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        print(f"Error converting to JSON: {e}")
        return ""

    # 将 JSON 字符串写入文件
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(list_str)
    except IOError as e:
        print(f"Error writing to file: {e}")
        return ""

    return filename


def upload_file_to_server(filepath: str) -> str:
    """将文件上传到服务器"""
    url = f"http://{SERVER_URL}:3001/api/v1/document/upload"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {ANYTHINGLLM_TOKEN}'
    }
    with open(filepath, 'rb') as file:
        files = {'file': (os.path.basename(filepath), file, 'text/plain')}
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        return response.json()["documents"][0]["location"]
    else:
        raise Exception(f"文件上传失败，状态码: {response.status_code}")


def update_embeddings_on_server(location: str):
    """更新服务器上的嵌入数据"""
    url = f"http://{SERVER_URL}:3001/api/v1/workspace/{ISRAG_WORKSPACE_NAME}/update-embeddings"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {ANYTHINGLLM_TOKEN}',
        'Content-Type': 'application/json'
    }
    _len = location.split("\\").__len__()
    _location_str = location.split("\\")[_len - 2] + "/" + location.split("\\")[_len - 1]
    data = {"adds": [_location_str]}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        raise Exception(f"更新嵌入失败，状态码: {response.status_code}")


def query_from_server(query_msg: str):
    """从服务器中查询数据"""
    url = f"http://{SERVER_URL}:3001/api/v1/workspace/{ISRAG_WORKSPACE_NAME}/chat"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {ANYTHINGLLM_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {"message": query_msg, "mode": "query"}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("请求成功:", response.json())
    else:
        raise Exception(f"请求失败，状态码: {response.status_code}")

    return response.json()


def read_data_rec(query_msg: str):
    """执行 SQL 查询并上传结果"""
    fetch_result = fetch_all_records()
    filepath = save_data_to_file(fetch_result, 'output.txt')
    location = upload_file_to_server(filepath)
    update_embeddings_on_server(location)
    return query_from_server(query_msg)


tool_rag = [{
    "type": "function",
    "function": {
        "name": "rag",
        "description": "在数据库中查询用户问题相关的记录",
        "parameters": {
            "type": "object",
            "properties": {
                "query_msg": {
                    "type": "string",
                    "description": "将用户查询需求传入，必须将所有的时间信息转换为yyyy-mm-dd hh:mm:ss的形式",
                },
            },
            "required": ["query_msg"],
            "additionalProperties": False
        },
    }
}]


# ========================sql生成查询========================
def sql_search(query):
    """根据message执行相应的sql操作"""
    result = session.execute(text(query))
    records = result.fetchall()
    return records


tool_sql_search = [{
    "type": "function",
    "function": {
        "name": "sql_search",
        "description": "使用此工具返回数据库结果并回答用户问题",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                        SQL query extracting info to answer the user's question.
                        SQL should be written using this database schema:
                        {database_schema_string}
                        The query should be returned in plain text, not in JSON.
                        The query should only contain grammars supported by SQLite.
                        """,
                },
            },
            "required": ["query"],
            "additionalProperties": False
        },
    }
}]


# ========================sql生成执行========================
def sql_operate(query):
    """根据message执行相应的sql操作"""
    session.execute(text(query))
    session.commit()
    return "已完成记录操作"


tool_sql_operate = [{
    "type": "function",
    "function": {
        "name": "sql_operate",
        "description": "使用此工具记录新事件或修改原事件",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                        SQL query inserting new record or updating existing records to database.
                        SQL should be written using this database schema:
                        {database_schema_string}
                        The query should be returned in plain text, not in JSON.
                        The query should only contain grammars supported by SQLite.
                        """,
                },
            },
            "required": ["query"],
            "additionalProperties": False
        },
    }
}]


# ========================以描述形式返回所有记录========================
def summarize_records(data_list):
    """
    将每条记录总结为一个字符串，并返回新的记录列表
    :param data_list: 原始记录列表
    :return: 包含总结字符串的新记录列表
    """
    new_data_list = []
    for record in data_list:
        summary = (
            f"[记录时间]为{record['record_time']}，"
            f"[记录地点]为{record['record_location_name']}，"
            f"[目标时间]为{record['target_time']}，"
            f"[目标地点]为{record['target_location_name']}，"
            f"[结束时间]为{record['finish_time']}，"
            f"[提醒时间]为{record['wake_time']}，"
            f"[提醒地点]为{record['target_location_name']}，"
            f"[事件总结]为{record['record_descrpt']}，"
            f"[事件状态]为{'完成' if record['record_status'] else '未完成'},"
            f"[图片描述]为{record['image_descrpt']}，"
            f"[图片ID]为{record['image_id']}."
        )
        new_data_list.append(summary)
    return new_data_list


def sql_get_records(query):
    results = session.query(RecordItem).filter(text(query)).all()
    data_list = [record.__dict__ for record in results]
    return data_list

def sql_get_summarized(query):
    data_list = sql_get_records(query)
    new_data_list = summarize_records(data_list)
    return new_data_list


tool_sql_get_summarized = [{
    "type": "function",
    "function": {
        "name": "sql_get_summarized",
        "description": "在数据库中筛选后取得对应的记录描述，用以回答用户问题",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                        Only generate SQL filter criteria codes, never generate codes before WHERE or including WHERE.                        
                        Database schema is:
                        {database_schema_string}
                        The query should be returned in plain text, not in JSON.
                        You should only generate codes after WHERE, such as [record_status =1/0] and other criteria
                        """,
                },
            },
            "required": ["query"],
            "additionalProperties": False
        },
    }
}]

def sql_all_summarized():
    data_list = fetch_all_records()
    new_data_list = summarize_records(data_list)
    return new_data_list

tool_sql_all_summarized = [{
    "type": "function",
    "function": {
        "name": "sql_all_summarized",
        "description": "返回数据库所有数据的描述",
        "parameters": {
            "type": "object",
            "properties": {
                "query_msg": {
                    "type": "string",
                    "description": "默认ask",
                },
            },
            "required": ["query_msg"],
            "additionalProperties": False
        },
    }
}]

tools_rag_sql = tool_sql_operate + tool_sql_all_summarized
