# api_client.py

import json

import httpx
import requests


async def client_post(url: str, args):
    async with httpx.AsyncClient() as client:
        try:
            payload = json.dumps(args, ensure_ascii=False)
            response = await client.post(url, content=payload, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An error occurred: {e.__class__.__name__}==>{str(e)}")


async def client_patch(url: str, args):
    async with httpx.AsyncClient() as client:
        try:
            payload = json.dumps(args, ensure_ascii=False)
            response = await client.patch(url, content=payload, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An error occurred: {e.__class__.__name__}==>{str(e)}")


class APIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'accept': 'application/json',
            'x-api-key': self.api_key
        }

    def post_json(self, url, body, custom_headers=None, timeout=60):
        """
        发送带有 JSON 数据的 POST 请求。
        """
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'

        if custom_headers:
            headers.update(custom_headers)  # 合并自定义请求头
        try:
            response = requests.post(url, headers=headers, data=json.dumps(body), timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as req_error:
            if isinstance(req_error, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
                print("网络连接错误:", req_error)
                raise
            else:
                print("请求异常:", req_error)
                raise

    def post_files(self, url, files, custom_headers=None, timeout=60):
        """
        发送带有文件的 POST 请求。
        """
        headers = self.default_headers.copy()

        if custom_headers:
            headers.update(custom_headers)  # 合并自定义请求头
        try:
            response = requests.post(url, headers=headers, files=files, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as req_error:
            if isinstance(req_error, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
                print("网络连接错误:", req_error)
                raise
            else:
                print("请求异常:", req_error)
                raise
