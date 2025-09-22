# secure_server.py
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import urllib.parse
from pathlib import Path
import logging
import sys
import argparse
import json
import shutil
import uuid
from datetime import datetime

# 配置端口
PORT = 8000

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--log-file', help='日志文件路径')
args = parser.parse_args()

# 配置日志
if args.log_file:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(args.log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# 定义允许访问的文件列表
ALLOWED_FILES = [
    'index.html',
    'favicon.ico',
    # 可以根据需要添加其他文件
]

# 定义允许访问的文件夹列表
ALLOWED_FOLDERS = [
    'html',
    'picture',
    'voice',
    'log',
    'logs',
    'readingroom'  # 添加readingroom文件夹以支持读书室功能
]

app = Flask(__name__)
CORS(app)  # 启用CORS支持

def is_path_allowed(filename):
    """
    检查文件路径是否被允许访问
    """
    # 检查文件是否在允许列表中
    if filename in ALLOWED_FILES:
        return True
    
    # 检查文件是否在允许的文件夹中
    for folder in ALLOWED_FOLDERS:
        if filename.startswith(folder + '/'):
            return True
    
    return False

def prevent_path_traversal(filepath):
    """
    防止路径遍历攻击
    """
    if not os.path.abspath(filepath).startswith(os.path.abspath(os.getcwd())):
        raise PermissionError("Access denied due to path traversal attempt")

@app.route('/')
@app.route('/<path:filename>')
def serve_static(filename='index.html'):
    """
    提供静态文件服务
    """
    logger.info(f"收到GET请求: /{filename}")
    
    # 检查文件是否被允许访问
    if not is_path_allowed(filename):
        logger.warning(f"尝试访问被拒绝的文件: {filename}")
        return jsonify({'error': "Forbidden: You don't have permission to access this file"}), 403
    
    # 构建文件路径
    filepath = os.path.join(os.getcwd(), filename)
    
    # 检查文件是否存在
    if not os.path.exists(filepath):
        logger.warning(f"文件不存在: {filepath}")
        return jsonify({'error': "File not found"}), 404
    
    # 防止路径遍历攻击
    try:
        prevent_path_traversal(filepath)
    except PermissionError as e:
        logger.warning(f"路径遍历攻击尝试: {filepath}")
        return jsonify({'error': str(e)}), 403
    
    # 返回文件
    try:
        return send_file(filepath)
    except Exception as e:
        logger.error(f"发送文件失败: {e}")
        return jsonify({'error': "Failed to serve file"}), 500

@app.route('/api/clear-log', methods=['GET'])
def handle_clear_log():
    """
    处理清空日志的请求 - 直接清空logs文件夹中的所有文件
    """
    try:
        logs_dir = os.path.join(os.getcwd(), 'logs')
        
        # 检查logs目录是否存在
        if not os.path.exists(logs_dir):
            return jsonify({'error': "Logs directory not found"}), 404
            
        if not os.path.isdir(logs_dir):
            return jsonify({'error': "Logs path is not a directory"}), 500
        
        cleared_files = []
        failed_files = []
        
        # 遍历logs目录中的所有文件
        for filename in os.listdir(logs_dir):
            filepath = os.path.join(logs_dir, filename)
            try:
                # 只处理文件，跳过子目录
                if os.path.isfile(filepath):
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write('')
                    cleared_files.append(filename)
            except Exception as e:
                failed_files.append(f"{filename} ({str(e)})")
        
        response = {
            'success': True,
            'message': f'已清空 {len(cleared_files)} 个日志文件',
            'cleared_files': cleared_files,
            'failed_files': failed_files
        }
        logger.info(f"已清空日志目录中的所有文件: {cleared_files}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"清空日志文件失败: {e}")
        return jsonify({'error': f"Failed to clear log files: {str(e)}"}), 500

@app.route('/api/list-logs', methods=['GET'])
def handle_list_logs():
    """
    处理获取日志文件列表的请求
    """
    try:
        logs_dir = os.path.join(os.getcwd(), 'logs')
        
        # 检查logs目录是否存在
        if not os.path.exists(logs_dir):
            return jsonify({'error': "Logs directory not found"}), 404
            
        if not os.path.isdir(logs_dir):
            return jsonify({'error': "Logs path is not a directory"}), 500
        
        log_files = []
        
        # 遍历logs目录中的所有文件
        for filename in os.listdir(logs_dir):
            filepath = os.path.join(logs_dir, filename)
            # 只处理文件，跳过子目录
            if os.path.isfile(filepath):
                # 获取文件信息
                stat = os.stat(filepath)
                log_files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
        
        response = {
            'success': True,
            'logs': log_files
        }
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"获取日志文件列表失败: {e}")
        return jsonify({'error': f"Failed to list log files: {str(e)}"}), 500

@app.route('/api/get-log', methods=['GET'])
def handle_get_log():
    """
    处理获取日志内容的请求
    """
    try:
        # 获取要获取内容的日志文件名
        log_file = request.args.get('file')
        
        if not log_file:
            return jsonify({'error': "Missing file parameter"}), 400
        
        # 构建文件路径
        filepath = os.path.join(os.getcwd(), 'logs', log_file)
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            return jsonify({'error': "Log file not found"}), 404
            
        # 检查是否是文件
        if not os.path.isfile(filepath):
            return jsonify({'error': "Path is not a file"}), 400
        
        # 读取文件内容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        response = {
            'success': True,
            'file': log_file,
            'content': content
        }
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"获取日志文件失败: {e}")
        return jsonify({'error': f"Failed to get log file: {str(e)}"}), 500

@app.route('/api/save-book', methods=['POST'])
def handle_save_book():
    """
    处理保存书卷的请求
    """
    try:
        book_data = request.get_json()
        
        # 创建readingroom目录（如果不存在）
        readingroom_dir = os.path.join(os.getcwd(), 'readingroom')
        if not os.path.exists(readingroom_dir):
            os.makedirs(readingroom_dir)
        
        # 生成唯一的书卷ID
        book_id = str(uuid.uuid4())
        book_dir = os.path.join(readingroom_dir, book_id)
        os.makedirs(book_dir)
        
        # 保存书卷信息
        book_info = {
            'id': book_id,
            'name': book_data['name'],
            'created_at': datetime.now().isoformat(),
            'file_count': len(book_data['files'])
        }
        
        # 保存文件
        for i, file_data in enumerate(book_data['files']):
            file_path = os.path.join(book_dir, file_data['name'])
            
            if file_data['type'].startswith('image/'):
                # 保存图片文件
                import base64
                header, encoded = file_data['content'].split(',', 1)
                with open(file_path, 'wb') as f:
                    f.write(base64.b64decode(encoded))
            else:
                # 保存文本文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_data['content'])
        
        # 保存书卷元数据
        metadata_path = os.path.join(book_dir, 'metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(book_info, f, ensure_ascii=False, indent=2)
        
        # 更新书卷列表
        books_list_path = os.path.join(readingroom_dir, 'books.json')
        books_list = []
        if os.path.exists(books_list_path):
            with open(books_list_path, 'r', encoding='utf-8') as f:
                books_list = json.load(f)
        
        books_list.append(book_info)
        with open(books_list_path, 'w', encoding='utf-8') as f:
            json.dump(books_list, f, ensure_ascii=False, indent=2)
        
        response = {
            'success': True,
            'message': '书卷保存成功',
            'book_id': book_id
        }
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"保存书卷失败: {e}")
        return jsonify({'error': f"保存书卷失败: {str(e)}"}), 500

@app.route('/api/list-books', methods=['GET'])
def handle_list_books():
    """
    处理获取书卷列表的请求
    """
    try:
        readingroom_dir = os.path.join(os.getcwd(), 'readingroom')
        
        # 检查readingroom目录是否存在
        if not os.path.exists(readingroom_dir):
            os.makedirs(readingroom_dir)
        
        books_list_path = os.path.join(readingroom_dir, 'books.json')
        books_list = []
        if os.path.exists(books_list_path):
            with open(books_list_path, 'r', encoding='utf-8') as f:
                books_list = json.load(f)
        
        response = {
            'success': True,
            'books': books_list
        }
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"获取书卷列表失败: {e}")
        return jsonify({'error': f"获取书卷列表失败: {str(e)}"}), 500

@app.route('/api/load-book/<book_id>', methods=['GET'])
def handle_load_book(book_id):
    """
    处理加载书卷的请求
    """
    try:
        readingroom_dir = os.path.join(os.getcwd(), 'readingroom')
        book_dir = os.path.join(readingroom_dir, book_id)
        
        # 检查书卷目录是否存在
        if not os.path.exists(book_dir):
            return jsonify({'error': "书卷不存在"}), 404
        
        # 读取书卷元数据
        metadata_path = os.path.join(book_dir, 'metadata.json')
        if not os.path.exists(metadata_path):
            return jsonify({'error': "书卷元数据丢失"}), 500
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            book_info = json.load(f)
        
        # 读取文件列表
        files = []
        for filename in os.listdir(book_dir):
            if filename == 'metadata.json':
                continue
                
            file_path = os.path.join(book_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    'id': f"{book_id}_{filename}",
                    'filename': filename,
                    'file_type': 'image/' + filename.split('.')[-1] if filename.split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'gif'] else 'text/plain',
                    'file_size': stat.st_size,
                    'sort_order': 0
                })
        
        response = {
            'success': True,
            'book': book_info,
            'files': files
        }
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"加载书卷失败: {e}")
        return jsonify({'error': f"加载书卷失败: {str(e)}"}), 500

@app.route('/api/delete-book', methods=['POST'])
def handle_delete_book():
    """
    处理删除书卷的请求
    """
    try:
        request_data = request.get_json()
        
        book_id = request_data['id']
        readingroom_dir = os.path.join(os.getcwd(), 'readingroom')
        book_dir = os.path.join(readingroom_dir, book_id)
        
        # 检查书卷目录是否存在
        if not os.path.exists(book_dir):
            return jsonify({'error': "书卷不存在"}), 404
        
        # 删除书卷目录
        import shutil
        shutil.rmtree(book_dir)
        
        # 更新书卷列表
        books_list_path = os.path.join(readingroom_dir, 'books.json')
        books_list = []
        if os.path.exists(books_list_path):
            with open(books_list_path, 'r', encoding='utf-8') as f:
                books_list = json.load(f)
        
        # 移除已删除的书卷
        books_list = [book for book in books_list if book['id'] != book_id]
        with open(books_list_path, 'w', encoding='utf-8') as f:
            json.dump(books_list, f, ensure_ascii=False, indent=2)
        
        response = {
            'success': True,
            'message': '书卷删除成功'
        }
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"删除书卷失败: {e}")
        return jsonify({'error': f"删除书卷失败: {str(e)}"}), 500

if __name__ == '__main__':
    logger.info(f"安全服务器运行在端口 {PORT}")
    logger.info("允许访问的文件:")
    for file in ALLOWED_FILES:
        logger.info(f"  - {file}")
    logger.info("允许访问的文件夹:")
    for folder in ALLOWED_FOLDERS:
        logger.info(f"  - {folder} (文件夹内所有文件)")
    logger.info("按 Ctrl+C 停止服务器")
    
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False,use_reloader=False)
    except KeyboardInterrupt:
        logger.info("服务器已停止")
        print("\n服务器已停止")