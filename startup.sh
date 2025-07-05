#!/bin/bash
# OCR Mac API 启动脚本

# 设置工作目录
cd "$(dirname "$0")"

# 创建日志目录
mkdir -p logs

# 加载环境变量（如果存在）
if [ -f ".env" ]; then
    # 只导出非注释行和非空行
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# 设置 Python 路径
export PYTHONPATH="$PWD:$PWD/src:$PWD/ocrmac-main:$PYTHONPATH"

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python 版本: $PYTHON_VERSION"

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
    echo "虚拟环境已激活"
else
    echo "未找到虚拟环境，使用系统 Python"
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import fastapi, uvicorn, Vision, objc, PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "缺少依赖，尝试安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "依赖安装失败，退出"
        exit 1
    fi
fi

# 创建 PID 文件
echo $$ > ocrmac_api.pid

# 启动服务
echo "启动 OCR Mac API 服务..."
echo "时间: $(date)"
echo "PID: $$"
echo "工作目录: $PWD"
echo "=================================="

# 启动 API 服务
exec python3 main.py --host 0.0.0.0 --port 8003 --workers 4 --log-level INFO 