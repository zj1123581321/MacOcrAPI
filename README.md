# OCR Mac API

基于 macOS 原生 OCR 能力的高性能 HTTP API 服务。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置服务
```bash
cp config.example.env .env
# 编辑 .env 文件，修改认证令牌等配置
```

### 3. 启动服务
```bash
python3 main.py --port 8004
```

## 📝 API 使用

### 基本请求
```bash
curl --location 'http://localhost:8004/predict' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer your-secure-token-here' \
--data '{
    "image_base64": "图片的base64编码",
    "language_preference": ["zh-Hans", "en-US"],
    "recognition_level": "accurate"
}'
```

### 响应格式
```json
[
    {
        "dt_boxes": [[x1,y1],[x2,y1],[x2,y2],[x1,y2]],
        "rec_txt": "识别的文本",
        "score": 0.9999
    }
]
```

### 带排版功能的请求
```bash
curl --location 'http://localhost:8004/predict-format' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer your-secure-token-here' \
--data '{
    "image_base64": "图片的base64编码",
    "language_preference": ["zh-Hans", "en-US"],
    "recognition_level": "accurate",
    "enable_llm_format": true
}'
```

### 带排版的响应格式
```json
{
    "results": [
        {"dt_boxes": [[x1,y1],[x2,y1],[x2,y2],[x1,y2]], "rec_txt": "标题", "score": 0.99}
    ],
    "local_format": {
        "markdown": "# 标题\n\n正文内容",
        "success": true,
        "error": null
    },
    "llm_format": {
        "markdown": "# 标题\n\n正文内容（已校对）",
        "success": true,
        "error": null
    },
    "processing_time": 0.5,
    "image_size": [800, 600]
}
```

- `results`: 原始 OCR 结果（位置信息）
- `local_format`: 本地算法排版结果（始终返回）
- `llm_format`: LLM 排版结果（仅当 `enable_llm_format: true` 时返回）

## ⚙️ 重要配置

### 中文识别优化
在 `.env` 文件中设置：
```
LANGUAGE_PREFERENCE=zh-Hans,en-US
```

### 支持的语言
- `zh-Hans` - 简体中文
- `zh-Hant` - 繁体中文
- `en-US` - 英语
- `ja-JP` - 日语
- `ko-KR` - 韩语

### LLM 排版配置
使用 `/predict-format` 接口的 LLM 排版功能需要配置：
```
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-your-api-key
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT=30
```

支持任何 OpenAI 兼容的 API（如 OpenAI、Azure OpenAI、本地部署的模型等）。

## 🔧 macOS 自动启动

### 安装自动启动
```bash
./install.sh
```

### 设置开机启动
```bash
./setup_autostart.sh
```

## 📊 API 接口

- `POST /predict` - OCR 识别（返回位置信息）
- `POST /predict-detailed` - 详细识别结果
- `POST /predict-format` - 带排版的 OCR 识别（返回原始结果 + Markdown 排版）
- `GET /health` - 健康检查
- `GET /stats` - 统计信息（需认证）
- `GET /supported-languages` - 支持的语言列表（需认证）

## 📁 项目结构

```
250705_OcrMacApi/
├── src/                    # 核心源代码
│   ├── __init__.py        # 包初始化
│   ├── api.py             # FastAPI 路由和接口
│   ├── models.py          # 数据模型定义
│   ├── ocr_service.py     # OCR 服务封装
│   ├── config.py          # 配置管理
│   ├── formatter_local.py # 本地智能排版模块
│   └── formatter_llm.py   # LLM 排版模块
├── ocrmac-main/           # OCR 核心库
├── main.py                # 应用程序入口
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量配置
├── config.example.env     # 配置模板
├── .gitignore            # Git 忽略文件
├── startup.sh            # 启动脚本
├── install.sh            # 安装脚本
├── setup_autostart.sh    # 自动启动设置
├── com.ocrmac.api.plist  # macOS 服务配置
├── README.md             # 项目说明
└── logs/                 # 日志目录
```

## 🛠️ 故障排除

1. **中文识别效果差**：设置 `language_preference: ["zh-Hans", "en-US"]`
2. **认证失败**：检查 Authorization header 中的 Bearer token
3. **服务启动失败**：检查端口是否被占用，查看日志文件
4. **LLM 排版失败**：检查 `llm_format.error` 字段，常见原因：
   - 未配置 `LLM_BASE_URL` 或 `LLM_API_KEY`
   - API 请求超时（可调整 `LLM_TIMEOUT`）
   - API 密钥无效或余额不足

## �� 许可证

MIT License 