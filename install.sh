#!/bin/bash
# OCR Mac API 自动安装脚本

set -e

echo "===================="
echo "OCR Mac API 安装脚本"
echo "===================="

# 检查 macOS 系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "错误：此应用程序只能在 macOS 系统上运行"
    exit 1
fi

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 Python 3，请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python 版本: $PYTHON_VERSION"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "错误：未找到 pip3，请先安装 pip"
    exit 1
fi

# 获取当前目录
INSTALL_DIR=$(pwd)
echo "安装目录: $INSTALL_DIR"

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "虚拟环境已激活"
fi

# 安装依赖
echo "安装 Python 依赖..."
pip3 install -r requirements.txt

# 创建日志目录
mkdir -p logs
echo "创建日志目录: $INSTALL_DIR/logs"

# 复制配置文件
if [ ! -f ".env" ]; then
    cp config.example.env .env
    echo "创建配置文件: .env"
    echo "请编辑 .env 文件以配置您的设置"
fi

# 设置脚本可执行权限
chmod +x startup.sh
echo "设置启动脚本权限"

# 更新 plist 文件中的路径
sed -i.bak "s|/Users/zhanglixing/Dev/projects/250705_OcrMacApi|$INSTALL_DIR|g" com.ocrmac.api.plist
echo "更新 LaunchAgent 配置文件"

# 测试安装
echo "测试安装..."
PYTHONPATH="$INSTALL_DIR:$INSTALL_DIR/ocrmac-main" python3 -c "
try:
    import fastapi
    import uvicorn
    import Vision
    import objc
    from PIL import Image
    import psutil
    from pydantic import BaseModel
    print('✓ 所有核心依赖都已正确安装')
    
    # 测试 OCR 功能
    from ocrmac.ocrmac import text_from_image
    print('✓ OCR 功能模块导入成功')
    
    # 测试配置
    from config import settings
    print('✓ 配置模块导入成功')
    
    # 测试数据模型
    from models import OCRRequest, OCRResponse
    print('✓ 数据模型导入成功')
    
    print('✓ 所有模块都可以正常导入，安装成功！')
    
except ImportError as e:
    print(f'✗ 依赖安装失败: {e}')
    print('请尝试手动安装：pip3 install -r requirements.txt')
    exit(1)
except Exception as e:
    print(f'✗ 测试时发生错误: {e}')
    print('依赖已安装但可能存在配置问题')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "===================="
    echo "安装完成！"
    echo "===================="
    echo ""
    echo "快速启动："
    echo "  python3 main.py"
    echo ""
    echo "后台启动："
    echo "  ./startup.sh"
    echo ""
    echo "设置自动启动："
    echo "  ./setup_autostart.sh"
    echo ""
    echo "API 文档："
    echo "  http://localhost:8003/docs"
    echo ""
    echo "请编辑 .env 文件以配置您的设置"
else
    echo "安装失败，请检查错误信息"
    exit 1
fi 