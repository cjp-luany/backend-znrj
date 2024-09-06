import random

from api import get_session
from backend.mobile_service.main import api, crud_record
import calendar
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi import Depends, FastAPI


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