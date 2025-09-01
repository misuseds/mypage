<?php
// keyinfoapi/save_config.php
include 'config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['deepseekKey']) || !isset($input['personalInfo'])) {
        echo json_encode(['success' => false, 'message' => '缺少必要参数']);
        exit;
    }
    
    try {
        // 更新DeepSeek API Key
        $stmt = $pdo->prepare("INSERT INTO user_configs (config_key, config_value) VALUES (?, ?) ON DUPLICATE KEY UPDATE config_value = ?");
        $stmt->execute(['deepseek_api_key', $input['deepseekKey'], $input['deepseekKey']]);
        
        // 更新个人信息
        $stmt = $pdo->prepare("INSERT INTO user_configs (config_key, config_value) VALUES (?, ?) ON DUPLICATE KEY UPDATE config_value = ?");
        $stmt->execute(['personal_info', $input['personalInfo'], $input['personalInfo']]);
        
        echo json_encode(['success' => true, 'message' => '配置保存成功']);
    } catch (Exception $e) {
        echo json_encode(['success' => false, 'message' => '保存配置失败: ' . $e->getMessage()]);
    }
} else {
    echo json_encode(['success' => false, 'message' => '无效的请求方法']);
}
?>