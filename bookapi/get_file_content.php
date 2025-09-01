<?php
// bookapi/get_file_content.php
include 'config.php';

// 这个API不需要设置Content-Type: application/json，因为它返回的是文件内容
if (!isset($_GET['id'])) {
    header('HTTP/1.1 400 Bad Request');
    die('缺少文件ID');
}

try {
    $fileId = intval($_GET['id']);
    
    $stmt = $pdo->prepare("SELECT filename, file_type, content, content_text FROM book_files WHERE id = ?");
    $stmt->execute([$fileId]);
    $file = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if (!$file) {
        header('HTTP/1.1 404 Not Found');
        die('文件不存在');
    }
    
    // 设置适当的响应头
    header("Content-Type: " . $file['file_type']);
    
    if ($file['content'] !== null) {
        // 二进制内容（图片）
        header("Content-Length: " . strlen($file['content']));
        echo $file['content'];
    } else {
        // 文本内容
        echo $file['content_text'];
    }
    exit;
} catch (Exception $e) {
    header('HTTP/1.1 500 Internal Server Error');
    die('获取文件失败: ' . $e->getMessage());
}
?>