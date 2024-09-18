import random
import string
import time


def get_key():
    characters = string.ascii_letters + string.digits
    random_key = ''.join(random.choices(characters, k=11))
    return random_key


# 生成数字形式id
def python_get_now_timespan():
    # return int(time.time())
    return int(time.time().__str__()[:-3].replace(".", ""))
