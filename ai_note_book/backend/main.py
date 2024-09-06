import subprocess
import os
from dotenv import load_dotenv

# 加载根目录下的 .env 文件
load_dotenv()

def start_service_llm():
    env = os.environ.copy()
    # 从 .env 文件中获取 PYTHON_SYSTEM_PATH
    python_path = env.get("PYTHON_SYSTEM_PATH", "python")
    # env["PYTHONPATH"] = "./common"
    subprocess.Popen([python_path, "llm_service/main.py"])

def start_service_mobile():
    env = os.environ.copy()
    # 从 .env 文件中获取 PYTHON_SYSTEM_PATH
    python_path = env.get("PYTHON_SYSTEM_PATH", "python")
    # env["PYTHONPATH"] = "./common"
    subprocess.Popen([python_path, "mobile_service/main.py"])


def start_selected_services(services):
    """根据配置启动选定的服务"""
    for service in services:
        if service == "llm":
            start_service_llm()
        elif service == "mobile":
            start_service_mobile()

if __name__ == "__main__":
   # 配置要启动的服务
    services_to_start = ["llm", "mobile"]  # 可以从配置文件或环境变量中读取

    start_selected_services(services_to_start)
    print("Selected services are starting...")