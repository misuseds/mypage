<?php
// bookapi/load_book.php
include 'config.php';

header('Content-Type: application/json'); // 添加这行

if (!isset($_GET['id'])) {
    echo json_encode(['success' => false, 'message' => '缺少书籍ID']);
    exit;
}

try {
    $bookId = intval($_GET['id']);
    
    // 获取书籍信息
    $stmt = $pdo->prepare("SELECT id, name, file_count, created_at, updated_at FROM books WHERE id = ?");
    $stmt->execute([$bookId]);
    $book = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if (!$book) {
        echo json_encode(['success' => false, 'message' => '书籍不存在']);
        exit;
    }
    
    // 获取文件列表
    $stmt = $pdo->prepare("SELECT id, filename, file_type, file_size, sort_order FROM book_files WHERE book_id = ? ORDER BY sort_order");
    $stmt->execute([$bookId]);
    $files = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    echo json_encode(['success' => true, 'book' => $book, 'files' => $files]);
} catch (Exception $e) {
    echo json_encode(['success' => false, 'message' => '加载书籍失败: ' . $e->getMessage()]);
}
?>