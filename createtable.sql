-- 书籍表
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    file_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 文件表
CREATE TABLE book_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(100),
    file_size INT,
    content LONGBLOB,
    content_text LONGTEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- 用户配置表
CREATE TABLE user_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 初始化配置项
INSERT INTO user_configs (config_key, config_value) VALUES 
('deepseek_api_key', ''),
('personal_info', '');