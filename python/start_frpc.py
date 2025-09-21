# start_frpc.py
import subprocess
import sys
import os

if __name__ == "__main__":
    # 获取命令行参数中的frpc路径
    if len(sys.argv) < 2:
        print("请提供frpc可执行文件的路径")
        sys.exit(1)
    
    frpc_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(frpc_path):
        print(f"指定的frpc路径不存在: {frpc_path}")
        sys.exit(1)
    
    # 获取剩余的参数作为frpc的参数
    frpc_args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # 执行 frpc 带有特定参数
    try:
        result = subprocess.run([frpc_path] + frpc_args)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"执行frpc时出错: {e}")
        sys.exit(1)