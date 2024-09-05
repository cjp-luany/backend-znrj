
import calendar
import os
import random
import time
import json

from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

from databases import Database
from fastapi.middleware.cors import CORSMiddleware
from fastcrud import crud_router, FastCRUD
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, \
    Boolean
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from fastapi import Depends, FastAPI
import requests

# 加载当前目录下的 .env 文件
load_dotenv()

DEBUG = True
MAX_RESULT_SIZE = 1000
ROWS_PER_PAGE = 50
SECRET_KEY = '123456FLASK'

# 数据库连接
CUR_DIR = os.path.realpath(os.path.dirname(__file__))
JOIN_DIR = os.path.join(CUR_DIR, "sqlite.db")
DATABASE_URL = "sqlite+aiosqlite:///" + JOIN_DIR  # 这里的路径应该是你的数据库文件的路径
# DATABASE_URL = "sqlite:///sqlite.db" # 这里的路径应该是你的数据库文件的路径

database = Database(DATABASE_URL)  # https://pypi.org/project/databases/ 参考database的使用方法

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


IMAGE_RECOGNITION_SERVER_URL = "http://api.llm.marko1616.com:8000"


def python_get_now_timespan():
    return int(time.time())


# Database session dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


# Create tables before the app start
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


api = FastAPI(lifespan=lifespan)


class Base(DeclarativeBase):
    pass


class RecordItem(Base):
    __tablename__ = 'record'
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


class RecordItemCreateSchema(BaseModel):
    record_time: datetime
    record_location_name: str
    record_location: str
    target_time: datetime
    target_location_name: str
    target_location: str
    finish_time: datetime
    wake_time: datetime
    wake_location_name: str
    wake_location: str
    record_descrpt: str
    record_status: bool
    image_descrpt: str
    image_id: str


class RecordItemUpdateSchema(BaseModel):
    record_time: datetime
    record_location_name: str
    record_location: str
    target_time: datetime
    target_location_name: str
    target_location: str
    finish_time: datetime
    wake_time: datetime
    wake_location_name: str
    wake_location: str
    record_descrpt: str
    record_status: bool
    image_descrpt: str
    image_id: str


# CRUD operations setup
crud_record = FastCRUD(RecordItem)


class ImageItem(Base):
    __tablename__ = 'images'
    id = Column(String, primary_key=True)
    image_descrpt = Column(String, default="")
    image_code = Column(String, default="")


class ImageItemCreateSchema(BaseModel):
    id: str
    image_descrpt: str
    image_code: str

    def __init__(self, id: str, image_descrpt: str, image_code: str):
        super().__init__(id=id, image_descrpt=image_descrpt, image_code=image_code)


class ImageItemUpdateSchema(BaseModel):
    image_descrpt: str
    image_code: str


crud_image = FastCRUD(ImageItem)

# CRUD router setup
record_item_router = crud_router(
    session=get_session,
    model=RecordItem,
    create_schema=RecordItemCreateSchema,
    update_schema=RecordItemUpdateSchema,
    path="/api/record",
    tags=["RecordItem"]
)

api.include_router(record_item_router)

image_item_router = crud_router(
    session=get_session,
    model=ImageItem,
    create_schema=ImageItemCreateSchema,
    update_schema=ImageItemUpdateSchema,
    path="/api/image",
    tags=["ImageItem"]
)

api.include_router(image_item_router)


def get_week_dates():
    # 定义一个列表，用于将weekday()函数的输出(这个函数输出0-6，代表周一到周日)转换为中文的星期
    weekDays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    # 获取当前的日期（东八区）
    now = datetime.now(timezone(timedelta(hours=8)))

    # 创建一个列表来储存当前周的所有日期以及对应的星期数
    weekCalendar = []

    # 从当前日期开始的七天，他们的日期和星期数，注意日期我们转换为了字符串
    for i in range(7):
        day = now + timedelta(days=i)
        weekCalendar.append({
            "date": day.date().__str__(),
            "title": weekDays[day.weekday()]
        })

    return weekCalendar



"""
返回一周日期
date
title
返回每一日任务
textTitle
color
minutesDuration
dateTime
"""


def get_tasks_for_each_day(year_month_str):
    # 将输入的字符串转换为datetime对象，方便后续操作
    date = datetime.strptime(year_month_str, "%Y-%m")

    # calendar.monthrange返回指定年月的第一天是周几（0-6，0是周一）和这个月的天数
    _, days_in_month = calendar.monthrange(date.year, date.month)

    tasks = []

    # 对每一天进行处理
    for day in range(1, days_in_month + 1):
        # 转换为字符串形式的日期（"YYYY-MM-DD"）
        date_str = date.replace(day=day).strftime("%Y-%m-%d")

        # 模拟从数据源获取任务
        # 真实编程时可能需要连接数据库或调用其他函数/方法获取指定日期的任务
        daily_tasks = []

        # 将获取到的任务数量和任务列表存入字典
        tasks.append({"date":date_str, "task_count": len(daily_tasks), "tasks": daily_tasks})

    return tasks

@api.get("/weekItems/")
async def week_items( db: AsyncSession = Depends(get_session)):
    w = get_week_dates()
    items = await crud_record.get_multi(db=db, target_time__lt=w[-1]["date"], target_time__gt=w[0]["date"])
    #print(items.__str__())
    # {'data': [{'record_time': datetime.datetime(2024, 8, 14, 19, 47, 42), 'target_time': datetime.datetime(2024, 8, 15, 8, 0), 'finish_time': datetime.datetime(2024, 8, 15, 9, 0), 'wake_time': datetime.datetime(2024, 8, 15, 7, 0), 'record_descrpt': '在公司，3个人开会', 'record_status': False}], 'total_count': 1}

    # 创建一个新的列表，用于组合每天的日期和任务
    new_items = []
    # for date_item in w:
    #     # 对于一周中的每一天，找到这一天的所有任务
    #     tasks_for_day = [item for item in items['data'] if item['target_time'].date().isoformat() == date_item["date"]]
    #     # 将日期和任务组合在一个字典中，然后添加到新的列表中
    #     new_items.append({"date": date_item, "tasks": tasks_for_day})

    for date_item in w:
        formatted_tasks = []
        # 对于一周中的每一天，找到这一天的所有任务
        for item in items['data']:
            if item['target_time'].date().isoformat() == date_item["date"]:
                # 生成随机颜色，每个颜色的值在0-255之间
                color = '#{:02x}{:02x}{:02x}'.format(random.randint(0, 255), random.randint(0, 255),
                                                     random.randint(0, 255))
                # 选取1到16（含）之间的随机整数
                color_number = random.randint(1, 16)

                # 计算任务完成所需的分钟数
                duration = item["finish_time"] - item["target_time"]
                duration_in_s = duration.total_seconds()
                minutesDuration = divmod(duration_in_s, 60)[0]

                # 格式化任务信息
                task = {
                    'textTitle': item['record_descrpt'],
                    'color': color_number,
                    'minutesDuration': int(minutesDuration),
                    'dateTime': date_item["date"],
                    'hour': item["target_time"].hour,
                    'minute': item["target_time"].minute
                }

                formatted_tasks.append(task)

        # 将日期和任务组合在一个字典中，然后添加到新的列表中
        new_items.append({"date": date_item, "tasks": formatted_tasks})

    # #print(new_items.__str__())
    return {"data": new_items, "code":200}


@api.get("/monthItems/{year_month}/")
async def month_items(year_month:str, db: AsyncSession = Depends(get_session)):
    m = get_tasks_for_each_day(year_month)
    #print(m)
    #  "[{'date': '2024-08-01', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-02', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-03', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-04', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-05', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-06', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-07', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-08', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-09', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-10', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-11', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-12', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-13', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-14', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-15', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-16', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-17', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-18', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-19', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-20', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-21', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-22', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-23', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-24', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-25', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-26', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-27', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-28', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-29', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-30', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-31', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}]"
    items = await crud_record.get_multi(db=db, target_time__lt=m[-1]["date"], target_time__gt=m[0]["date"])
    #print(items.__str__())
    new_items = list(map(lambda x: {
        "target_time": x['target_time'],
        "record_descrpt": x['record_descrpt']
    }, items['data']))
    #print(new_items.__str__())
    # [{'target_time': datetime.datetime(2024, 8, 21, 15, 0), 'record_descrpt': '下周三下午3点的会议'}, {'target_time': datetime.datetime(2024, 8, 14, 15, 0), 'record_descrpt': '在2024-08-14 15:00进行市场开拓会议，预计持续1小时'}, {'target_time': datetime.datetime(2024, 8, 14, 20, 0), 'record_descrpt': '2024年8月14日20:00在北京路吃饭'}, {'target_time': datetime.datetime(2024, 8, 15, 8, 0), 'record_descrpt': '在公司，3个人开会'}]

    # 添加任务到对应的日期中
    for new_item in new_items:
        target_time = new_item["target_time"].date().__str__()  # 获取这个任务的目标日期
        for item in m:  # 逐个检查m中的项目，是否日期匹配
            if item["date"] == target_time:
                # 如果目标日期在m中，添加这个任务到这天的任务清单中
                item["tasks"].append(new_item["record_descrpt"])
                # 重新计算任务数量
                item["task_count"] = len(item["tasks"])
                break  # 已找到匹配的日期，无需继续寻找

    # 添加任务到对应的日期中
    # for item in new_items:
    #     target_time = item["target_time"]    # 获取这个任务的目标日期
    #     if target_time in m:
    #         # 如果目标日期在m中，添加这个任务到这天的任务清单中
    #         m[target_time]["tasks"].append(item["record_descrpt"])
    #         # 重新计算任务数量
    #         m[target_time]["task_count"] = len(m[target_time]["tasks"])

    return {"data": m, "code":200}



@api.get("/monthTodoItems/{year_month}/")
async def month_todo_items(year_month:str, db: AsyncSession = Depends(get_session)):
    m = get_tasks_for_each_day(year_month)
    #print(m)
    #  "[{'date': '2024-08-01', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-02', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-03', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-04', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-05', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-06', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-07', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-08', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-09', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-10', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-11', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-12', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-13', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-14', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-15', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-16', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-17', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-18', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-19', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-20', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-21', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-22', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-23', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-24', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-25', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-26', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-27', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-28', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-29', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-30', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}, {'date': '2024-08-31', 'task_count': 3, 'tasks': ['Title1', 'Title2', '...']}]"
    # items = await crud_record.get_multi(db=db, target_time__lt=m[-1]["date"], target_time__gt=m[0]["date"])
    items = await crud_record.get_multi(db=db)
    #print(items.__str__())
    return {"data": items, "code":200}


# 上传图片模型
class UploadImageItem(BaseModel):
    img_base64: str

@api.post("/uploadOneImage/")
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
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi import Depends
    from pydantic import BaseModel

    class UploadImageItem(BaseModel):
        img_base64: str

    _id = uuid.uuid4()

    _old_url = f'{IMAGE_RECOGNITION_SERVER_URL}/v1/chat/completions'

    url = 'https://api.gptapi.us/v1/messages'

    # add code here : auth x-api-key: aaa
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'x-api-key':'sk-yyVoHd34C4cheQLRAeB6B8C337F946Ed8629A0D7F402E6C'
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

        # _image_descrpt = response.json()['choices'][0]['message']['content']
    
        _image_descrpt = response.json()['content'][0]['text']
        
        new_item = await crud_image.create(db, ImageItemCreateSchema(id=_id.__str__(), image_descrpt=_image_descrpt,
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



@api.get("/getImageUUID/")
async def get_image_from_uuid(uuid:str, db: AsyncSession = Depends(get_session)):
    try:
        return {
            "code": 200,
            "data": crud_record.get(db, ImageItem.id == uuid)
        }
    except:
        return {
            "code": 500,
            "data": f"未找到图片或内部错误"
        }


# 启动fastapi
def run_fastapi2():
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=6201, loop="asyncio")


# cors名单
origins = [
"*",
    "http://127.0.0.1:8102",
    "http://localhost:8102",
    "http://127.0.0.1:6102",
    "http://127.0.0.1:6201",
    "http://127.0.0.1:6200"
    "http://127.0.0.1:6103",
    "http://127.0.0.1:6202",
    "http://127.0.0.1:6203",
    "http://localhost:6102",
    "http://localhost:6103",
    "http://localhost:6202",
    "http://localhost:6203",
    "http://localhost:62065"
]


# cors中间件
api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)






# @app.post("/custom/items/")
# async def create_item(item_data: CreateItemSchema, db: AsyncSession = Depends(get_session)):
#     return await item_crud.create(db, item_data)
#
# @app.get("/custom/items/{item_id}")
# async def read_item(item_id: int, db: AsyncSession = Depends(get_session)):
#     item = await item_crud.get(db, id=item_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return item

