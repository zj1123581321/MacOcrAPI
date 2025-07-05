#!/bin/bash
# macOS 自动启动删除脚本

set -e

echo "========================"
echo "删除 OCR Mac API 自动启动"
echo "========================"

# 检查 macOS 系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "错误：此脚本只能在 macOS 系统上运行"
    exit 1
fi

PLIST_FILE="com.ocrmac.api.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "正在删除 OCR Mac API 自动启动配置..."

# 1. 停止服务
echo "1. 停止服务..."
if launchctl list | grep -q "com.ocrmac.api"; then
    launchctl stop com.ocrmac.api
    echo "✓ 服务已停止"
else
    echo "- 服务未运行"
fi

# 2. 卸载 LaunchAgent
echo "2. 卸载 LaunchAgent..."
if [ -f "$PLIST_PATH" ]; then
    launchctl unload "$PLIST_PATH"
    echo "✓ LaunchAgent 已卸载"
else
    echo "- LaunchAgent 配置文件不存在"
fi

# 3. 删除 plist 文件
echo "3. 删除配置文件..."
if [ -f "$PLIST_PATH" ]; then
    rm "$PLIST_PATH"
    echo "✓ 配置文件已删除: $PLIST_PATH"
else
    echo "- 配置文件不存在"
fi

# 4. 验证删除结果
echo "4. 验证删除结果..."
if launchctl list | grep -q "com.ocrmac.api"; then
    echo "✗ 警告：服务仍在运行中"
else
    echo "✓ 服务已完全移除"
fi

if [ -f "$PLIST_PATH" ]; then
    echo "✗ 警告：配置文件仍然存在"
else
    echo "✓ 配置文件已完全删除"
fi

echo ""
echo "========================"
echo "自动启动删除完成！"
echo "========================"
echo ""
echo "注意事项："
echo "- OCR Mac API 服务已停止"
echo "- 系统重启后不会自动启动该服务"
echo "- 如需手动启动，请使用: ./startup.sh"
echo "- 如需重新设置自动启动，请运行: ./setup_autostart.sh"
echo "" 