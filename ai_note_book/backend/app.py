from dotenv import load_dotenv
from crud.start import start as crud_start

# 加载当前目录下的 .env 文件
load_dotenv()

if __name__ == '__main__':
    print('Start znrj service...')
    import threading

    crud_thread = threading.Thread(target=crud_start)
    crud_thread.start()
