import json
import time
from datetime import datetime
import requests

tecent_map_api_key = 'ESPBZ-WDHKQ-MBD5P-BWOB2-NZYYV-6EBP4'


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


def thought_step(query):
    return query


def get_current_location():
    """获取经纬度"""
    response = requests.get("http://127.0.0.1:6201/get_lat_longit/")
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
