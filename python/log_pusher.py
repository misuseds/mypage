import asyncio
import websockets
import json
from pathlib import Path

LOG_FILES = {
    "mouse_control": "E:/llm-findwork/logs/mouse_control.log",
    "llm_server": "E:/llm-findwork/logs/llm_server.log",
    "yolo_server": "E:/llm-findwork/logs/yolo_server.log",
    "index_server": "E:/llm-findwork/logs/index_server.log",
    "frp_client": "E:/llm-findwork/logs/frp_client.log"
}

async def log_pusher(websocket, path):
    # 为每个连接创建日志监听任务
    tasks = []
    for service, log_file in LOG_FILES.items():
        task = asyncio.create_task(tail_log(service, log_file, websocket))
        tasks.append(task)
    
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f"日志推送异常: {e}")
    finally:
        for task in tasks:
            task.cancel()

async def tail_log(service, log_file, websocket):
    """实时读取日志文件并推送"""
    file_path = Path(log_file)
    if not file_path.exists():
        file_path.touch()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        # 移动到文件末尾
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                await websocket.send(json.dumps({
                    "service": service,
                    "log": line.strip()
                }))
            else:
                await asyncio.sleep(0.1)

# 启动WebSocket服务器
start_server = websockets.serve(log_pusher, "127.0.0.1", 5678)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()