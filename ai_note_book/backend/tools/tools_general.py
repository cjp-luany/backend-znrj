import time
import string
import random
from datetime import datetime
import json


def print_json(data):
    """
    打印参数。如果参数是有结构的（如字典或列表），则以格式化的 JSON 形式打印；
    否则，直接打印该值。
    """
    if hasattr(data, 'model_dump_json'):
        data = json.loads(data.model_dump_json())

    if (isinstance(data, (list))):
        for item in data:
            print_json(item)
    elif (isinstance(data, (dict))):
        print(json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ))
    else:
        print(data)

# ========================生成随机id========================
# def get_key():
#     characters = string.ascii_letters + string.digits
#     random_key = ''.join(random.choices(characters, k=11))
#     return random_key
#
#
# tool_get_key = [{
#     "type": "function",
#     "function": {
#         "name": "get_key",
#         "description": "生成id",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "query_msg": {
#                     "type": "string",
#                     "description": "默认传入ask",
#                 },
#             },
#             "required": ["query_msg"],
#             "additionalProperties": False
#         },
#     }
# }]

# ========================获取当前时间========================
def get_time():
    """
    获取当前时间，并以 datetime 格式返回，精确到秒
    :return: 当前时间的 datetime 对象，微秒部分为零
    """
    # 获取当前时间的时间戳
    current_timestamp = time.time()
    # 将时间戳转换为 datetime 对象，并将微秒部分设置为零
    current_time = datetime.fromtimestamp(current_timestamp).replace(microsecond=0)
    return current_time




# ========================获取当前周几========================
# def get_week_day():
#     """
#     获取当前星期几
#     """
#     today = datetime.now()
#     weekday_name = today.strftime("%A")
#     return weekday_name


# tool_get_week_day = [{
#     "type": "function",
#     "function": {
#         "name": "get_week_day",
#         "description": "获取当前是周几",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "message": {
#                     "type": "string",
#                     "description": "和时间相关",
#                 },
#             },
#             "required": ["message"],
#             "additionalProperties": False
#         },
#     }
# }]

def get_current_time():
    """
    获取当前时间，并以 YYYY-MM-DD hh:mm:ss 格式返回当前时间字符串和星期名称
    :return: 当前时间的字符串，格式为 'YYYY-MM-DD hh:mm:ss'，以及星期名称
    """
    # 获取当前时间的时间戳
    current_timestamp = time.time()
    # 将时间戳转换为 datetime 对象，并格式化为字符串
    current_time = datetime.fromtimestamp(current_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    # 获取当前星期名称
    weekday_name = datetime.now().strftime("%A")
    return current_time, weekday_name

tool_get_current_time = [{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "获取当前时间与星期几",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "无需传入参数",
                },
            },
            "required": ["message"],
            "additionalProperties": False
        },
    }
}]


tools_general = tool_get_current_time