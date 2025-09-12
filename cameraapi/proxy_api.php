<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit(0);
}

// 获取请求数据
$data = json_decode(file_get_contents('php://input'), true);

if (!$data || !isset($data['url'])) {
    echo json_encode(['success' => false, 'error' => 'Missing URL parameter']);
    exit(1);
}

$url = $data['url'];
$method = $data['method'] ?? 'GET';

// 初始化cURL
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

// 如果是POST请求且有数据
if ($method === 'POST' && isset($data['body'])) {
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data['body']);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
}

// 执行请求
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

// 返回结果
if ($error) {
    echo json_encode(['success' => false, 'error' => 'cURL Error: ' . $error]);
} else {
    echo json_encode([
        'success' => $httpCode >= 200 && $httpCode < 300,
        'data' => $response,
        'httpCode' => $httpCode
    ]);
}
?>