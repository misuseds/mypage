<?php
// bookapi/save_book.php
include 'config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['name']) || !isset($input['files'])) {
        echo json_encode(['success' => false, 'message' => '缺少必要参数']);
        exit;
    }
    
    try {
        $pdo->beginTransaction();
        
        // 检查书籍是否已存在
        $stmt = $pdo->prepare("SELECT id FROM books WHERE name = ?");
        $stmt->execute([$input['name']]);
        $existingBook = $stmt->fetch();
        
        if ($existingBook) {
            // 更新现有书籍
            $bookId = $existingBook['id'];
            $stmt = $pdo->prepare("UPDATE books SET file_count = ?, updated_at = NOW() WHERE id = ?");
            $stmt->execute([count($input['files']), $bookId]);
            
            // 删除旧文件
            $stmt = $pdo->prepare("DELETE FROM book_files WHERE book_id = ?");
            $stmt->execute([$bookId]);
        } else {
            // 创建新书籍
            $stmt = $pdo->prepare("INSERT INTO books (name, file_count) VALUES (?, ?)");
            $stmt->execute([$input['name'], count($input['files'])]);
            $bookId = $pdo->lastInsertId();
        }
        
        // 插入文件
        foreach ($input['files'] as $index => $file) {
            $content = null;
            $contentText = null;
            
            if (strpos($file['type'], 'image/') === 0) {
                // 处理图片文件 (base64数据)
                if (preg_match('/^data:image\/(.*?);base64,(.*)$/', $file['content'], $matches)) {
                    $content = base64_decode($matches[2]);
                } else {
                    $content = base64_decode($file['content']);
                }
            } else {
                // 处理文本文件
                $contentText = $file['content'];
            }
            
            $stmt = $pdo->prepare("INSERT INTO book_files (book_id, filename, file_type, file_size, content, content_text, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?)");
            $stmt->execute([
                $bookId,
                $file['name'],
                $file['type'],
                $file['size'],
                $content,
                $contentText,
                $index
            ]);
        }
        
        $pdo->commit();
        echo json_encode(['success' => true, 'message' => '书籍保存成功', 'book_id' => $bookId]);
    } catch (Exception $e) {
        $pdo->rollBack();
        echo json_encode(['success' => false, 'message' => '保存失败: ' . $e->getMessage()]);
    }
} else {
    echo json_encode(['success' => false, 'message' => '无效的请求方法']);
}
?>