#!/bin/bash
# macOS 自动启动设置脚本

set -e

echo "========================"
echo "macOS 自动启动设置脚本"
echo "========================"

# 检查 macOS 系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "错误：此脚本只能在 macOS 系统上运行"
    exit 1
fi

# 获取当前目录
CURRENT_DIR=$(pwd)
PLIST_FILE="com.ocrmac.api.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

# 检查 plist 文件是否存在
if [ ! -f "$PLIST_FILE" ]; then
    echo "错误：未找到 $PLIST_FILE 文件"
    exit 1
fi

# 检查启动脚本是否存在
if [ ! -f "startup.sh" ]; then
    echo "错误：未找到 startup.sh 文件"
    exit 1
fi

# 确保启动脚本可执行
chmod +x startup.sh

# 创建 LaunchAgents 目录（如果不存在）
mkdir -p "$LAUNCH_AGENTS_DIR"

# 复制 plist 文件到 LaunchAgents 目录
echo "复制 LaunchAgent 配置文件..."
cp "$PLIST_FILE" "$LAUNCH_AGENTS_DIR/"

# 加载 LaunchAgent
echo "加载 LaunchAgent..."
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

# 启动服务
echo "启动服务..."
launchctl start com.ocrmac.api

# 等待服务启动
sleep 3

# 检查服务状态
echo "检查服务状态..."
if launchctl list | grep -q "com.ocrmac.api"; then
    echo "✓ 服务已成功启动"
    echo "✓ 自动启动已设置完成"
    echo ""
    echo "服务管理命令："
    echo "  启动服务: launchctl start com.ocrmac.api"
    echo "  停止服务: launchctl stop com.ocrmac.api"
    echo "  重启服务: launchctl stop com.ocrmac.api && launchctl start com.ocrmac.api"
    echo "  卸载服务: launchctl unload ~/Library/LaunchAgents/com.ocrmac.api.plist"
    echo ""
    echo "日志查看："
    echo "  标准输出: tail -f $CURRENT_DIR/logs/ocrmac_api.log"
    echo "  错误输出: tail -f $CURRENT_DIR/logs/ocrmac_api_error.log"
    echo ""
    echo "API 访问："
    echo "  服务地址: http://localhost:8003"
    echo "  API 文档: http://localhost:8003/docs"
    echo "  健康检查: http://localhost:8003/health"
else
    echo "✗ 服务启动失败"
    echo "请检查日志文件以获取更多信息："
    echo "  $CURRENT_DIR/logs/ocrmac_api_error.log"
    exit 1
fi 