import requests


def get_ip_location(api_key, ip=None):
    url = "https://apis.map.qq.com/ws/location/v1/ip"
    params = {
        'key': api_key,
        'ip': ip,  # 如果不提供IP地址，会自动使用请求端的IP
        'output': 'json'
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(data)



# 替换为你的API密钥
api_key = 'ESPBZ-WDHKQ-MBD5P-BWOB2-NZYYV-6EBP4'
get_ip_location(api_key)