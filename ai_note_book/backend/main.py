import signal
import subprocess
import os
import sys

from dotenv import load_dotenv
import asyncio

# 加载根目录下的 .env 文件
load_dotenv()

def start_service_llm():
    python_path = os.getenv("PYTHON_SYSTEM_PATH", "python")
    # env["PYTHONPATH"] = "./common"
    subprocess.Popen([python_path, "llm_service/main.py"])

def start_service_mobile():
    python_path = os.getenv("PYTHON_SYSTEM_PATH", "python")
    # env["PYTHONPATH"] = "./common"
    subprocess.Popen([python_path, "mobile_service/main.py"])


async def start_service_llm():
    python_path = os.getenv("PYTHON_SYSTEM_PATH", "python")

    # 启动子进程，异步执行
    process = await asyncio.create_subprocess_exec(
        python_path, "llm_service/main.py",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    async def handle_stream(stream, name):
        while True:
            line = await stream.readline()
            if line:
                print(f"{name}: {line.decode().rstrip()}")
            else:
                break

    # 创建任务来处理 stdout 和 stderr
    stdout_task = asyncio.create_task(handle_stream(process.stdout, 'STDOUT'))
    stderr_task = asyncio.create_task(handle_stream(process.stderr, 'STDERR'))

    # 不等待子进程结束，函数立即返回
    # 可选择性地存储任务以防止被垃圾回收
    return process, stdout_task, stderr_task


async def start_service_mobile():
    python_path = os.getenv("PYTHON_SYSTEM_PATH", "python")

    # 启动子进程，异步执行
    process = await asyncio.create_subprocess_exec(
        python_path, "mobile_service/main.py",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    async def handle_stream(stream, name):
        while True:
            line = await stream.readline()
            if line:
                print(f"{name}: {line.decode().rstrip()}")
            else:
                break

    # 创建任务来处理 stdout 和 stderr
    stdout_task = asyncio.create_task(handle_stream(process.stdout, 'STDOUT'))
    stderr_task = asyncio.create_task(handle_stream(process.stderr, 'STDERR'))

    # 不等待子进程结束，函数立即返回
    # 可选择性地存储任务以防止被垃圾回收
    return process, stdout_task, stderr_task


# def start_selected_services(services):
#
#     """根据配置启动选定的服务"""
#     for service in services:
#         if service == "llm":
#             # asyncio.run(start_service_mobile())
#             loop = asyncio.get_event_loop()
#             loop.create_task(start_service_llm())
#             # 主程序的其他逻辑
#             try:
#                 loop.run_forever()
#             except KeyboardInterrupt:
#                 pass
#         elif service == "mobile":
#             # asyncio.run(start_service_mobile())
#             loop = asyncio.get_event_loop()
#             loop.create_task(start_service_mobile())
#             # 主程序的其他逻辑
#             try:
#                 loop.run_forever()
#             except KeyboardInterrupt:
#                 pass
#
#
#
#
# if __name__ == "__main__":
#    # 配置要启动的服务
#     services_to_start = ["mobile"]  # 可以从配置文件或环境变量中读取
#
#     start_selected_services(services_to_start)
#     print("Selected services are starting...")




async def start_service(service_name, script_path):
    """
    启动指定服务的子进程并处理其输出。

    :param service_name: 服务名称
    :param script_path: 服务脚本路径
    :return: 启动的子进程
    """
    python_path = os.getenv("PYTHON_SYSTEM_PATH", "python")

    try:
        # 启动子进程，异步执行
        process = await asyncio.create_subprocess_exec(
            python_path, script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        async def handle_stream(stream, name):
            while True:
                line = await stream.readline()
                if line:
                    print(f"[{service_name}][{name}]: {line.decode().rstrip()}")
                else:
                    break

        # 创建任务来处理 stdout 和 stderr
        asyncio.create_task(handle_stream(process.stdout, 'STDOUT'))
        asyncio.create_task(handle_stream(process.stderr, 'STDERR'))

        return process

    except Exception as e:
        print(f"[{service_name}] 启动失败: {e}")
        return None

async def start_selected_services(services):
    """
    根据配置启动选定的服务。

    :param services: 服务名称的列表
    :return: 启动的子进程列表
    """
    service_scripts = {
        "llm": "llm_service/main.py",
        "mobile": "mobile_service/main.py"
    }

    processes = []

    for service in services:
        script_path = service_scripts.get(service.lower())
        if script_path:
            process = await start_service(service, script_path)
            if process:
                processes.append((service, process))
        else:
            print(f"未知的服务: {service}")

    return processes

def terminate_processes(processes):
    """
    终止所有子进程。

    :param processes: 启动的子进程列表
    """
    for service, process in processes:
        if process.returncode is None:
            print(f"[{service}] 正在终止，PID: {process.pid}")
            process.terminate()

async def main():
    # 配置要启动的服务
    services_to_start = ["mobile"]  # 可以从配置文件或环境变量中读取

    # 启动选定的服务
    processes = await start_selected_services(services_to_start)
    print("Selected services are starting...")

    try:
        # 等待所有子进程结束
        await asyncio.gather(*(process.wait() for _, process in processes))
    except KeyboardInterrupt:
        print("程序被中断，正在终止所有服务...")
        terminate_processes(processes)

        # 等待所有子进程结束
        for service, process in processes:
            try:
                await process.wait()
                print(f"[{service}] 已终止，退出码: {process.returncode}")
            except Exception as e:
                print(f"[{service}] 终止时出错: {e}")

    print("所有服务已关闭。")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("程序被中断")