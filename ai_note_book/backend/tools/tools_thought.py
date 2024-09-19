
thought_step_string = """
1. 结合关键概念，我收集到什么信息？
2. 下一步我要达到什么目标？
3. 基于下一步目标我要做什么？（比如调用什么工具或是与用户沟通什么内容）
"""




def thought_step(query):
    return query


tool_thought_step = [{
    "type": "function",
    "function": {
        "name": "thought_step",
        "description": "调用thought_step工具进行思考，记录每一次交互后的思路，固定每次收到新信息均需调用",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                        按以下标准模板思考，并一步步输出每一项:
                        {thought_step_string}
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