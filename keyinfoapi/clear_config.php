<?php
// keyinfoapi/clear_config.php
include 'config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try {
        // 清空配置值但保留记录
        $stmt = $pdo->prepare("UPDATE user_configs SET config_value = ''");
        $stmt->execute();
        
        echo json_encode(['success' => true, 'message' => '配置已清空']);
    } catch (Exception $e) {
        echo json_encode(['success' => false, 'message' => '清空配置失败: ' . $e->getMessage()]);
    }
} else {
    echo json_encode(['success' => false, 'message' => '无效的请求方法']);
}
?>