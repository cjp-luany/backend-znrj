import base64

from fastapi import Depends, requests
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from crud.models import get_session, ImageItemCreateSchema

IMAGE_RECOGNITION_SERVER_URL = "http://api.llm.marko1616.com:8000"


# 上传图片模型
class UploadImageItem(BaseModel):
    img_base64: str


mykey = f'sk-yyVoHd34C4cheQLRAeB6B8C337F946Ed8629A0D7F402E6C'


async def recognize_one_image(item: UploadImageItem, db: AsyncSession = Depends(get_session)):
    """
    入参：
    img_base64 ： base64编码图片，除去data.image base64, 逗号后面的内容

    保存和识别图片
    1. 上传图片获取图片描述
    2. 返回id，图片描述
    3. 存储id，图片描述，编码
    """

    import uuid
    import requests
    import json

    _id = uuid.uuid4()

    _old_url = f'{IMAGE_RECOGNITION_SERVER_URL}/v1/chat/completions'

    url = 'https://api.gptapi.us/v1/messages'

    # add code here : auth x-api-key: aaa
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'x-api-key': f'{mykey}'
    }

    body = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": item.img_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": "这张图里有什么，用中文回答，少于25字"
                    }
                ]
            }
        ]
    }

    try:
        # 设置超时时间为30秒
        response = requests.post(url, headers=headers, data=json.dumps(body), timeout=60)

        response.raise_for_status()

        print("获取图像识别成功:")
        print("服务器返回的响应:", response.json())

        # GLM: response.json()['choices'][0]['message']['content']

        # Claude-3
        _image_descrpt = response.json()['content'][0]['text']

        new_item = await crud.start.crud_image.create(db, ImageItemCreateSchema(id=_id.__str__(),
                                                                                image_descrpt=_image_descrpt,
                                                                                image_code=item.img_base64))

        return {
            "code": 200,
            "data": {
                "image_id": new_item.__dict__["id"],
                "image_descrpt": new_item.__dict__["image_descrpt"]
            }
        }

    except requests.exceptions.RequestException as req_error:
        if isinstance(req_error, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
            print("网络连接错误:", req_error)
            return {
                "code": 500,
                "data": "网络连接错误，请稍后重试"
            }
        else:
            print("请求异常:", req_error)
            return {
                "code": 500,
                "data": "请求异常，请稍后重试"
            }
    except KeyError as e:
        print("响应解析失败:", e)
        return {
            "code": 500,
            "data": "无法解析服务器返回的响应"
        }
    except Exception as e:
        print("发生错误:", e)
        return {
            "code": 500,
            "data": "发生未知错误"
        }


def transcribe_audio(base64_audio):
    """
    将 Base64 编码的音频文件发送到 OpenAI 的转录服务。

    :param base64_audio: Base64 编码的 MP3 音频文件
    :param api_key: OpenAI API 密钥
    :return: 转录结果的 JSON 响应
    """
    # 解码 Base64 字符串为字节
    audio_data = base64.b64decode(base64_audio)

    # 使用 requests 库发送 POST 请求
    url = "https://api.gptapi.us/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {mykey}"
    }

    # 准备文件数据
    files = {
        "file": ("audio.wav", audio_data, "audio/wav"),
        "model": (None, "whisper-1")
    }

    # 发送请求
    response = requests.post(url, headers=headers, files=files)

    # 检查请求是否成功
    if response.status_code == 200:
        return response.json()  # 返回转录结果
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


class SpeechAsrModel(BaseModel):
    audio: str
    audio_format: str

    # {
    #     'audio': base64String,
    #     "audio_format": "wav",
    # }


async def speech_asr(item: SpeechAsrModel):
    try:
        result = transcribe_audio(item.audio)
        print("Transcription Result:", result)

        return {
            "code": 200,
            "data": result
        }

    except Exception as e:
        print("Failed to transcribe audio:", e)
        return {
            "code": 500,
            "data": f"内部错误{e}"
        }


def generate_speech_base64(text, voice="alloy"):
    """
    生成语音并返回 WAV 文件的 Base64 编码。

    :param api_key: OpenAI API 密钥
    :param text: 要转换为语音的文本
    :param voice: 使用的语音类型
    :return: WAV 文件的 Base64 编码
    """
    url = "https://api.gptapi.us/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {mykey}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "tts-1-1106",
        "input": text,
        "voice": voice
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, json=data)

    # 检查请求是否成功
    if response.status_code == 200:
        # 将响应内容保存为 WAV 文件
        with open("speech.wav", "wb") as wav_file:
            wav_file.write(response.content)

        # 读取 WAV 文件并转换为 Base64 编码
        with open("speech.wav", "rb") as wav_file:
            wav_data = wav_file.read()
            base64_encoded = base64.b64encode(wav_data).decode('utf-8')

        return base64_encoded
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


async def speech_tts(text: str, voice: str = "alloy"):
    try:
        base64_audio = generate_speech_base64(text, voice)
        # print("Base64 Encoded WAV Audio:", base64_audio)
        return {
            "code": 200,
            "data": base64_audio
        }

    except Exception as e:
        print("Failed to transcribe audio:", e)
        return {
            "code": 500,
            "data": f"内部错误{e}"
        }
