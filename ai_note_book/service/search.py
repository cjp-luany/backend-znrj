import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine
from sqlalchemy import text
# from geoalchemy2 import Geometry
from sqlalchemy.orm import sessionmaker

from crud.models import RecordItem

load_dotenv()

CUR_DIR = os.path.realpath(os.path.dirname(__file__))
PARENT_DIR = os.path.dirname(CUR_DIR)
JOIN_DIR = os.path.join(PARENT_DIR, "sqlite.db")
DATABASE_URL = f"sqlite:///{JOIN_DIR}"

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)
# 创建会话
Session = sessionmaker(bind=engine)
session = Session()
api = FastAPI()
client = OpenAI()


def get_user_id():
    response = requests.get("http://127.0.0.1:6201/get_user_id/")
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
