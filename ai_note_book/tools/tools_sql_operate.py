import os

from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import requests
import uuid
from sqlalchemy import text
from tools.tools_location import get_current_location, get_current_location_name  # 假设位置工具导入
from tools.tools_general import get_time  # 假设时间工具导入

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

def get_sqlite_db_path(db_name='sqlite.db'):
    """
    获取当前目录上一级目录下的 SQLite 数据库文件路径。

    :param db_name: 数据库文件名，默认为 'sqlite.db'
    :return: SQLite 数据库文件的完整路径
    """
    # 获取当前工作目录
    current_directory = os.getcwd()

    # 获取上一级目录
    parent_directory = os.path.dirname(current_directory)

    # 构建数据库文件的路径
    sqlite_db_path = os.path.join(parent_directory, db_name)

    return sqlite_db_path


import requests
import uuid
from sqlalchemy import text

def sql_insert(target_time, finish_time, wake_time,
               record_descrpt, record_status, image_descrpt, image_id, record_cls):
    """插入一条新的记录到数据库中"""

    # 从 API 获取 user_id
    response = requests.get("http://127.0.0.1:6202/get_user_id/")
    user_id = response.json()

    # 生成UUID
    unique_id = str(uuid.uuid4())

    # 获取当前时间
    record_time = get_time()

    # 获取当前位置信息
    record_location_name = get_current_location_name()
    record_location = get_current_location()

    # 格式化 location 值
    record_location_str = f"({record_location[0]}, {record_location[1]})"

    # 构建SQL插入语句
    query = f"""
    INSERT INTO record (
        record_id, 
        record_time, 
        record_location_name, 
        record_location, 
        target_time, 
        finish_time, 
        wake_time, 
        record_descrpt, 
        record_status, 
        image_descrpt, 
        image_id, 
        record_cls, 
        user_id
    ) VALUES (
        '{unique_id}', 
        '{record_time}', 
        '{record_location_name}', 
        '{record_location_str}', 
        {f"'{target_time}'" if target_time else "NULL"}, 
        {f"'{finish_time}'" if finish_time else "NULL"}, 
        {f"'{wake_time}'" if wake_time else "NULL"}, 
        '{record_descrpt}', 
        {f"'{record_status}'" if record_status else "NULL"}, 
        {f"'{image_descrpt}'" if image_descrpt else "NULL"}, 
        {f"'{image_id}'" if image_id else "NULL"}, 
        {f"'{record_cls}'" if record_cls else "NULL"}, 
        '{user_id}'
    );
    """

    # 执行SQL插入操作
    session.execute(text(query))
    session.commit()
    return f"记录已成功插入,record_id为{unique_id}"

# 工具封装
tool_sql_insert = [{
    "type": "function",
    "function": {
        "name": "sql_insert",
        "description": "使用此工具插入新的事件记录",
        "parameters": {
            "type": "object",
            "properties": {
                "target_time": {
                    "type": "string",
                    "description": "[目标时间]，格式DateTime为 'YYYY-MM-DD HH:MM:SS'，如果无相关信息，则为空值。"
                },
                "finish_time": {
                    "type": "string",
                    "description": "[结束时间]，格式DateTime为 'YYYY-MM-DD HH:MM:SS'，如果无相关信息，则为空值。"
                },
                "wake_time": {
                    "type": "string",
                    "description": "[提醒时间]，格式DateTime为 'YYYY-MM-DD HH:MM:SS'，如果无相关信息，则为空值。"
                },
                "record_descrpt": {
                    "type": "string",
                    "description": "[事件总结]"
                },
                "record_status": {
                    "type": "string",
                    "description": "[事件状态]，分为“未完成”/“完成”/“记事”/“取消”，不可为空值。"
                },
                "image_descrpt": {
                    "type": "string",
                    "description": "[图片描述]，如果无相关信息，则为空值。"
                },
                "image_id": {
                    "type": "string",
                    "description": "[图片ID]，如果无相关信息，则为空值。"
                },
                "record_cls": {
                    "type": "string",
                    "description": "[记录类别]，表示事件的类别。如果无相关信息，则为空值。"
                }
            },
            "required": [
                "target_time",
                "finish_time",
                "wake_time",
                "record_descrpt",
                "record_status",
                "image_descrpt",
                "image_id",
                "record_cls"
            ],
            "additionalProperties": False
        },
    }
}]



import requests
from sqlalchemy import text

def sql_update(record_ids, target_time=None, finish_time=None,
               wake_time=None, record_descrpt=None,
               record_status=None, image_descrpt=None, record_cls=None):
    """更新记录中的指定字段，支持批量更新，强制包含record_id和user_id条件"""

    # 在函数内部获取 user_id，确保每次调用时是独立的
    response = requests.get("http://127.0.0.1:6202/get_user_id/")
    user_id = response.json()

    # 构建SQL更新语句的各个部分
    set_clauses = []

    if target_time is not None:
        set_clauses.append(f"target_time = :target_time")
    if finish_time is not None:
        set_clauses.append(f"finish_time = :finish_time")
    if wake_time is not None:
        set_clauses.append(f"wake_time = :wake_time")
    if record_descrpt is not None:
        set_clauses.append(f"record_descrpt = :record_descrpt")
    if record_status is not None:
        set_clauses.append(f"record_status = :record_status")
    if image_descrpt is not None:
        set_clauses.append(f"image_descrpt = :image_descrpt")
    if record_cls is not None:
        set_clauses.append(f"record_cls = :record_cls")

    # 如果没有要更新的字段，则直接返回
    if not set_clauses:
        return "没有提供更新的字段"

    # 构建SET子句
    set_clause_str = ", ".join(set_clauses)

    # 构建WHERE子句，强制包含多个record_id和user_id条件
    record_ids_str = ", ".join(f"'{str(record_id)}'" for record_id in record_ids)
    where_clause_str = f"record_id IN ({record_ids_str}) AND user_id = :user_id"

    # 构建完整的 SQL 更新语句
    query = f"""
    UPDATE record
    SET {set_clause_str}
    WHERE {where_clause_str};
    """

    # 执行SQL更新操作
    session.execute(text(query), {
        'target_time': target_time,
        'finish_time': finish_time,
        'wake_time': wake_time,
        'record_descrpt': record_descrpt,
        'record_status': record_status,
        'image_descrpt': image_descrpt,
        'record_cls': record_cls,
        'user_id': user_id
    })
    session.commit()
    return "记录已成功更新"

tool_sql_update = [{
    "type": "function",
    "function": {
        "name": "sql_update",
        "description": "使用此工具更新事件记录的字段，只能以记录唯一标识record_id为定位条件，支持批量更新。",
        "parameters": {
            "type": "object",
            "properties": {
                "record_ids": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "要更新的记录的唯一标识record_id列表。"
                },
                "target_time": {
                    "type": "string",
                    "description": "[目标时间]，格式为 'YYYY-MM-DD HH:MM:SS'。如果不修改此字段，可以不传此参数。"
                },
                "finish_time": {
                    "type": "string",
                    "description": "[结束时间]，格式为 'YYYY-MM-DD HH:MM:SS'。如果不修改此字段，可以不传此参数。"
                },
                "wake_time": {
                    "type": "string",
                    "description": "[提醒时间]，格式为 'YYYY-MM-DD HH:MM:SS'。如果不修改此字段，可以不传此参数。"
                },
                "record_descrpt": {
                    "type": "string",
                    "description": "[事件总结]。如果不修改此字段，可以不传此参数。"
                },
                "record_status": {
                    "type": "string",
                    "description": "[事件状态]，分为“未完成”/“完成”/“记事”/“取消”。如果不修改此字段，可以不传此参数。"
                },
                "image_descrpt": {
                    "type": "string",
                    "description": "[图片描述]，如果不修改此字段，可以不传此参数。"
                },
                "record_cls": {
                    "type": "string",
                    "description": "[记录类别]，表示事件的类别。如果不修改此字段，可以不传此参数。"
                }
            },
            "required": ["record_ids"],
            "additionalProperties": False
        },
    }
}]





# ANYTHINGLLM_TOKEN = "A6WW35F-A6RMWBH-PWRQJV3-5DT5DYS"  # this is server anything llm token
# ISRAG_WORKSPACE_NAME = "israg"
# NORAG_WORKSPACE_NAME = "norag"

# ========================数据库结构========================
# database_schema_string = """
# CREATE TABLE record (
#     id STR PRIMARY KEY NOT NULL, -- 键值，11位大小写字母数字组成
#     record_time DATETIME, -- [记录时间],格式为YYYY-MM-DD hh:mm:ss
#     record_location_name STR, -- [记录地点],格式为STR
#     record_location String, -- [记录坐标],格式为String:经度,纬度
#     target_time DATETIME, -- [目标时间],格式为YYYY-MM-DD hh:mm:ss
#     target_location_name STR, -- [目标地点],格式为STR
#     target_location String, -- [目标坐标],格式为String:经度,纬度
#     finish_time DATETIME, -- [结束时间],格式为YYYY-MM-DD hh:mm:ss
#     wake_time DATETIME, -- [提醒时间],格式为YYYY-MM-DD hh:mm:ss
#     wake_location_name String, -- [提醒地点],格式为STR
#     wake_location String, -- [提醒坐标],格式为String:经度,纬度
#     record_descrpt STR , -- [事件总结]
#     record_status BOOLEAN -- [事件状态]，0为未完成，1为完成
#     image_descrpt STR -- [图片描述]，如用户未提及则为Null
#     image_id STR -- [图片ID]，如用户未提及则为Null
#     user_id STR -- [用户ID]
# );
# """
#
# database_update_schema_string = """
# CREATE TABLE record (
#     target_time DATETIME, -- [目标时间],格式为YYYY-MM-DD hh:mm:ss
#     target_location_name STR, -- [目标地点],格式为STR
#     target_location String, -- [目标坐标],格式为String:经度,纬度
#     finish_time DATETIME, -- [结束时间],格式为YYYY-MM-DD hh:mm:ss
#     wake_time DATETIME, -- [提醒时间],格式为YYYY-MM-DD hh:mm:ss
#     wake_location_name String, -- [提醒地点],格式为STR
#     wake_location String, -- [提醒坐标],格式为String:经度,纬度
#     record_descrpt STR , -- [事件总结]
#     record_status BOOLEAN -- [事件状态]，0为未完成，1为完成
#     image_descrpt STR -- [图片描述]，如用户未提及则为Null
# );
# """


# ========================rag工具========================
# def fetch_all_records():
#     """
#     查询所有数据
#     :return:
#     """
#
#     results = session.query(RecordItem).all()
#     data_list = [record.__dict__ for record in results]
#     return data_list
#
#
# def save_data_to_file(data: List[Dict], filename: str) -> str:
#     """将数据保存到文件中"""
#     # 处理并筛选数据
#     result = list(map(lambda x: {
#         # "record_time": x['record_time'],
#         "record_descrpt": x['record_descrpt']
#     }, data))
#
#     # 将结果转换为 JSON 字符串
#     try:
#         list_str = json.dumps(result, indent=4, ensure_ascii=False)
#     except (TypeError, ValueError) as e:
#         print(f"Error converting to JSON: {e}")
#         return ""
#
#     # 将 JSON 字符串写入文件
#     try:
#         with open(filename, 'w', encoding='utf-8') as f:
#             f.write(list_str)
#     except IOError as e:
#         print(f"Error writing to file: {e}")
#         return ""
#
#     return filename
#
#
# def upload_file_to_server(filepath: str) -> str:
#     """将文件上传到服务器"""
#     url = f"http://{SERVER_URL}:3001/api/v1/document/upload"
#     headers = {
#         'accept': 'application/json',
#         'Authorization': f'Bearer {ANYTHINGLLM_TOKEN}'
#     }
#     with open(filepath, 'rb') as file:
#         files = {'file': (os.path.basename(filepath), file, 'text/plain')}
#         response = requests.post(url, headers=headers, files=files)
#
#     if response.status_code == 200:
#         return response.json()["documents"][0]["location"]
#     else:
#         raise Exception(f"文件上传失败，状态码: {response.status_code}")
#
#
# def update_embeddings_on_server(location: str):
#     """更新服务器上的嵌入数据"""
#     url = f"http://{SERVER_URL}:3001/api/v1/workspace/{ISRAG_WORKSPACE_NAME}/update-embeddings"
#     headers = {
#         'accept': 'application/json',
#         'Authorization': f'Bearer {ANYTHINGLLM_TOKEN}',
#         'Content-Type': 'application/json'
#     }
#     _len = location.split("\\").__len__()
#     _location_str = location.split("\\")[_len - 2] + "/" + location.split("\\")[_len - 1]
#     data = {"adds": [_location_str]}
#     response = requests.post(url, headers=headers, data=json.dumps(data))
#
#     if response.status_code != 200:
#         raise Exception(f"更新嵌入失败，状态码: {response.status_code}")
#
#
# def query_from_server(query_msg: str):
#     """从服务器中查询数据"""
#     url = f"http://{SERVER_URL}:3001/api/v1/workspace/{ISRAG_WORKSPACE_NAME}/chat"
#     headers = {
#         'accept': 'application/json',
#         'Authorization': f'Bearer {ANYTHINGLLM_TOKEN}',
#         'Content-Type': 'application/json'
#     }
#     data = {"message": query_msg, "mode": "query"}
#     response = requests.post(url, headers=headers, data=json.dumps(data))
#
#     if response.status_code == 200:
#         print("请求成功:", response.json())
#     else:
#         raise Exception(f"请求失败，状态码: {response.status_code}")
#
#     return response.json()
#
#
# def read_data_rec(query_msg: str):
#     """执行 SQL 查询并上传结果"""
#     fetch_result = fetch_all_records()
#     filepath = save_data_to_file(fetch_result, 'output.txt')
#     location = upload_file_to_server(filepath)
#     update_embeddings_on_server(location)
#     return query_from_server(query_msg)
#
#
# tool_rag = [{
#     "type": "function",
#     "function": {
#         "name": "rag",
#         "description": "在数据库中查询用户问题相关的记录",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "query_msg": {
#                     "type": "string",
#                     "description": "将用户查询需求传入，必须将所有的时间信息转换为yyyy-mm-dd hh:mm:ss的形式",
#                 },
#             },
#             "required": ["query_msg"],
#             "additionalProperties": False
#         },
#     }
# }]



# ========================sql执行插入========================







# ========================以描述形式返回所有记录========================
# def summarize_records(data_list):
#     """
#     将每条记录总结为一个字符串，并返回新的记录列表
#     :param data_list: 原始记录列表
#     :return: 包含总结字符串的新记录列表
#     """
#     new_data_list = []
#     for record in data_list:
#         summary = (
#             f"[记录时间]为{record['record_time']}，"
#             f"[记录地点]为{record['record_location_name']}，"
#             f"[目标时间]为{record['target_time']}，"
#             #f"[目标地点]为{record['target_location_name']}，"
#             f"[结束时间]为{record['finish_time']}，"
#             f"[提醒时间]为{record['wake_time']}，"
#             #f"[提醒地点]为{record['wake_location_name']}，"
#             f"[事件总结]为{record['record_descrpt']}，"
#             f"[事件状态]为{'完成' if record['record_status'] else '未完成'},"
#             f"[图片描述]为{record['image_descrpt']}，"
#             f"[图片ID]为{record['image_id']}."
#         )
#         new_data_list.append(summary)
#     return new_data_list
#
#
# def sql_get_records(query):
#     response = requests.get("http://127.0.0.1:6202/get_user_id/")
#     user_id = response.json()
#     full_query = f"user_id = '{user_id}' AND {query}"  # 强制包含 user_id 条件
#     results = session.query(RecordItem).filter(text(full_query)).all()
#     data_list = [record.__dict__ for record in results]
#     return data_list
#
# def sql_search_summarized(query):
#     data_list = sql_get_records(query)
#     new_data_list = summarize_records(data_list)
#     return new_data_list
#
#
# tool_sql_search_summarized = [{
#     "type": "function",
#     "function": {
#         "name": "sql_search_summarized",
#         "description": "在数据库中筛选后取得符合条件的记录描述，用以回答用户问题。查询时必须包含当前用户的user_id条件。",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "query": {
#                     "type": "string",
#                     "description": f"""
#                         Only generate SQL filter criteria codes, never generate codes before WHERE or including WHERE.
#                         Database schema is:
#                         {database_schema_string}
#                         The query should be returned in plain text, not in JSON.
#                         You should only generate codes after WHERE, such as [record_status =1/0] and other criteria.
#                         Note: user_id condition will be automatically added to ensure user-specific data is retrieved.
#                         """,
#                 },
#             },
#             "required": ["query"],
#             "additionalProperties": False
#         },
#     }
# }]
#
# def sql_all_summarized():
#     data_list = fetch_all_records()
#     new_data_list = summarize_records(data_list)
#     return new_data_list
#
# tool_sql_all_summarized = [{
#     "type": "function",
#     "function": {
#         "name": "sql_all_summarized",
#         "description": "返回数据库所有数据的描述",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "query_msg": {
#                     "type": "string",
#                     "description": "默认ask",
#                 },
#             },
#             "required": ["query_msg"],
#             "additionalProperties": False
#         },
#     }
# }]

tools_sql_operate = tool_sql_insert + tool_sql_update