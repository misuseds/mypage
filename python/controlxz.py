# controlxz.py
import logging
from datetime import datetime
from pynput.keyboard import Key, Controller
import threading
from flask import Flask, request, jsonify

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量用于存储按键状态
key_state = {
    'X': False,
    'Z': False,
    'last_updated': None
}

# 创建键盘控制器
keyboard = Controller()

# Flask应用
app = Flask(__name__)

from flask_cors import CORS
CORS(app)
def press_key(key):
    """模拟按键按下"""
    logger.info(f"模拟按键按下: {key}")
    
    try:
        # 使用独立线程避免阻塞
        def _press():
            if key == 'X':
                keyboard.press('x')
                keyboard.release('x')
            elif key == 'Z':
                keyboard.press('z')
                keyboard.release('z')
        
        thread = threading.Thread(target=_press)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        logger.error(f"按键模拟失败: {e}")

def control_keys(action, key):
    """控制X和Z按键状态"""
    try:
        if action not in ['press', 'release'] or key not in ['X', 'Z']:
            return {'error': '无效的操作或按键'}, 400
        
        # 实际按键控制（只在按下时触发）
        if action == 'press':
            press_key(key)
        
        # 更新按键状态
        global key_state
        key_state[key] = (action == 'press')
        key_state['last_updated'] = datetime.now().isoformat()
        
        logger.info(f"按键 {key} 状态更新为: {action}")
        
        return {
            'status': 'success',
            'message': f'按键 {key} 已{action}',
            'key_state': key_state
        }, 200
        
    except Exception as e:
        logger.error(f"控制按键时出错: {e}")
        return {'error': str(e)}, 500

def get_key_state():
    """获取当前按键状态"""
    logger.info("获取按键状态")
    return key_state

def control_health_check():
    """按键控制健康检查"""
    return {
        'status': 'healthy', 
        'message': '按键控制模块正在运行',
        'timestamp': datetime.now().isoformat()
    }

# HTTP 接口
@app.route('/control', methods=['POST'])
def handle_control():
    """处理按键控制请求"""
    data = request.get_json()
    action = data.get('action')
    key = data.get('key')
    
    # 调用已有的控制函数
    result, status_code = control_keys(action, key)
    return jsonify(result), status_code

@app.route('/state', methods=['GET'])
def handle_get_state():
    """获取按键状态"""
    state = get_key_state()
    return jsonify(state)

@app.route('/health', methods=['GET'])
def handle_health_check():
    """健康检查"""
    health_info = control_health_check()
    return jsonify(health_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)