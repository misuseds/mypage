// config.js - 全局配置文件
const APP_CONFIG = {
    // 生产环境配置（内网穿透地址）
    BASE_URL: 'http://171.80.1.215:21815',
    
    // 本地测试时可以改为:
    // BASE_URL: 'http://localhost:801',
    
    // 其他可能的配置项
    API_TIMEOUT: 30000,
    DEBUG_MODE: false
};

// 为了兼容性，同时导出为全局变量
window.APP_CONFIG = APP_CONFIG;