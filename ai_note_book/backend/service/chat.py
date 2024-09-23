import asyncio
import json
import os
import threading
import time
from functools import wraps

import requests
from openai.types.chat import ChatCompletionMessageToolCall
from pydantic import BaseModel

from service.function_call import fc_thought_step, fc_sql_insert, fc_sql_update, fc_sql_search
from service.search import OpenAI, PARENT_DIR, sql_search
from utils.api_client import client_post, client_patch
from utils.unclassified import get_current_time, print_json, thought_step, get_current_location_name, \
    get_current_location

client = OpenAI()
path_prompt = os.path.join(PARENT_DIR, "prompt")

with open(os.path.join(path_prompt, "agent_prompt.txt"), 'r', encoding='utf-8') as file:
    system_message_content = file.read()

chat_tools = fc_thought_step + fc_sql_insert + fc_sql_update + fc_sql_search

chat_histories = {}
chat_histories_lock = threading.Lock()

class Query(BaseModel):
    query: str
    latitude: str
    longitude: str
    user_id: str


def get_completion(messages, model="qwen-plus"):
    """ 依赖：OpenAI """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            tools=chat_tools,
        )
        return response.choices[0].message
    except Exception as e:
        print({e})


def clear_chat_history(user_id):
    """ 依赖：chat_histories｜system_message_content｜agent_prompt """

    if user_id in chat_histories:
        print(f"5分钟内无回复，清空用户 {user_id} 的聊天记录...")
        chat_histories[user_id] = [{"role": "system", "content": system_message_content}]
        print(f"用户 {user_id} 的 chat_history 已清空")


def reset_clear_timer(user_id):
    """ 依赖：chat_histories """
    try:
        if user_id in chat_histories:
            if chat_histories[user_id].get('timer'):
                chat_histories[user_id]['timer'].cancel()
            chat_histories[user_id]['timer'] = threading.Timer(300, clear_chat_history, args=[user_id])
            chat_histories[user_id]['timer'].start()
    except Exception as e:
        print({e.__class__.__name__: str(e)})


def get_params_by_chat(function_name, args):
    """ 将 Function Call 输出的 args 转换成网络请求的参数
    参数：
        function_name (str): Function Call 函数名，
        args (dict): Function Call 输出的args
    返回值：
        args | custom_dict (dict): args合并自定义参数，获得网络请求需要的参数
    """

    _copy = {}
    try:
        _copy = args.copy()
    except Exception as e:
        print({e.__class__.__name__: str(e)})

    if function_name == "sql_insert":
        # 同步 获取 user_id
        response = requests.get("http://127.0.0.1:6201/get_user_id/")
        _user_id = response.json()

        # 获取当前时间
        record_time = get_current_time()[0]

        # 获取当前位置信息
        record_location_name = get_current_location_name()
        record_location = get_current_location()

        # 格式化 location 值
        record_location_str = f"({record_location[0]}, {record_location[1]})"

        custom_dict = {
            "record_time": record_time,
            "record_location_name": record_location_name,
            "record_location": record_location_str,
            "user_id": _user_id
        }

        return args | custom_dict

    elif function_name == "sql_update":
        # _ids =args["record_ids"]

        # 同步 获取 user_id
        response = requests.get("http://127.0.0.1:6201/get_user_id/")
        _user_id = response.json()

        custom_dict = {
            "user_id": _user_id
        }

        return args | custom_dict

    elif function_name == "sql_search":
        return args

    else:
        return args


def tool_calls_handler(tool: ChatCompletionMessageToolCall):
    """ 调用大模型输出的 tool 进行 Function Call，执行工具函数
       参数：
           tool (class): Openai 通过对话历史返回的tool对象
       返回值：
           chat_histories: 对话历史通过对话函数的循环输出
    """

    try:
        arguments = tool.function.arguments
        args = json.loads(arguments)
        print(f"{user_id}===={tool.function.name}====")
        print(args)
        result = None

        if tool.function.name == "sql_insert":
            params = get_params_by_chat(tool.function.name, args)
            # asyncio.run(client_post("http://127.0.0.1:6201/api/record/create", params))
            # response.json()["record_id"] 有id但是需要用其他方法从异步获取结果
            result = f"记录已成功插入,record_id为"  # {unique_id}

        elif tool.function.name == "sql_update":
            params = get_params_by_chat(tool.function.name, args)
            for record_id in params["record_ids"]:
                asyncio.run(client_patch(f"http://127.0.0.1:6201/api/record/update/{record_id}", params))
            result = "记录已成功更新"

        elif tool.function.name == "sql_search":
            # 调用 sql_search，不需要 include_descrpt_search 参数
            result = sql_search(
                query=args.get("query", ""),  # 获取 query 参数，默认为空字符串
                record_descrpt=args.get("record_descrpt")  # 获取 record_descrpt 参数
            )

            print(f"{user_id}====Filtered Records====")
            print_json(result)

        elif tool.function.name == "thought_step":
            result = thought_step(args)

        elif tool.function.name == "get_current_time":
            result = get_current_time()

        # print(f"{user_id}====Result of {tool.function.name}====")
        # print(result)

        # TODO: 发现问题，这里append没上锁，导致资源抢占
        chat_histories[user_id]["chat_history"].append({
            "tool_call_id": tool.id,
            "role": "tool",
            "name": tool.function.name,
            "content": str(result)
        })

    except Exception as e:
        print({e.__class__.__name__: str(e)})


def threaded_chat(func):
    @wraps(func)
    def wrapper(user_id, *args, **kwargs):
        if user_id not in chat_histories:
            with chat_histories_lock:
                if user_id not in chat_histories:
                    chat_histories[user_id] = {
                        "chat_history": [{"role": "system", "content": system_message_content}],
                        "timer": None
                    }

        def process_wrapper():
            result = func(user_id, *args, **kwargs)
            return result

        chat_thread = threading.Thread(target=process_wrapper)
        chat_thread.start()
        chat_thread.join()

        with chat_histories_lock:
            # thread chat return
            # return chat_histories[user_id]["chat_history"][-1]["content"]

            _ret = chat_histories[user_id]["chat_history"][-1]
            if "content" in _ret and isinstance(_ret["content"], str):
                return _ret["content"]

    return wrapper


@threaded_chat
def chat(user_id, user_input, latitude, longitude):
    current_time, weekday_name = get_current_time()
    message = {"role": "user", "content": f"当前时间为 {current_time}，{weekday_name}\\n\\n{user_input}"}

    with chat_histories_lock:
        chat_histories[user_id]["chat_history"].append(message)

    while True:
        _ll = chat_histories[user_id]["chat_history"].__len__()
        print(f"{user_id}=====本轮回复====={_ll}")
        response = get_completion(chat_histories[user_id]["chat_history"])
        if response is None:
            break

        print(f"=====response.tool_calls====={response.tool_calls}")
        print_json(response)

        if response.content is None:
            response.content = ""

        with chat_histories_lock:
            # TODO: 这里是问题根源
            # chat_histories[user_id]["chat_history"].append(response)
            if isinstance(response,str):
                chat_histories[user_id]["chat_history"].append(response)

        if response.tool_calls:
            for tool in response.tool_calls:
                """ 正在调用：Function Call 处理函数 """
                # time.sleep(3)
                tool_calls_handler(tool)
                # return user_id, tool.function.name
        else:
            final_message = {"role": "assistant", "content": response.content}

            with chat_histories_lock:
                chat_histories[user_id]["chat_history"].append(final_message)

            print(f"{user_id}=====最终回复=====")
            print(response.content)
            print(f"{user_id}=====chat_history=====")
            print_json(chat_histories[user_id]["chat_history"])
            break

    _ret = chat_histories[user_id]["chat_history"][-1]
    if "content" in _ret and isinstance(_ret["content"], str):
        return _ret["content"]


def chat_wrapper(user_id):
    return lambda *args, **kwargs: chat(user_id, *args, **kwargs)

def start_loop(query_value: Query):
    """ 对话函数，一直循环对话，使用CoT
       参数：
           query : 用户输入
           latitude : 纬度 0,90
           longitude : 经度 -180,180
           user_id : 用户id
       返回值：
           response: 输出对话回答
    """

    query_dic = query_value.dict()
    global latitude, longitude, user_id

    user_id = query_dic["user_id"]

    if "query" not in query_dic:
        current_location = get_current_location(query_dic['latitude'], query_dic['longitude'])
        latitude = query_dic['latitude']
        longitude = query_dic['longitude']
    else:
        latitude = query_dic['latitude']
        longitude = query_dic['longitude']
        user1_chat = chat_wrapper(user_id)
        response = user1_chat(query_dic["query"], latitude, longitude)

    return {"Response": response, 'code': 200}


def get_lat_longit_value():
    """ TODO：优化全局对象管理，使用缓存 [ {userid, model_obejct },...] """
    return latitude, longitude


def get_user_id():
    return user_id






















def old_chat_warpper(user_id):
    if user_id not in chat_histories:
        chat_histories[user_id] = {
            "chat_history": [{"role": "system", "content": system_message_content}],
            "timer": None
        }

    current_time, weekday_name = get_current_time()

    def chat(user_input, latitude, longitude):
        """ 对话函数，一直循环对话，使用CoT
           参数：
               user_input : 用户输入
               latitude : 纬度 0,90
               longitude : 经度 -180,180
           返回值：
               chat_histories: 输出对话历史最后一条对话（系统返回）
        """

        # reset_clear_timer(user_id)
        message = {"role": "user", "content": f"当前时间为{current_time}，{weekday_name}\n\n{user_input}"}
        chat_histories[user_id]["chat_history"].append(message)

        """ TODO：进行对话循环的多线程改写 
                    可以先将循环注释，打开下面两行，是可以多线程的
        """
        # time.sleep(3)
        # return user_id

        while True:
            print(f"{user_id}=====本轮回复=====")
            response = get_completion(chat_histories[user_id]["chat_history"])
            print_json(response)
            if response.content is None:
                response.content = ""
            chat_histories[user_id]["chat_history"].append(response)

            if response.tool_calls:
                for tool in response.tool_calls:
                    """ 完成：Function Call 处理函数 """
                    # tool_calls_handler(tool)
                    time.sleep(3)
            else:
                chat_histories[user_id]["chat_history"].append({"role": "assistant", "content": response.content})

                print(f"{user_id}=====最终回复=====")
                print(response.content)
                print(f"{user_id}=====chat_history=====")
                print_json(chat_histories[user_id]["chat_history"])
                break
        return chat_histories[user_id]["chat_history"][-1]["content"]

    return chat
