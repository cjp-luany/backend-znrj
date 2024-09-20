from service.descriptions import *

fc_thought_step = tool_thought_step
fc_get_current_time = tool_get_current_time
fc_get_current_location = tool_get_current_location
fc_get_current_location_name = tool_get_current_location_name
fc_get_location_summary = tool_get_location_summary
fc_sql_insert = tool_sql_insert
fc_sql_search = tool_sql_search
fc_sql_update = tool_sql_update

"""
    Function Call 必须在对应目录下实现函数名
    注意：这里具体函数的实现我放到了调用方的脚本中，比如实现sql insert放到chat中，实现sql search放到search中
    调试过这是可以的，原理是读取大模型回复的tool对象，拆解获取tool名再去调用自己实现的函数
"""


def thought_step(query):
    pass


def get_current_time(message):
    pass


def get_current_location(message):
    pass


def get_current_location_name(message):
    pass


def get_location_summary(message):
    pass


def sql_insert(message):
    pass


def sql_search(message):
    pass


def sql_update(message):
    pass
