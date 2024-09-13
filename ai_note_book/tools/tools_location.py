import requests
from ENV import tecent_map_api_key
# tecent_map_api_key = 'ESPBZ-WDHKQ-MBD5P-BWOB2-NZYYV-6EBP4'
#======获取当前坐标======

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


#======获取当前地点描述======
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


#======获取查询的地点信息======


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


# def calculate_dispersion(data):
#     if data['status'] == 0:
#         latitudes = [result['location']['lat'] for result in data['data']]
#         longitudes = [result['location']['lng'] for result in data['data']]
#
#         # 计算标准差作为离散度的度量
#         lat_std = np.std(latitudes)
#         lng_std = np.std(longitudes)
#         print(round((lat_std + lng_std) / 2, 3))
#         # 判断纬度和经度标准差的平均值
#         if round((lat_std + lng_std) / 2, 3) >= 0.001:
#             dispersion = "非精准"
#         else:
#             dispersion = "精准"
#         return dispersion
#     else:
#         return None


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


# print(get_location_summary("超市"))

#======get_location_summary大模型描述======
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

#======拼接tools_location大模型描述======
tools_location = tool_get_current_location + tool_get_current_location_name + tool_get_location_summary

# 替换为你自己的API密钥

# tools_location = tool_get_current_location + tool_get_location_summary
# latitude=40.12
# longitude=116.27
# # latitude = 30.467467
# # longitude = 104.0169
# get_location_summary("火车站",latitude,longitude)
# a  = 1
