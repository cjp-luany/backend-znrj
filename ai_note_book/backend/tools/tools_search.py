import os

from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import requests
import json
from typing import List, Dict
from fastapi import FastAPI
# from geoalchemy2 import Geometry
from sqlalchemy import Column, String, DateTime, \
    Boolean
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from openai import OpenAI
import uuid
from datetime import datetime
from sqlalchemy import text

from tools.tools_location import get_current_location, get_current_location_name  # 假设位置工具导入
from tools.tools_general import get_time  # 假设时间工具导入


load_dotenv()


class RecordItem():
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

# 数据库连接
CUR_DIR = os.path.realpath(os.path.dirname(__file__))
PARENT_DIR = os.path.dirname(CUR_DIR)
JOIN_DIR = os.path.join(PARENT_DIR, "sqlite.db")
# DATABASE_URL = "sqlite:///" + JOIN_DIR  # 这里的路径应该是你的数据库文件的路径
DATABASE_URL = f"sqlite:///{JOIN_DIR}"
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
client = OpenAI()

database_update_schema_string = """
    --记录列名：record_cls，格式：STR，描述：[记录类别],包含会议、记录、待办、想法
    --记录列名：record_time，格式：DATETIME，描述：一件事被用户记录的时间,格式为YYYY-MM-DD hh:mm:ss
    --记录列名：record_location_name，格式：STR，描述：一件事被用户记录的地点,格式为STR
    --记录列名：target_time，格式：DATETIME，描述：用户计划做某件事的目标时间,格式为YYYY-MM-DD hh:mm:ss
    --记录列名：finish_time，格式：DATETIME，描述：某件事开始后结束的时间,格式为YYYY-MM-DD hh:mm:ss
    --记录列名：wake_time，格式：DATETIME，描述：用户为某个记录设定的提醒时间,格式为YYYY-MM-DD hh:mm:ss
    --记录列名：record_descrpt，格式：STR，描述：事件的总结描述
    --记录列名：record_status，格式：STR，描述：[事件状态]，分为“未完成”/“完成”/“记事”/“取消”
    --记录列名：image_descrpt，格式：STR，描述：[图片描述]，如用户未提及则为Null"""

def get_user_id():
    response = requests.get("http://127.0.0.1:6202/get_user_id/")
    return response.json()

def summarize_records(data_list):
    """
    将每条记录总结为一个字符串，并返回新的记录列表
    :param data_list: 原始记录列表
    :return: 包含总结字符串的新记录列表
    """
    new_data_list = []
    for record in data_list:
        summary = (
            f"[记录id]为{record['record_id']}，"
            f"[记录时间]为{record['record_time']}，"
            f"[记录类别]为{record['record_cls']}，"
            f"[记录地点]为{record['record_location_name']}，"
            f"[目标时间]为{record['target_time']}，"
            f"[结束时间]为{record['finish_time']}，"
            f"[提醒时间]为{record['wake_time']}，"
            f"[事件总结]为{record['record_descrpt']}，"
            f"[事件状态]为{record['record_status']}，"
            f"[图片描述]为{record['image_descrpt']}，"
            f"[图片ID]为{record['image_id']}."
        )
        new_data_list.append(summary)
    return new_data_list

def sql_get_records(query):
    user_id = get_user_id()
    full_query = f"user_id = '{user_id}' AND {query}"  # 强制包含 user_id 条件
    results = session.query(RecordItem).filter(text(full_query)).all()
    data_list = [record.__dict__ for record in results]
    return data_list

def get_all_record_descrpt(user_id):
    """
    获取所有满足 user_id 条件的 record_descrpt 并返回列表
    """
    query = f"user_id = '{user_id}'"
    results = session.query(RecordItem).filter(text(query)).all()
    return [{"record_descrpt": record.record_descrpt} for record in results]

def find_similar_records_from_memory(record_descrpt_list, query, similarity_threshold=0.6):
    """
    在内存中的记录列表中查找与查询相似度高于阈值的所有记录。
    """
    if not record_descrpt_list:
        return []

    document_texts = [doc['record_descrpt'] for doc in record_descrpt_list]

    document_embeddings = []
    for text in document_texts:
        response = client.embeddings.create(
            model="text-embedding-v3",
            input=text
        )
        embedding = response.data[0].embedding
        document_embeddings.append(embedding)

    query_response = client.embeddings.create(
        model="text-embedding-v3",
        input=query
    )
    query_embedding = query_response.data[0].embedding

    if not document_embeddings:
        return []

    if len(document_embeddings) > 0 and len(document_embeddings[0]) == 1:
        document_embeddings = [embedding.reshape(1, -1) for embedding in document_embeddings]

    similarities = cosine_similarity([query_embedding], document_embeddings)[0]

    similar_records = []
    for idx, score in enumerate(similarities):
        if score >= similarity_threshold:
            similar_records.append({'record_descrpt': document_texts[idx]})

    return similar_records

def sql_search(query=None, record_descrpt=None):
    """
    根据条件查询数据库，并使用 summarize_records 返回结果。
    如果 record_descrpt 存在且非空，则执行 RAG 搜索；否则只执行 SQL 查询。
    """
    user_id = get_user_id()
    final_query = ""

    # 1. 检查是否需要执行 RAG 搜索
    if record_descrpt and record_descrpt.strip():
        record_descrpt_list = get_all_record_descrpt(user_id)
        rag_results = find_similar_records_from_memory(record_descrpt_list, record_descrpt)

        descrpt_list = [item['record_descrpt'] for item in rag_results]
        if descrpt_list:
            rag_query = " OR ".join([f"record_descrpt = '{descrpt}'" for descrpt in descrpt_list])
            if query:
                final_query = f"({query}) OR ({rag_query})"
            else:
                final_query = rag_query
        else:
            final_query = query if query else ""

    else:
        final_query = query if query else ""

    if final_query:
        data_list = sql_get_records(final_query)
    else:
        data_list = []

    # 如果 data_list 为空，返回提示信息
    if not data_list:
        return "没有找到相关记录"

    summarized_data = summarize_records(data_list)
    return summarized_data


tool_sql_search = [{
    "type": "function",
    "function": {
        "name": "sql_search",
        "description": "在数据库中根据用户的查询条件返回符合条件的记录描述。工具会根据查询内容自动选择合适的查询路径（SQL查询或RAG召回），并最终返回格式化的记录描述。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                        用户查询条件中事件描述以外的部分（例如时间、地点、状态等）。该字段应仅包含WHERE子句中的条件内容。
                        如果用户只提供了事件描述，则此字段可以为空。数据库结构为{database_update_schema_string}。
                    """,
                },
                "record_descrpt": {
                    "type": "string",
                    "description": """
                        用户查询中的事件描述部分。如果用户提供了事件描述内容（例如查询有没有关于什么的事情，有没有人欠我钱等），系统会使用RAG路径查找与该描述最相似的记录。
                        如果事件描述与其他查询条件同时存在，系统会将两者组合以进行最终查询。
                    """,
                }
            },
            "required": [],
            "additionalProperties": False
        },
    }
}]