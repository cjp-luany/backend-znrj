import asyncio

import httpx
from dotenv import load_dotenv, find_dotenv
from openai.types.chat import ChatCompletionMessageToolCall
from utils import unclassified

from crud.models import RecordItemCreateSchema
from tools.tools_general import *
from tools.tools_sql_operate import *
from tools.tools_thought import *
from tools.tools_location import *
from tools.tools_search import *
from pydantic import BaseModel
import threading

client = OpenAI()
with open(os.path.join(CUR_DIR, "prompt/agent_prompt.txt"), 'r', encoding='utf-8') as file:
    system_message_content = file.read()

tools = tools_thought + tools_sql_operate + tool_sql_search

chat_histories = {}


class Query(BaseModel):
    query: str
    latitude: str
    longitude: str
    user_id: str


def get_completion(messages, model="qwen-plus"):
    """ 依赖：OpenAI """

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        tools=tools,
    )
    return response.choices[0].message


def clear_chat_history(user_id):
    """ 依赖：chat_histories｜system_message_content｜agent_prompt """

    if user_id in chat_histories:
        print(f"5分钟内无回复，清空用户 {user_id} 的聊天记录...")
        chat_histories[user_id] = [{"role": "system", "content": system_message_content}]
        print(f"用户 {user_id} 的 chat_history 已清空")


def reset_clear_timer(user_id):
    """ 依赖：chat_histories """

    if user_id in chat_histories:
        if chat_histories[user_id].get('timer'):
            chat_histories[user_id]['timer'].cancel()
        chat_histories[user_id]['timer'] = threading.Timer(300, clear_chat_history, args=[user_id])
        chat_histories[user_id]['timer'].start()


async def post_record(url: str, args):
    payload = json.dumps(args)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, content=payload, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


def params_handler_by_function_name(function_name, args):
    if function_name == "sql_insert":
        return args

    elif function_name == "sql_update":
        return args

    elif function_name == "sql_search":
        return args

    else:
        return args


def tool_calls_handler(tool: ChatCompletionMessageToolCall):
    """ TODO: 完成逻辑 """

    try:
        arguments = tool.function.arguments
        args = json.loads(arguments)
        print(f"{user_id}===={tool.function.name}====")
        print(args)
        result = None

        if tool.function.name == "sql_insert":
            params = params_handler_by_function_name(tool.function.name, args)
            asyncio.run(post_record("http://127.0.0.1:6201/api/record/create", params))
            result = f"记录已成功插入,record_id为"  # {unique_id}

        elif tool.function.name == "sql_update":
            params = params_handler_by_function_name(tool.function.name, args)
            asyncio.run(post_record(f"http://127.0.0.1:6201/api/record/update/{params.record_id}", params))
            result = "记录已成功更新"

        elif tool.function.name == "sql_search":
            # 调用 sql_search，不需要 include_descrpt_search 参数
            result = sql_search(
                query=args.get("query", ""),  # 获取 query 参数，默认为空字符串
                record_descrpt=args.get("record_descrpt")  # 获取 record_descrpt 参数
            )

            print(f"{user_id}====Filtered Records====")
            if isinstance(result, str):
                print(result)

        elif tool.function.name == "thought_step":
            result = unclassified.thought_step(args)

        elif tool.function.name == "get_current_time":
            result = unclassified.get_current_time()

        print(f"{user_id}====Result of {tool.function.name}====")
        print(result)
        chat_histories[user_id]["chat_history"].append({
            "tool_call_id": tool.id,
            "role": "tool",
            "name": tool.function.name,
            "content": str(result)
        })

    except Exception as e:
        print({e.__class__.__name__: str(e)})


def chat_warpper(user_id):
    if user_id not in chat_histories:
        chat_histories[user_id] = {
            "chat_history": [{"role": "system", "content": system_message_content}],
            "timer": None
        }

    current_time, weekday_name = get_current_time()

    def chat(user_input, latitude, longitude):
        reset_clear_timer(user_id)
        message = {"role": "user", "content": f"当前时间为{current_time}，{weekday_name}\n\n{user_input}"}
        chat_histories[user_id]["chat_history"].append(message)

        while True:
            print(f"{user_id}=====本轮回复=====")
            response = get_completion(chat_histories[user_id]["chat_history"])
            print_json(response)
            if response.content is None:
                response.content = ""
            chat_histories[user_id]["chat_history"].append(response)

            if response.tool_calls:
                for tool in response.tool_calls:
                    """ TODO: 完成逻辑 """
                    tool_calls_handler(tool)
                    continue

                    if tool.function.name == "sql_insert":  # 新添加的elif条件
                        tool_call = response.tool_calls[0]
                        arguments = tool_call.function.arguments
                        args = json.loads(arguments)
                        print(f"{user_id}====SQL INSERT====")
                        print(args)
                        result = sql_insert(
                            record_cls=args["record_cls"],
                            target_time=args["target_time"],
                            finish_time=args["finish_time"],
                            wake_time=args["wake_time"],
                            record_descrpt=args["record_descrpt"],
                            record_status=args["record_status"],
                            image_descrpt=args["image_descrpt"],
                            image_id=args["image_id"]
                        )
                        print(f"{user_id}====插入结果====")
                        print(result)
                        chat_histories[user_id]["chat_history"].append({
                            "tool_call_id": tool.id,
                            "role": "tool",
                            "name": "sql_insert",
                            "content": str(result)
                        })
                    elif tool.function.name == "sql_update":  # 新添加的elif条件
                        tool_call = response.tool_calls[0]
                        arguments = tool_call.function.arguments
                        args = json.loads(arguments)
                        print(f"{user_id}====SQL UPDATE====")
                        print(args)

                        # 调用 sql_update 函数
                        result = sql_update(
                            record_ids=args["record_ids"],
                            target_time=args.get("target_time"),
                            finish_time=args.get("finish_time"),
                            wake_time=args.get("wake_time"),
                            record_descrpt=args.get("record_descrpt"),
                            record_status=args.get("record_status"),
                            image_descrpt=args.get("image_descrpt")
                        )

                        print(f"{user_id}====更新结果====")
                        print(result)
                        chat_histories[user_id]["chat_history"].append({
                            "tool_call_id": tool.id,
                            "role": "tool",
                            "name": "sql_update",
                            "content": str(result)
                        })
                    elif tool.function.name == "sql_search":
                        tool_call = response.tool_calls[0]
                        arguments = tool_call.function.arguments
                        args = json.loads(arguments)

                        # 调用 sql_search，不需要 include_descrpt_search 参数
                        result = sql_search(
                            query=args.get("query", ""),  # 获取 query 参数，默认为空字符串
                            record_descrpt=args.get("record_descrpt")  # 获取 record_descrpt 参数
                        )

                        print(f"{user_id}====Filtered Records====")
                        if isinstance(result, str):
                            print(result)
                        else:
                            print_json(result)
                        chat_histories[user_id]["chat_history"].append({
                            "tool_call_id": tool.id,
                            "role": "tool",
                            "name": "sql_search",
                            "content": str(result)
                        })
                    elif tool.function.name == "thought_step":
                        tool_call = response.tool_calls[0]
                        arguments = tool_call.function.arguments
                        print(f"{user_id}====思考记录====")
                        print(arguments)
                        result = thought_step(arguments)
                        chat_histories[user_id]["chat_history"].append({
                            "tool_call_id": tool.id,
                            "role": "tool",
                            "name": "thought_step",
                            "content": str(result)
                        })
                    elif tool.function.name == "get_current_time":
                        result = get_current_time()
                        chat_histories[user_id]["chat_history"].append({
                            "tool_call_id": tool.id,
                            "role": "tool",
                            "name": "get_current_time",
                            "content": str(result)
                        })
            else:
                chat_histories[user_id]["chat_history"].append({"role": "assistant", "content": response.content})
                print(f"{user_id}=====最终回复=====")
                print(response.content)
                print(f"{user_id}=====chat_history=====")
                print_json(chat_histories[user_id]["chat_history"])
                break
        return chat_histories[user_id]["chat_history"][-1]["content"]

    return chat


def start_loop(query_value: Query):
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
        response = chat_warpper(user_id)(query_dic["query"], latitude, longitude)

    return {"Response": response, 'code': 200}


def get_lat_longit_value():
    """ TODO：优化全局对象管理，使用缓存 [ {userid, model_obejct },...] """
    return latitude, longitude


def get_user_id():
    return user_id
