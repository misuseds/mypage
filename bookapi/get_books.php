<?php
// bookapi/get_books.php
include 'config.php';

try {
    $stmt = $pdo->query("SELECT id, name, file_count, created_at, updated_at FROM books ORDER BY updated_at DESC");
    $books = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    echo json_encode(['success' => true, 'books' => $books]);
} catch (Exception $e) {
    echo json_encode(['success' => false, 'message' => '获取书籍列表失败: ' . $e->getMessage()]);
}
?>