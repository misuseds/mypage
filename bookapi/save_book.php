<?php
// bookapi/save_book.php
include 'config.php';

// 确保始终返回JSON
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // 检查输入数据
    $inputData = file_get_contents('php://input');
    if (empty($inputData)) {
        echo json_encode(['success' => false, 'message' => '没有接收到数据']);
        exit;
    }
    
    $input = json_decode($inputData, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        echo json_encode(['success' => false, 'message' => 'JSON解析错误: ' . json_last_error_msg()]);
        exit;
    }
    
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
            $result = $stmt->execute([$input['name'], count($input['files'])]);
            if (!$result) {
                throw new Exception("插入书籍记录失败");
            }
            $bookId = $pdo->lastInsertId();
        }
        
        // 插入文件
        foreach ($input['files'] as $index => $file) {
            $content = null;
            $contentText = null;
            
            if (isset($file['type']) && strpos($file['type'], 'image/') === 0) {
                // 处理图片文件 (base64数据)
                $base64Data = $file['content'] ?? '';
                
                // 移除可能的数据URI前缀
                if (strpos($base64Data, 'data:') === 0) {
                    $base64Data = substr($base64Data, strpos($base64Data, ',') + 1);
                }
                
                // 解码base64数据
                $content = base64_decode($base64Data);
            } else {
                // 处理文本文件
                $contentText = isset($file['content']) ? $file['content'] : '';
            }
            
            $stmt = $pdo->prepare("INSERT INTO book_files (book_id, filename, file_type, file_size, content, content_text, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?)");
            $result = $stmt->execute([
                $bookId,
                isset($file['name']) ? $file['name'] : 'unknown',
                isset($file['type']) ? $file['type'] : 'text/plain',
                isset($file['size']) ? $file['size'] : 0,
                $content, // 二进制数据
                $contentText, // 文本数据
                $index
            ]);
            
            if (!$result) {
                throw new Exception("插入文件记录失败: " . $file['name']);
            }
        }
        
        $pdo->commit();
        echo json_encode(['success' => true, 'message' => '书籍保存成功', 'book_id' => $bookId]);
    } catch (Exception $e) {
        $pdo->rollBack();
        error_log("Save book error: " . $e->getMessage()); // 记录错误日志
        echo json_encode(['success' => false, 'message' => '保存失败: ' . $e->getMessage()]);
    }
} else {
    echo json_encode(['success' => false, 'message' => '无效的请求方法']);
}
?>