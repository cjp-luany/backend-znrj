# descriptions_fc.py

"""==================== thought step ===================="""

thought_step_string = """
1. 结合关键概念，我收集到什么信息？
2. 下一步我要达到什么目标？
3. 基于下一步目标我要做什么？（比如调用什么工具或是与用户沟通什么内容）
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

"""==================== get current time ===================="""

tool_get_current_time = [{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "获取当前时间与星期几",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "无需传入参数",
                },
            },
            "required": ["message"],
            "additionalProperties": False
        },
    }
}]

"""==================== get location ===================="""

tool_get_current_location = [{
    "type": "function",
    "function": {
        "name": "get_current_location",
        "description": "获取当前位置信息的经纬度",
        "parameters": {
            "type": "object",
            "properties": {
                "query_msg": {
                    "type": "string",
                    "description": "默认ask",
                },
            },
            "required": ["query_msg"],
            "additionalProperties": False
        },
    }
}]

tool_get_current_location_name = [{
    "type": "function",
    "function": {
        "name": "get_current_location_name",
        "description": "获取当前位置描述",
        "parameters": {
            "type": "object",
            "properties": {
                "query_msg": {
                    "type": "string",
                    "description": "默认ask",
                },
            },
            "required": ["query_msg"],
            "additionalProperties": False
        },
    }
}]

tool_get_location_summary = [{
    "type": "function",
    "function": {
        "name": "get_location_summary",
        "description": "查询位置信息，只传入地点描述的文本，不要传入任何其他参数。该工具已封装了用户位置信息，你无需额外获取。",
        "parameters": {
            "type": "object",
            "properties": {
                "query_msg": {
                    "type": "string",
                    "description": "将用户查询的地点的描述文本传入",
                },
            },
            "required": ["query_msg"],
            "additionalProperties": False
        },
    }
}]

"""==================== sql operation ===================="""

tool_sql_insert = [{
    "type": "function",
    "function": {
        "name": "sql_insert",
        "description": "使用此工具插入新的事件记录",
        "parameters": {
            "type": "object",
            "properties": {
                "target_time": {
                    "type": "string",
                    "description": "[目标时间]，格式DateTime为 'YYYY-MM-DD HH:MM:SS'，如果无相关信息，则为空值。"
                },
                "finish_time": {
                    "type": "string",
                    "description": "[结束时间]，格式DateTime为 'YYYY-MM-DD HH:MM:SS'，如果无相关信息，则为空值。"
                },
                "wake_time": {
                    "type": "string",
                    "description": "[提醒时间]，格式DateTime为 'YYYY-MM-DD HH:MM:SS'，如果无相关信息，则为空值。"
                },
                "record_descrpt": {
                    "type": "string",
                    "description": "[事件总结]"
                },
                "record_status": {
                    "type": "string",
                    "description": "[事件状态]，分为“未完成”/“完成”/“记事”/“取消”，不可为空值。"
                },
                "image_descrpt": {
                    "type": "string",
                    "description": "[图片描述]，如果无相关信息，则为空值。"
                },
                "image_id": {
                    "type": "string",
                    "description": "[图片ID]，如果无相关信息，则为空值。"
                },
                "record_cls": {
                    "type": "string",
                    "description": "[记录类别]，表示事件的类别。如果无相关信息，则为空值。"
                }
            },
            "required": [
                "target_time",
                "finish_time",
                "wake_time",
                "record_descrpt",
                "record_status",
                "image_descrpt",
                "image_id",
                "record_cls"
            ],
            "additionalProperties": False
        },
    }
}]

tool_sql_update = [{
    "type": "function",
    "function": {
        "name": "sql_update",
        "description": "使用此工具更新事件记录的字段，只能以记录唯一标识record_id为定位条件，支持批量更新。",
        "parameters": {
            "type": "object",
            "properties": {
                "record_ids": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "要更新的记录的唯一标识record_id列表。"
                },
                "target_time": {
                    "type": "string",
                    "description": "[目标时间]，格式为 'YYYY-MM-DD HH:MM:SS'。如果不修改此字段，可以不传此参数。"
                },
                "finish_time": {
                    "type": "string",
                    "description": "[结束时间]，格式为 'YYYY-MM-DD HH:MM:SS'。如果不修改此字段，可以不传此参数。"
                },
                "wake_time": {
                    "type": "string",
                    "description": "[提醒时间]，格式为 'YYYY-MM-DD HH:MM:SS'。如果不修改此字段，可以不传此参数。"
                },
                "record_descrpt": {
                    "type": "string",
                    "description": "[事件总结]。如果不修改此字段，可以不传此参数。"
                },
                "record_status": {
                    "type": "string",
                    "description": "[事件状态]，分为“未完成”/“完成”/“记事”/“取消”。如果不修改此字段，可以不传此参数。"
                },
                "image_descrpt": {
                    "type": "string",
                    "description": "[图片描述]，如果不修改此字段，可以不传此参数。"
                },
                "record_cls": {
                    "type": "string",
                    "description": "[记录类别]，表示事件的类别。如果不修改此字段，可以不传此参数。"
                }
            },
            "required": ["record_ids"],
            "additionalProperties": False
        },
    }
}]

"""==================== sql search ===================="""

database_update_schema_string = """
    --记录列名：record_cls，格式：STR，描述：[记录类别],包含会议、记录、待办、想法
    --记录列名：record_time，格式：DATETIME，描述：一件事被用户记录的时间,格式为YYYY-MM-DD hh:mm:ss
    --记录列名：record_location_name，格式：STR，描述：一件事被用户记录的地点,格式为STR
    --记录列名：target_time，格式：DATETIME，描述：用户计划做某件事的目标时间,格式为YYYY-MM-DD hh:mm:ss
    --记录列名：finish_time，格式：DATETIME，描述：某件事开始后结束的时间,格式为YYYY-MM-DD hh:mm:ss
    --记录列名：wake_time，格式：DATETIME，描述：用户为某个记录设定的提醒时间,格式为YYYY-MM-DD hh:mm:ss
    --记录列名：record_descrpt，格式：STR，描述：事件的总结描述
    --记录列名：record_status，格式：STR，描述：[事件状态]，分为“未完成”/“完成”/“记事”/“取消”
    --记录列名：image_descrpt，格式：STR，描述：[图片描述]，如用户未提及则为Null"""

tool_sql_search = [{
    "type": "function",
    "function": {
        "name": "sql_search",
        "description": "在数据库中根据用户的查询条件返回符合条件的记录描述。工具会根据查询内容自动选择合适的查询路径（SQL查询或RAG召回），并最终返回格式化的记录描述。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                        用户查询条件中事件描述以外的部分（例如时间、地点、状态等）。该字段应仅包含WHERE子句中的条件内容。
                        如果用户只提供了事件描述，则此字段可以为空。数据库结构为{database_update_schema_string}。
                    """,
                },
                "record_descrpt": {
                    "type": "string",
                    "description": """
                        用户查询中的事件描述部分。如果用户提供了事件描述内容（例如查询有没有关于什么的事情，有没有人欠我钱等），系统会使用RAG路径查找与该描述最相似的记录。
                        如果事件描述与其他查询条件同时存在，系统会将两者组合以进行最终查询。
                    """,
                }
            },
            "required": [],
            "additionalProperties": False
        },
    }
}]
