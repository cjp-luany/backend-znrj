import json
from datetime import time, datetime
import requests

tecent_map_api_key = 'ESPBZ-WDHKQ-MBD5P-BWOB2-NZYYV-6EBP4'

thought_step_string = """
1. 结合关键概念，我收集到什么信息？
2. 下一步我要达到什么目标？
3. 基于下一步目标我要做什么？（比如调用什么工具或是与用户沟通什么内容）
"""

tool_thought_step = [{
    "type": "function",
    "function": {
        "name": "thought_step",
        "description": "记录每一次交互后的思路，固定每次收到新信息均需调用",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                        按以下标准模板思考，并一步步输出每一项:
                        {thought_step_string}
                        """,
                },
            },
            "required": ["query"],
            "additionalProperties": False
        },
    }
}]

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

tool_get_current_location = [{
    "type": "function",
    "function": {
        "name": "get_current_location",
        "description": "获取当前位置信息的经纬度",
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

tool_get_current_location_name = [{
    "type": "function",
    "function": {
        "name": "get_current_location_name",
        "description": "获取当前位置描述",
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

tool_get_location_summary = [{
    "type": "function",
    "function": {
        "name": "get_location_summary",
        "description": "查询位置信息，只传入地点描述的文本，不要传入任何其他参数。该工具已封装了用户位置信息，你无需额外获取。",
        "parameters": {
            "type": "object",
            "properties": {
                "query_msg": {
                    "type": "string",
                    "description": "将用户查询的地点的描述文本传入",
                },
            },
            "required": ["query_msg"],
            "additionalProperties": False
        },
    }
}]


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



def thought_step(query):
    return query


def thought_key_record(query):
    return query


def get_current_location():
    """获取经纬度"""
    response = requests.get("http://127.0.0.1:6202/get_lat_longit/")
    # print(response.content)
    res_json = response.json()
    if response.status_code == 200:
        latitude = res_json[0]
        longitude = res_json[1]
        current_location = latitude, longitude
        return current_location


def get_current_location_name():
    lat, lng = get_current_location()

    url = "https://apis.map.qq.com/ws/geocoder/v1/?location="
    params = {
        'location': f"{lat},{lng}",
        'key': tecent_map_api_key,
        'poi_options': 'policy=5',
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == 0:
        # 返回 formatted_addresses 中的 recommend 地址
        return data['result']['formatted_addresses']['standard_address']
    else:
        return "Error: 无法获取地址信息"


def fetch_location_data(keyword):
    lat, lng = get_current_location()
    url = "https://apis.map.qq.com/ws/place/v1/suggestion"
    params = {
        'keyword': keyword,
        'location': f'{lat},{lng}',
        'key': tecent_map_api_key,
        'page_size': 5,
    }
    response = requests.get(url, params=params)
    return response.json()


def format_location_data(data):
    if not data or 'status' not in data or data['status'] != 0:
        return "Error: 数据无效或请求失败"

    if 'data' not in data or not data['data']:
        return "Error: 没有返回任何地点数据"

    location_strings = []
    for result in data['data']:
        location_string = (
            f"名称: {result.get('title', '未知名称')}, "
            f"地址: {result.get('address', '地址未知')}, "
            f"距离: {result.get('_distance', '未知距离')}米, "
            f"纬度: {result['location']['lat']}, "
            f"经度: {result['location']['lng']}"
        )
        location_strings.append(location_string)

    return '\n'.join(location_strings)


def get_location_summary(keyword):
    # 从 query_msg 中提取关键词和位置信息
    # 假设 query_msg 是一个包含 'keyword' 和 'location' 键的字典
    data = fetch_location_data(keyword)
    location_text = format_location_data(data)
    # dispersion = calculate_dispersion(data)
    return f"{location_text}"
    # if dispersion is not None:
    #     return f"{location_text}"
    # else:
    #     return location_text
