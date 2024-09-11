from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from tools.tools_general import *
from tools.tools_sql_operate import *
from tools.tools_thought import *
from tools.tools_location import *
from tools.tools_search import *
import uvicorn
from threading import Thread
from pydantic import BaseModel
from api import run_fastapi2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading 
from flask import Flask, render_template, send_from_directory


# 数据库连接
CUR_DIR = os.path.realpath(os.path.dirname(__file__))
JOIN_DIR = os.path.join(CUR_DIR, "sqlite.db")
DATABASE_URL = "sqlite:///" + JOIN_DIR
SERVER_URL = "47.115.151.97"
ANYTHINGLLM_TOKEN = "A6WW35F-A6RMWBH-PWRQJV3-5DT5DYS"
ISRAG_WORKSPACE_NAME = "israg"
NORAG_WORKSPACE_NAME = "norag"
_ = load_dotenv(find_dotenv())

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()
api = FastAPI()

client = OpenAI()
with open(os.path.join(CUR_DIR, "prompt/agent_prompt.txt"), 'r', encoding='utf-8') as file:
    system_message_content = file.read()

tools = tools_thought + tools_general + tools_sql_operate + tool_sql_search

chat_histories = {}

def get_completion(messages, model="qwen-plus"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        tools=tools,
    )
    return response.choices[0].message

def clear_chat_history(user_id):
    if user_id in chat_histories:
        print(f"5分钟内无回复，清空用户 {user_id} 的聊天记录...")
        chat_histories[user_id] = [{"role": "system", "content": system_message_content}]
        print(f"用户 {user_id} 的 chat_history 已清空")

def reset_clear_timer(user_id):
    if user_id in chat_histories:
        if chat_histories[user_id].get('timer'):
            chat_histories[user_id]['timer'].cancel()
        chat_histories[user_id]['timer'] = threading.Timer(300, clear_chat_history, args=[user_id])
        chat_histories[user_id]['timer'].start()

def chat_warpper(user_id):
    if user_id not in chat_histories:
        chat_histories[user_id] = {
            "chat_history": [{"role": "system", "content": system_message_content}],
            "timer": None
        }

    def chat(user_input, latitude, longitude):
        reset_clear_timer(user_id)
        message = {"role": "user", "content": user_input}
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

                    if tool.function.name == "sql_insert":  # 新添加的elif条件
                        tool_call = response.tool_calls[0]
                        arguments = tool_call.function.arguments
                        args = json.loads(arguments)
                        print(f"{user_id}====SQL INSERT====")
                        print(args)
                        result = sql_insert(
                            record_cls=args["record_cls"],
                            target_time=args["target_time"],
                            target_location_name=args["target_location_name"],
                            target_location=args["target_location"],
                            finish_time=args["finish_time"],
                            wake_time=args["wake_time"],
                            wake_location_name=args["wake_location_name"],
                            wake_location=args["wake_location"],
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
                            where_conditions=args["where_conditions"],
                            target_time=args.get("target_time"),
                            target_location_name=args.get("target_location_name"),
                            target_location=args.get("target_location"),
                            finish_time=args.get("finish_time"),
                            wake_time=args.get("wake_time"),
                            wake_location_name=args.get("wake_location_name"),
                            wake_location=args.get("wake_location"),
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
                    # elif tool.function.name == "get_week_day":
                    #     result = get_week_day()
                    #     chat_histories[user_id]["chat_history"].append({
                    #         "tool_call_id": tool.id,
                    #         "role": "tool",
                    #         "name": "get_week_day",
                    #         "content": str(result)
                    #     })
                    # elif tool.function.name == "get_key":
                    #     result = get_key()
                    #     print(f"{user_id}====key id====")
                    #     print_json(result)
                    #     chat_histories[user_id]["chat_history"].append({
                    #         "tool_call_id": tool.id,
                    #         "role": "tool",
                    #         "name": "get_key",
                    #         "content": str(result)
                    #     })
                    # elif tool.function.name == "get_current_location":
                    #     result = get_current_location()
                    #     print(f"{user_id}====记录坐标====")
                    #     print(result)
                    #     chat_histories[user_id]["chat_history"].append({
                    #         "tool_call_id": tool.id,
                    #         "role": "tool",
                    #         "name": "get_current_location",
                    #         "content": str(result)
                    #     })
                    # elif tool.function.name == "get_current_location_name":
                    #     result = get_current_location_name()
                    #     print(f"{user_id}====记录位置====")
                    #     print(result)
                    #     chat_histories[user_id]["chat_history"].append({
                    #         "tool_call_id": tool.id,
                    #         "role": "tool",
                    #         "name": "get_current_location_name",
                    #         "content": str(result)
                    #     })
                    # elif tool.function.name == "get_location_summary":
                    #     tool_call = response.tool_calls[0]
                    #     arguments = tool_call.function.arguments
                    #     print(f"{user_id}====查询的目标====")
                    #     print(arguments)
                    #     result = get_location_summary(arguments)
                    #     print(f"{user_id}====返回的地址信息====")
                    #     print(result)
                    #     chat_histories[user_id]["chat_history"].append({
                    #         "tool_call_id": tool.id,
                    #         "role": "tool",
                    #         "name": "get_location_summary",
                    #         "content": str(result)
                    #     })
                    # elif tool.function.name == "sql_operate":
                    #     tool_call = response.tool_calls[0]
                    #     arguments = tool_call.function.arguments
                    #     args = json.loads(arguments)
                    #     print(f"{user_id}====SQL====")
                    #     print(args["query"])
                    #     result = sql_operate(args["query"])
                    #     print(f"{user_id}====结果====")
                    #     print(result)
                    #     chat_histories[user_id]["chat_history"].append({
                    #         "tool_call_id": tool.id,
                    #         "role": "tool",
                    #         "name": "sql_operate",
                    #         "content": str(result)
                    #     })
                    # elif tool.function.name == "sql_search_summarized":
                    #     tool_call = response.tool_calls[0]
                    #     arguments = tool_call.function.arguments
                    #     args = json.loads(arguments)
                    #
                    #     # 打印传入的查询条件
                    #     print(f"{user_id}====SQL====")
                    #     print(args["query"])
                    #
                    #     # 调用 sql_get_summarized 函数，并打印结果
                    #     result = sql_search_summarized(args["query"])
                    #
                    #     print(f"{user_id}====Filtered Records====")
                    #     print_json(result)
                    #
                    #     # 将结果添加到聊天历史中
                    #     chat_histories[user_id]["chat_history"].append({
                    #         "tool_call_id": tool.id,
                    #         "role": "tool",
                    #         "name": "sql_search_summarized",
                    #         "content": str(result)
                    #     })
                    #
                    # elif tool.function.name == "sql_all_summarized":
                    #     result = sql_all_summarized()
                    #     print(f"{user_id}====all Records====")
                    #     print_json(result)
                    #     chat_histories[user_id]["chat_history"].append({
                    #         "tool_call_id": tool.id,
                    #         "role": "tool",
                    #         "name": "sql_all_summarized",
                    #         "content": str(result)
                    #     })
            else:
                chat_histories[user_id]["chat_history"].append({"role": "assistant", "content": response.content})
                print(f"{user_id}=====最终回复=====")
                print(response.content)
                print(f"{user_id}=====chat_history=====")
                print_json(chat_histories[user_id]["chat_history"])
                break
        return chat_histories[user_id]["chat_history"][-1]["content"]
    return chat

latitude = 0
longitude = 0
user_id ="TODO:"

class Query(BaseModel):
    query: str
    latitude: str
    longitude: str
    user_id: str

@api.post("/query/")
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

@api.get("/get_lat_longit/")
def get_lat_longit_value():
    return latitude, longitude

@api.get("/get_user_id/")
def get_user_id():
    return user_id


def run_fastapi():
    uvicorn.run(api, host="0.0.0.0", port=6202, loop="asyncio")

# cors名单
origins = [
"*",
    "http://127.0.0.1:8102",
    "http://localhost:51296",
    "http://127.0.0.1:6102",
    "http://127.0.0.1:6201",
    "http://127.0.0.1:6200",
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

'''
是否使用flask
'''
# 创建flask实例，指定静态文件夹
app = Flask(__name__,
            static_folder=os.path.join(CUR_DIR, 'static'),
            template_folder=os.path.join(CUR_DIR, 'templates'))
# 启动flask
def run_flask():
    app.run(host='0.0.0.0', port=6200)

# 路由控制
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# =====================console测试=======================
if __name__ == '__main__':
    # 启动fastapi
    thread_fast = Thread(target=run_fastapi)
    thread_fast.start()

    thread_test = Thread(target=run_fastapi2)
    thread_test.start()

    thread_flask = Thread(target=run_flask)
    thread_flask.start()
# =====================连前端=======================

