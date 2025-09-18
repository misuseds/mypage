<?php
// proxy.php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit(0);
}

// 修改Flask服务地址 - 使用本地地址和正确的端口
// 根据您的controlxz.py文件，Flask服务运行在5001端口而不是5000端口
define('FLASK_SERVICE_URL', 'http://ns3.llmfindworksnjsgcs.fwh.is');

// 记录请求日志
error_log("HTTP Proxy - 收到请求: " . $_SERVER['REQUEST_METHOD'] . " " . $_SERVER['REQUEST_URI']);

// 获取请求数据
$input_data = file_get_contents('php://input');
$data = json_decode($input_data, true);
error_log("HTTP Proxy - 请求数据: " . print_r($data, true));

if (!$data || !isset($data['action'])) {
    error_log("HTTP Proxy - 错误: 缺少action参数");
    echo json_encode(['success' => false, 'error' => 'Missing action parameter']);
    exit(1);
}

$action = $data['action'];
error_log("HTTP Proxy - 执行操作: " . $action);

switch ($action) {
    case 'get_state':
        error_log("HTTP Proxy - 从Flask服务获取当前状态");
        
        // 直接获取按键状态
        $url = FLASK_SERVICE_URL . '/state'; // 修改为/state端点
        error_log("HTTP Proxy - 请求URL: " . $url);
        $response = fetchFromFlask($url, 'GET');
        
        if ($response === false) {
            error_log("HTTP Proxy - 连接Flask按键控制服务失败，URL: " . $url);
            echo json_encode(['success' => false, 'error' => '无法连接到按键控制服务，请检查Flask服务是否运行']);
            exit(1);
        }
        
        $state = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            error_log("HTTP Proxy - JSON解析错误: " . json_last_error_msg() . " 响应内容: " . $response);
            echo json_encode(['success' => false, 'error' => '服务响应格式错误']);
            exit(1);
        }
        
        error_log("HTTP Proxy - 当前状态: " . print_r($state, true));
        echo json_encode(['success' => true, 'data' => $state]);
        break;
        
    case 'control':
        error_log("HTTP Proxy - 向Flask服务发送控制命令");
        
        if (!isset($data['key']) || !isset($data['key_action'])) {
            error_log("HTTP Proxy - 错误: 缺少key或key_action参数");
            echo json_encode(['success' => false, 'error' => 'Missing key or key_action']);
            exit(1);
        }
        
        $key = $data['key'];
        $key_action = $data['key_action'];
        
        error_log("HTTP Proxy - 按键: " . $key . ", 操作: " . $key_action);
        
        if (!in_array($key, ['X', 'Z']) || !in_array($key_action, ['press', 'release'])) {
            error_log("HTTP Proxy - 错误: 无效的按键或操作");
            echo json_encode(['success' => false, 'error' => 'Invalid key or action']);
            exit(1);
        }
        
        // 构造发送到Flask服务的数据
        $post_data = json_encode([
            'action' => $key_action,
            'key' => $key
        ]);
        
        $url = FLASK_SERVICE_URL . '/control';
        error_log("HTTP Proxy - 控制命令 URL: " . $url);
        $response = fetchFromFlask($url, 'POST', $post_data);
        
        if ($response === false) {
            error_log("HTTP Proxy - 连接Flask按键控制服务失败，URL: " . $url);
            echo json_encode(['success' => false, 'error' => '无法连接到按键控制服务']);
            exit(1);
        }
        
        $result = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            error_log("HTTP Proxy - JSON解析错误: " . json_last_error_msg() . " 响应内容: " . $response);
            echo json_encode(['success' => false, 'error' => '服务响应格式错误']);
            exit(1);
        }
        
        error_log("HTTP Proxy - Flask服务响应: " . print_r($result, true));
        
        if (isset($result['error'])) {
            echo json_encode(['success' => false, 'error' => $result['error']]);
            exit(1);
        }
        
        echo json_encode([
            'success' => true, 
            'message' => $result['message'] ?? "按键 {$key} 已{$key_action}",
            'data' => $result['key_state'] ?? $result
        ]);
        break;
        
    default:
        error_log("HTTP Proxy - 错误: 无效的操作 " . $action);
        echo json_encode(['success' => false, 'error' => 'Invalid action']);
        break;
}

/**
 * 向Flask服务发送HTTP请求
 * 
 * @param string $url 请求URL
 * @param string $method HTTP方法 (GET/POST)
 * @param string $data POST数据
 * @return string|false 响应内容或false表示失败
 */
function fetchFromFlask($url, $method = 'GET', $data = null) {
    $options = [
        'http' => [
            'method' => $method,
            'header' => [
                'Content-Type: application/json',
                'Accept: application/json'
            ],
            'timeout' => 30,  // 增加超时时间
            'ignore_errors' => false
        ]
    ];
    
    if ($method === 'POST' && $data) {
        $options['http']['content'] = $data;
    }
    
    error_log("HTTP Proxy - 发送请求到: " . $url . " 方法: " . $method);
    
    $context = stream_context_create($options);
    $response = @file_get_contents($url, false, $context);
    
    // 检查HTTP响应码
    $http_response_header_local = $http_response_header ?? [];
    if (!empty($http_response_header_local)) {
        $status_line = $http_response_header_local[0];
        error_log("HTTP Proxy - 响应状态: " . $status_line);
        preg_match('{HTTP\/\S*\s(\d{3})}', $status_line, $match);
        $status_code = $match[1] ?? null;
        
        if ($status_code) {
            error_log("HTTP Proxy - Flask服务返回状态码: " . $status_code . " for URL: " . $url);
        }
        
        // 如果返回404或其他错误状态码，返回false
        if ($status_code && $status_code >= 400) {
            error_log("HTTP Proxy - Flask服务返回错误状态码: " . $status_code);
            return false;
        }
    }
    
    // 检查是否有错误
    if ($response === false) {
        $error = error_get_last();
        error_log("HTTP Proxy - 请求Flask服务失败: " . ($error['message'] ?? '未知错误') . " for URL: " . $url);
        return false;
    }
    
    error_log("HTTP Proxy - 收到响应长度: " . strlen($response) . " 字符");
    return $response;
}

error_log("HTTP Proxy - 请求处理完成");
?>