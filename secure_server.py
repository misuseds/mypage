import http.server
import socketserver
import os
import urllib.parse
from pathlib import Path

# 配置端口
PORT = 8000

# 定义允许访问的文件列表
ALLOWED_FILES = [
    'index.html',
    'job-finder.html',
    'bookroom.html',
    'camera_solve.html',
    'ipadxz.html',
    'ai_terminal.html',
    'Repentance_room.html',
    '图片/558046.png',
    'favicon.ico',
    '音频/蓝手帕.mp3'

    # 可以根据需要添加其他文件
]

class SecureHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 解析请求路径
        parsed_path = urllib.parse.unquote(self.path)
        if parsed_path == '/':
            parsed_path = '/index.html'
        
        # 获取文件名（移除前导斜杠）
        filename = parsed_path.lstrip('/')
        
        # 检查文件是否在允许列表中
        if filename not in ALLOWED_FILES:
            print(f"尝试访问被拒绝的文件: {filename}")  # 添加这行来显示被拒绝的文件
            self.send_error(403, "Forbidden: You don't have permission to access this file")
            return
        
        # 检查文件是否存在
        filepath = os.path.join(os.getcwd(), filename)
        if not os.path.exists(filepath):
            self.send_error(404, "File not found")
            return
        
        # 防止路径遍历攻击
        if not os.path.abspath(filepath).startswith(os.path.abspath(os.getcwd())):
            self.send_error(403, "Forbidden: Access denied")
            return
        
        # 调用父类方法处理文件请求
        super().do_GET()
    
    def translate_path(self, path):
        # 重写路径转换方法，限制只能访问当前目录下的文件
        path = urllib.parse.unquote(path)
        if path == '/':
            path = '/index.html'
        
        filename = path.lstrip('/')
        if filename in ALLOWED_FILES:
            return os.path.join(os.getcwd(), filename)
        else:
            # 返回一个不存在的路径，让处理函数返回404
            return os.path.join(os.getcwd(), "forbidden")

# 创建服务器
with socketserver.TCPServer(("", PORT), SecureHTTPRequestHandler) as httpd:
    print(f"安全服务器运行在端口 {PORT}")
    print("允许访问的文件:")
    for file in ALLOWED_FILES:
        print(f"  - {file}")
    print("按 Ctrl+C 停止服务器")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")