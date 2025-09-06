<?php
header('Content-Type: application/json');

// 包含配置文件
include 'config.php';

try {
    // 从数据库获取DeepSeek API密钥
    $stmt = $pdo->prepare("SELECT config_value FROM user_configs WHERE config_key = ?");
    $stmt->execute(['deepseek_api_key']);
    $result = $stmt->fetch(PDO::FETCH_ASSOC);
    
    $apiKey = $result['config_value'] ?? '';
    
    // 检查API密钥是否存在
    if (!$apiKey || $apiKey === '') {
        http_response_code(401);
        echo json_encode(['error' => 'API密钥未配置或为空']);
        exit;
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => '获取API密钥失败: ' . $e->getMessage()]);
    exit;
}

$postData = json_decode(file_get_contents('php://input'), true);

// 检查是否接收到数据
if (!$postData) {
    http_response_code(400);
    echo json_encode(['error' => '无效的请求数据']);
    exit;
}

$ch = curl_init('https://api.deepseek.com/v1/chat/completions');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($postData));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Authorization: Bearer ' . $apiKey
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

// 检查cURL是否出错
if ($error) {
    http_response_code(500);
    echo json_encode(['error' => '请求失败: ' . $error]);
    exit;
}

// 检查HTTP状态码
if ($httpCode !== 200) {
    http_response_code($httpCode);
    // 尝试解析响应，如果无法解析则返回原始响应
    $decodedResponse = json_decode($response, true);
    if ($decodedResponse === null) {
        echo json_encode(['error' => 'API请求失败，状态码: ' . $httpCode, 'details' => $response]);
    } else {
        echo json_encode(['error' => 'API请求失败，状态码: ' . $httpCode, 'details' => $decodedResponse]);
    }
    exit;
}

// 直接输出API响应
echo $response;
?>