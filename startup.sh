#!/bin/bash
# OCR Mac API 启动脚本

# 设置工作目录
cd "$(dirname "$0")"
SCRIPT_DIR="$PWD"

# 创建日志目录
mkdir -p logs

# 加载环境变量（如果存在）
if [ -f ".env" ]; then
    # 只导出非注释行和非空行
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# 设置 Python 路径
export PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/src:$SCRIPT_DIR/ocrmac-main:$PYTHONPATH"

# 确定Python解释器路径
if [ -d "venv" ]; then
    echo "检测到虚拟环境，使用venv中的Python..."
    PYTHON_BIN="$SCRIPT_DIR/venv/bin/python3"
    PIP_BIN="$SCRIPT_DIR/venv/bin/pip3"
    
    # 检查虚拟环境是否有效
    if [ -x "$PYTHON_BIN" ]; then
        echo "✓ 虚拟环境Python路径: $PYTHON_BIN"
    else
        echo "✗ 虚拟环境损坏，请重新创建"
        exit 1
    fi
else
    echo "未找到虚拟环境，使用系统Python..."
    PYTHON_BIN="python3"
    PIP_BIN="pip3"
fi

# 检查 Python 版本
PYTHON_VERSION=$($PYTHON_BIN --version 2>&1 | cut -d' ' -f2)
echo "Python 版本: $PYTHON_VERSION"
echo "Python 路径: $PYTHON_BIN"

# 检查依赖
echo "检查依赖..."
$PYTHON_BIN -c "import fastapi, uvicorn, Vision, objc, PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "缺少依赖，尝试安装..."
    $PIP_BIN install -r requirements.txt
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
exec $PYTHON_BIN main.py --host 0.0.0.0 --port 8004 --workers 20 --log-level INFO 