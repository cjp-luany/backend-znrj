import pytest
import asyncio
import pytest_asyncio
import httpx

BASE_URL = "http://127.0.0.1:6201"  # FastAPI 应用的地址


async def aaa():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weekItems", timeout=5)
        assert isinstance(response.json(), dict)  # 检查返回值是否为字典
        assert "data" in response.json()  # 检查返回值中是否包含 "data" 键


def test_sum_of_squares():
    asyncio.run(aaa())


# async def main():
#     import pytest
#     pytest.main([__file__])  # pytest测试当前文件
#

# if __name__ == '__main__':
#     asyncio.run(main())



# async def main(n_tasks: int) -> None:
#
#     print("Task #\tTime")
#     print("-------------")
#
#     task = asyncio.create_task(test_sum_of_squares())
#     await task
#
# if __name__ == "__main__":
#     asyncio.run(main())


""" 单元测试各个接口 
    使用方法：
        - 先运行app.py
        - 在测试文件，鼠标点击要测试的函数名左侧绿色三角，有运行和调试两个选项
        - 选择运行 xxx.py 测试文件
"""