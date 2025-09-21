import os
from dotenv import load_dotenv
import json
import http.client
from urllib.parse import urlparse
from flask import Flask, request, jsonify

# 加载 .env 文件中的环境变量
load_dotenv()

app = Flask(__name__)

class LLMService:
    def __init__(self):
        # 从环境变量中获取 DeepSeek 参数
        self.api_url = os.getenv('DEEPSEEK_API_URL')
        self.model_name = os.getenv('DEEPSEEK_MODEL_NAME')
        self.api_key = os.getenv('DEEPSEEK_API_KEY')

    def create(self, messages, tools=None):
        # 解析 URL（去掉协议部分）
        parsed = urlparse(f"{self.api_url}/chat/completions")
        host, path = parsed.hostname, parsed.path
        
        # 创建 HTTP 连接
        conn = http.client.HTTPSConnection(host)

        # 构造请求体
        request_body = {
            "model": self.model_name,
            "messages": messages,
            "tools": tools,
            "temperature": 0.9  # 添加温度参数
        }

        # 发送 POST 请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        conn.request(
            "POST",
            path,
            body=json.dumps(request_body),
            headers=headers
        )

        # 获取响应
        response = conn.getresponse()
        if response.status != 200:
            raise Exception(f"LLM服务器错误: {response.status} - {response.read().decode('utf-8')}")

        # 读取响应内容
        response_data = response.read().decode('utf-8')
        data = json.loads(response_data)

        # 将响应保存到文件
        with open('formatted_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # 关闭连接
        conn.close()

        return data

# 创建 LLMService 实例
llm_service = LLMService()

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    try:
        # 从请求中获取 messages
        data = request.get_json()
        messages = data.get('messages', [])
        tools = data.get('tools', None)
        
        # 调用 LLMService 的 create 方法
        result = llm_service.create(messages, tools)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 启动 Flask 服务，监听 5003 端口
    app.run(host='0.0.0.0', port=5003, debug=True)