from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from tools.tools_general import *
from tools.tools_sql_operate import *
from tools.tools_thought import *
from tools.tools_location import *
import uvicorn
from threading import Thread
from pydantic import BaseModel
from api import RecordItem,run_fastapi2
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import threading 
# 数据库连接
# 数据库连接
CUR_DIR = os.path.realpath(os.path.dirname(__file__))
# PARENT_DIR = os.path.dirname(CUR_DIR)
JOIN_DIR = os.path.join(CUR_DIR, "sqlite.db")
DATABASE_URL = "sqlite:///" + JOIN_DIR  # 这里的路径应该是你的数据库文件的路径
# DATABASE_URL = "sqlite:////Users/yuanchaoyi/Documents/Ai项目/ai_note_book v1.0/sqlite.db"
SERVER_URL = "47.115.151.97"
# AnythingLLM_TOKEN = "7VAHKHX-N434531-P33SCGE-QBNHSGJ" # this is localhost anything llm token
ANYTHINGLLM_TOKEN = "A6WW35F-A6RMWBH-PWRQJV3-5DT5DYS"  # this is server anything llm token
ISRAG_WORKSPACE_NAME = "israg"
NORAG_WORKSPACE_NAME = "norag"
# 加载 .env 文件中定义的环境变量
_ = load_dotenv(find_dotenv())


# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)
# 创建会话
Session = sessionmaker(bind=engine)
session = Session()
api = FastAPI()

# 创建对话服务
client = OpenAI()
# 写入提示内容
with open(os.path.join(CUR_DIR, "prompt/tools.txt"), 'r', encoding='utf-8') as file:
    system_message_content = file.read()

tools = tools_thought + tools_general + tools_rag_sql
# system_message_content=system_message_content.format(tools=tools)

chat_history = [{"role": "system", "content": system_message_content}]

api = FastAPI()
def get_completion(messages, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        tools=tools,
    )
    return response.choices[0].message

clear_timer = None

def clear_chat_history():
    global chat_history
    print("5分钟内无回复，清空聊天记录...")
    # 只保留system部分
    chat_history = [{"role": "system", "content": system_message_content}]
    print("chat_history已清空")

def reset_clear_timer():
    global clear_timer
    if clear_timer:
        clear_timer.cancel()
    # 5分钟（300秒）后清空聊天记录
    clear_timer = threading.Timer(300, clear_chat_history)
    clear_timer.start()

# def chat_warpper(tool_history:list):

def chat(user_input,latitude,longitude):
    # query_during_chat() # 对话中查询，使用服务器rag
    reset_clear_timer()
    message = {"role": "user", "content": user_input}
    chat_history.append(message)
    # 调用GPT-4模型
    while True:
        print("=====本轮回复=====")
        response = get_completion(chat_history)
        print_json(response)
        if response.content is None:
            response.content = ""
        chat_history.append(response)
        if response.tool_calls:
            # Loop through each tool in the required action section
            for tool in response.tool_calls:
                if tool.function.name == "get_time":
                    # tool_history.append("get_time")
                    result = get_time()
                    print("====记录时间====")
                    print(result)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "get_time",
                        "content": str(result)
                    })
                elif tool.function.name == "get_week_day":
                    result = get_week_day()
                    print("====记录时间====")
                    print(result)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "get_week_day",
                        "content": str(result)
                    })
                elif tool.function.name == "get_key":
                    tool_call = response.tool_calls[0]
                    result = get_key()
                    print("====key id====")
                    print_json(result)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "get_key",
                        "content": str(result)
                    })
                elif tool.function.name == "get_current_location":
                    result = get_current_location()
                    print("====记录坐标====")
                    print(result)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "get_current_location",
                        "content": str(result)
                    })
                elif tool.function.name == "get_current_location_name":
                    result = get_current_location_name()
                    print("====记录位置====")
                    print(result)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "get_current_location_name",
                        "content": str(result)
                    })
                elif tool.function.name == "get_location_summary":
                    tool_call = response.tool_calls[0]
                    arguments = tool_call.function.arguments
                    print("====查询的目标====")
                    print(arguments)
                    result = get_location_summary(arguments)
                    print("====返回的地址信息====")
                    print(result)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "get_location_summary",
                        "content": str(result)
                    })
                elif tool.function.name == "sql_operate":
                    tool_call = response.tool_calls[0]
                    arguments = tool_call.function.arguments
                    args = json.loads(arguments)
                    print("====SQL====")
                    print(args["query"])
                    result = sql_operate(args["query"])
                    print("====结果====")
                    print(result)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "sql_operate",
                        "content": str(result)
                    })
                elif tool.function.name == "sql_search":
                    tool_call = response.tool_calls[0]
                    arguments = tool_call.function.arguments
                    args = json.loads(arguments)
                    print("====SQL====")
                    print(args["user_input"])
                    result = sql_search(args["user_input"])
                    print("====DB Records====")
                    print(result)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "sql",
                        "content": str(result)
                    })
                elif tool.function.name == "sql_get_summarized":
                    tool_call = response.tool_calls[0]
                    arguments = tool_call.function.arguments
                    args = json.loads(arguments)
                    print("====SQL====")
                    print(args["query"])
                    result = sql_get_summarized(args["query"])
                    print("====Filtered Records====")
                    print_json(result)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "sql_get_summarized",
                        "content": str(result)
                    })
                elif tool.function.name == "sql_all_summarized":
                    result = sql_all_summarized()
                    print("====all Records====")
                    print_json(result)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "sql_all_summarized",
                        "content": str(result)
                    })
                elif tool.function.name == "rag":
                    tool_call = response.tool_calls[0]
                    arguments = tool_call.function.arguments
                    print("====查询内容====")
                    print(arguments)
                    result = read_data_rec(arguments)
                    print("====查询结果====")
                    print(result)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "rag",
                        "content": str(result)
                    })
                # elif tool.function.name == "thought_summarize":
                #     tool_call = response.tool_calls[0]
                #     arguments = tool_call.function.arguments
                #     print("====思考内容====")
                #     print(arguments)
                #     result = thought_summarize(arguments)
                #     chat_history.append({
                #         "tool_call_id": tool.id,
                #         "role": "tool",
                #         "name": "tool_thought_summarize",
                #         "content": str(result)
                #     })
                elif tool.function.name == "thought_step":
                    tool_call = response.tool_calls[0]
                    arguments = tool_call.function.arguments
                    print("====思考记录====")
                    print(arguments)
                    result = thought_step(arguments)
                    chat_history.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": "thought_step",
                        "content": str(result)
                    })

        else:
            chat_history.append({"role": "assistant", "content": response.content})
            print("=====最终回复=====")
            print(response.content)
            print("=====chat_history=====")
            print_json(chat_history)
            break
    return chat_history[-1]["content"]





latitude = 0
longitude = 0
user_id ="TODO:"

class Query(BaseModel):
    query:str 
    latitude:str
    longitude:str

tool_historys = {"auser":[]}

@api.get("/now_at")
def _():
    return tool_historys[user_id]

@api.post("/query/")
def start_loop(query_value:Query):
    tool_history = []
    # question = "明天早上8点开会"
    query_dic = query_value.dict()
    global latitude
    global longitude
    print(query_dic)
    if "query" not in query_dic:
        current_location = get_current_location(query_dic['latitude'],query_dic['longitude'])
        latitude = query_dic['latitude']
        longitude = query_dic['longitude']
    elif "query" in query_dic:
        latitude = query_dic['latitude']
        longitude = query_dic['longitude']
        response = chat(query_dic["query"], query_dic['latitude'], query_dic['longitude'])
        # response = chat_warpper(tool_history[user_id])(query_dic["query"],query_dic['latitude'],query_dic['longitude'])
    # Example use
    # print(response)
    return {"Response":response,'code':200}


@api.get("/get_lat_longit/")
def get_lat_longit_value():
    return latitude,longitude


def run_fastapi():
    uvicorn.run(api, host="0.0.0.0", port=6202, loop="asyncio")


# cors名单
origins = [
"*",
    "http://127.0.0.1:8102",
    "http://localhost:61476",
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

# =====================console测试=======================
if __name__ == '__main__':
    # Accept command line input and output results
    # while True:
    #     question = input("请输入内容: ")
    #     # question = ""
    #     if question.lower() == 'q':
    #         print("退出程序")
    #         break
    #     # 30.467467,104.0169
    #     # chat_history.extend([HumanMessage(content=question)])
    #     chat(question,latitude=40.119346,longitude=116.266543)
# =====================console测试=======================

# =====================连前端=======================

# class Query(BaseModel):
#     query:str
#
#
# @api.post("/query/")
# def start_loop(query_value:Query):
#     query_dic = query_value.dict()
#     response = chat(query_dic["query"])
#     print(response)
#     # return {"Response":response}
#     return {
#         "data" : response,
#         "code" : 200
#     }

 
#         # 启动fastapi
    thread_fast = Thread(target=run_fastapi)
    thread_fast.start()
#
    thread_test = Thread(target=run_fastapi2)
    thread_test.start()
# =====================连前端=======================