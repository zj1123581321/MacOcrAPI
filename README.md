# OCR Mac API

基于 ocrmac 的高并发 OCR API 服务，支持 macOS 系统自动启动和 base64 图像处理。

## 功能特性

- 🚀 **高并发支持** - 基于 FastAPI 和异步处理
- 🖼️ **Base64 图像输入** - 支持直接传入 base64 编码的图像
- 🔒 **安全认证** - Bearer Token 认证机制
- 📊 **详细日志** - 完整的日志记录和监控
- 🍎 **macOS 原生** - 使用 Apple Vision 框架
- 🔧 **易于配置** - 支持环境变量和配置文件
- 🚀 **自动启动** - 支持 macOS 系统自动启动

## 系统要求

- **操作系统**: macOS 10.15+ (Catalina 或更高版本)
- **Python**: 3.8+
- **内存**: 建议 4GB 以上
- **存储**: 500MB 可用空间

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd 250705_OcrMacApi
```

### 2. 自动安装

```bash
chmod +x install.sh
./install.sh
```

### 3. 启动服务

```bash
# 前台启动（用于调试）
python3 main.py

# 后台启动
./startup.sh
```

### 4. 设置自动启动（可选）

```bash
chmod +x setup_autostart.sh
./setup_autostart.sh
```

## 手动安装

### 1. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 2. 配置环境

```bash
cp config.example.env .env
# 编辑 .env 文件以配置您的设置
```

### 3. 创建日志目录

```bash
mkdir -p logs
```

## 配置说明

### 环境变量

创建 `.env` 文件或设置环境变量：

```env
# 服务器配置
HOST=0.0.0.0
PORT=8003
WORKERS=4

# 安全配置
AUTH_TOKEN=your-secure-token-here
ALLOWED_ORIGINS=*

# OCR 配置
RECOGNITION_LEVEL=accurate  # accurate 或 fast
CONFIDENCE_THRESHOLD=0.0
FRAMEWORK=vision           # vision 或 livetext
LANGUAGE_PREFERENCE=       # 如: en-US,zh-Hans

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 性能配置
MAX_IMAGE_SIZE=10485760    # 10MB
REQUEST_TIMEOUT=30
```

### 配置参数说明

- `RECOGNITION_LEVEL`: 识别精度，`accurate` 精度高但速度慢，`fast` 速度快但精度相对较低
- `FRAMEWORK`: OCR 框架，`vision` 使用 Vision 框架，`livetext` 使用 LiveText 框架（需要 macOS Sonoma+）
- `LANGUAGE_PREFERENCE`: 语言偏好，多个语言用逗号分隔
- `AUTH_TOKEN`: API 认证令牌，建议使用强密码

## API 使用

### 基本用法

按照您提供的示例格式：

```bash
curl --location 'http://localhost:8003/predict' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer test' \
--data '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
}'
```

### 返回格式

```json
[
    {
        "dt_boxes": [[46,54],[127,54],[127,79],[46,79]],
        "rec_txt": "175.0M",
        "score": 0.9988542000452677
    },
    {
        "dt_boxes": [[46,126],[127,126],[127,152],[46,152]],
        "rec_txt": "150.0M",
        "score": 0.9995218416055044
    }
]
```

### 详细 API 接口

#### 1. OCR 识别

- **URL**: `POST /predict`
- **认证**: Bearer Token
- **请求体**:
  ```json
  {
      "image_base64": "base64编码的图像",
      "recognition_level": "accurate",  // 可选
      "language_preference": ["en-US"], // 可选
      "confidence_threshold": 0.0,      // 可选
      "framework": "vision"             // 可选
  }
  ```

#### 2. 详细识别结果

- **URL**: `POST /predict-detailed`
- **认证**: Bearer Token
- **返回**: 包含处理时间、图像尺寸等详细信息

#### 3. 健康检查

- **URL**: `GET /health`
- **认证**: 无需认证
- **返回**: 服务状态信息

#### 4. 统计信息

- **URL**: `GET /stats`
- **认证**: Bearer Token
- **返回**: 服务统计数据

#### 5. 支持的语言

- **URL**: `GET /supported-languages`
- **认证**: Bearer Token
- **返回**: 支持的语言列表

## 服务管理

### 启动服务

```bash
# 直接启动
python3 main.py

# 后台启动
./startup.sh

# 使用 launchctl（需要先设置自动启动）
launchctl start com.ocrmac.api
```

### 停止服务

```bash
# 停止 launchctl 服务
launchctl stop com.ocrmac.api

# 或者直接杀死进程
kill $(cat ocrmac_api.pid)
```

### 查看日志

```bash
# 实时查看日志
tail -f logs/ocrmac_api.log

# 查看错误日志
tail -f logs/ocrmac_api_error.log
```

### 重启服务

```bash
launchctl stop com.ocrmac.api && launchctl start com.ocrmac.api
```

## 性能优化

### 1. 调整工作进程数

```bash
# 在 .env 文件中设置
WORKERS=8  # 根据 CPU 核心数调整
```

### 2. 选择合适的识别级别

- `accurate`: 高精度，适合重要文档
- `fast`: 快速识别，适合大量处理

### 3. 限制图像大小

```bash
# 在 .env 文件中设置
MAX_IMAGE_SIZE=5242880  # 5MB
```

## 故障排除

### 1. 服务无法启动

```bash
# 检查 Python 版本
python3 --version

# 检查依赖
pip3 list | grep fastapi

# 查看详细错误
python3 main.py --debug
```

### 2. OCR 识别失败

```bash
# 检查 Vision 框架
python3 -c "import Vision; print('Vision 框架可用')"

# 检查图像格式
python3 -c "from PIL import Image; print('PIL 可用')"
```

### 3. 自动启动失败

```bash
# 检查 LaunchAgent 状态
launchctl list | grep com.ocrmac.api

# 查看 LaunchAgent 日志
log show --predicate 'subsystem == "com.apple.launchd"' --info
```

## 开发

### 项目结构

```
250705_OcrMacApi/
├── ocrmac-main/           # ocrmac 源码
├── config.py              # 配置管理
├── models.py              # 数据模型
├── ocr_service.py         # OCR 服务封装
├── api.py                 # FastAPI 路由
├── main.py                # 主程序入口
├── requirements.txt       # Python 依赖
├── startup.sh             # 启动脚本
├── install.sh             # 安装脚本
├── setup_autostart.sh     # 自动启动设置
├── com.ocrmac.api.plist   # macOS LaunchAgent 配置
├── config.example.env     # 环境变量示例
└── README.md              # 项目文档
```

### 代码设计原则

- **低耦合，高内聚** - 各模块功能独立
- **完整的注释** - 每个函数都有详细说明
- **完备的日志系统** - 方便调试和监控
- **避免冗余代码** - 提高代码复用性
- **工程最佳实践** - 遵循 Python 和 FastAPI 最佳实践

### 测试

```bash
# 安装测试依赖
pip3 install pytest pytest-asyncio httpx

# 运行测试
pytest tests/
```

## 许可证

本项目基于原始 ocrmac 项目进行二次开发，请遵循相应的许可证要求。

## 支持

如果您遇到问题或有功能建议，请：

1. 查看故障排除部分
2. 检查日志文件
3. 提交 Issue 或 Pull Request

## 版本历史

- **v1.0.0** - 初始版本
  - 基础 OCR API 功能
  - macOS 自动启动支持
  - Bearer Token 认证
  - 完整的日志系统 