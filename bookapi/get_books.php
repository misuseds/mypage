<?php
// bookapi/get_books.php
include 'config.php';

header('Content-Type: application/json');

try {
    $stmt = $pdo->query("SELECT id, name, file_count, created_at, updated_at FROM books ORDER BY updated_at DESC");
    $books = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    echo json_encode(['success' => true, 'books' => $books]);
} catch (Exception $e) {
    error_log("Get books error: " . $e->getMessage()); // 记录错误日志
    echo json_encode(['success' => false, 'message' => '获取书籍列表失败: ' . $e->getMessage()]);
}
?>