
summarize_thought_string = """
    总结思路方式：
        当[类别]为“记事”：
        - 记录时间=[记录时间]
        - 目标时间=“null”
        - 结束时间=“null”
        - 提醒时间=“null”
        - 事件总结=“[事件总结]”
        - 状态=“已完成”。
        当[类别]为“会议”或“待办”：
        - 记录时间=[记录时间]
        - 目标时间=[开始时间]
        - 结束时间=[结束时间]，如用户未提供，则默认[目标时间]的后1小时
        - 提醒时间=[提醒时间]，如用户未提供，则默认[目标时间]的前15分钟
        - 事件总结=“[事件总结]”，如果[类别]是“会议”，则其中需要体现[会议主题]
        - 状态=“未完成”。
"""


def thought_summarize(query):
    return query


tool_thought_summarize = [{
    "type": "function",
    "function": {
        "name": "thought_summarize",
        "description": "总结",
        "parameters": {
            "type": "object",
            "properties": {
                "query_msg": {
                    "type": "string",
                    "description": f"""
                        按此summarize_thought模板输出内容:
                        {summarize_thought_string}
                        输出必须完全以string形式.
                        """,
                },
            },
            "required": ["query"],
            "additionalProperties": False
        },
    }
}]


def thought_step(query):
    return query


thought_step_string = """
1. 关键概念：思考基于#关键概念定义所列出的[关键概念]，你取得了哪些关键概念。
同时可能存在多个事件，你应使用事件编号进行区分。
每个事件会存在多个关键概念，输出例子如下：
2. 下一步目标：基于#条件判断以及当前取得的关键概念，思考你下一步要取得什么信息？以纯文本描述输出。
3. 下一步动作：基于目标，思考你下一步要做什么动作？比如与用户沟通什么信息，或是调用哪个工具？以纯文本描述输出。
以上3点的输出将作为thought_step工具的输入。
输入例子：
「
关键概念：（1#事件，[用户意图]=“记录”，[记录类别]=“会议/记事/待办与想法”，[事件总结]=“关于xxx的会议”，[目标时间]=“2024-08-02 19:00:00”，[提醒时间]=“2024-08-02 20:00:00”，[提醒时间]=“2024-08-02 18:45:00”，[事件状态]=“未完成”），（2#事件。。。。。。。。。）
下一步目标：我要获取[记录时间]
下一步动作：我要调用get_time工具
」
"""

tool_thought_step = [{
    "type": "function",
    "function": {
        "name": "thought_step",
        "description": "记录每一次交互后的思路，固定每次收到新信息均需调用",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": """
                        按以下标准模板思考，并一步步输出每一项:
                        1. 关键概念：思考基于#关键概念定义所列出的[关键概念]，你取得了哪些关键概念。
                        同时可能存在多个事件，你应使用事件编号进行区分。
                        每个事件会存在多个关键概念，输出例子如下：
                        2. 下一步目标：基于#条件判断以及当前取得的关键概念，思考你下一步要取得什么信息？以纯文本描述输出。
                        3. 下一步动作：基于目标，思考你下一步要做什么动作？比如与用户沟通什么信息，或是调用哪个工具？以纯文本描述输出。
                        以上3点的输出将作为thought_step工具的输入。
                        输入例子：
                        「
                        关键概念：（1#事件，[用户意图]=“记录”，[记录类别]=“会议/记事/待办与想法”，[事件总结]=“关于xxx的会议”，[目标时间]=“2024-08-02 19:00:00”，[提醒时间]=“2024-08-02 20:00:00”，[提醒时间]=“2024-08-02 18:45:00”，[事件状态]=“未完成”），（2#事件。。。。。。。。。）
                        下一步目标：我要获取[记录时间]
                        下一步动作：我要调用get_time工具
                        」
                        """,
                },
            },
            "required": ["query"],
            "additionalProperties": False
        },
    }
}]


def thought_key_record(query):
    return query


tools_thought = tool_thought_step
