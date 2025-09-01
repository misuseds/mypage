<?php
// keyinfoapi/get_config.php
include 'config.php';

try {
    $stmt = $pdo->query("SELECT config_key, config_value FROM user_configs");
    $configs = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    $result = [];
    foreach ($configs as $config) {
        $result[$config['config_key']] = $config['config_value'];
    }
    
    echo json_encode(['success' => true, 'data' => $result]);
} catch (Exception $e) {
    echo json_encode(['success' => false, 'message' => '获取配置失败: ' . $e->getMessage()]);
}
?>