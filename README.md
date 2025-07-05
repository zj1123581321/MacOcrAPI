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

- `POST /predict` - OCR 识别
- `POST /predict-detailed` - 详细识别结果
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
│   └── config.py          # 配置管理
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

## �� 许可证

MIT License 