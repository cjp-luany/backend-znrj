import os
from dotenv import load_dotenv

def load_env(env_file: str):
    """加载指定的环境文件"""
    load_dotenv(env_file)

def get_env_variable(key: str, default: str = None) -> str:
    """获取环境变量"""
    return os.getenv(key, default)