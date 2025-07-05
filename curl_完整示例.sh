#!/bin/bash

# OCR Mac API - 完整 curl 示例
# 包含中文识别优化配置

echo "🚀 OCR Mac API curl 示例"
echo "========================"

# 服务地址
SERVER_URL="http://localhost:8004"
AUTH_TOKEN="your-secure-token-here"

# 示例1：基本请求（使用测试图片的base64）
echo "📝 示例1: 基本OCR请求"
curl --location "${SERVER_URL}/predict" \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer ${AUTH_TOKEN}" \
--data '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAZAAAADICAIAAABJdyC1AAAWDElEQVR4nO3de0xUx+IH8LMgIC9BFAVRQNAiIiIoojy1IKJYxeIDUaKRJljjq1FJr4ni20Zag0UbY6wt1tZ3AbVagZYCoggiCDQoj0IRBJGHPEVY2Jveub/5bfZx2IVFGe/389dwds6cs2v4OjM7ZxCIRCIOAIAFau/6BgAA"
}'

echo -e "\n"

# 示例2：中文优化请求
echo "📝 示例2: 中文优化OCR请求"
curl --location "${SERVER_URL}/predict" \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer ${AUTH_TOKEN}" \
--data '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAZAAAADICAIAAABJdyC1AAAWDElEQVR4nO3de0xUx+IH8LMgIC9BFAVRQNAiIiIoojy1IKJYxeIDUaKRJljjq1FJr4ni20Zag0UbY6wt1tZ3AbVagZYCoggiCDQoj0IRBJGHPEVY2Jveub/5bfZx2IVFGe/389dwds6cs2v4OjM7ZxCIRCIOAIAFau/6BgAA",
    "language_preference": ["zh-Hans", "en-US"],
    "recognition_level": "accurate",
    "confidence_threshold": 0.0
}'

echo -e "\n"

# 示例3：详细OCR请求
echo "📝 示例3: 详细OCR请求"
curl --location "${SERVER_URL}/predict-detailed" \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer ${AUTH_TOKEN}" \
--data '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAZAAAADICAIAAABJdyC1AAAWDElEQVR4nO3de0xUx+IH8LMgIC9BFAVRQNAiIiIoojy1IKJYxeIDUaKRJljjq1FJr4ni20Zag0UbY6wt1tZ3AbVagZYCoggiCDQoj0IRBJGHPEVY2Jveub/5bfZx2IVFGe/389dwds6cs2v4OjM7ZxCIRCIOAIAFau/6BgAA",
    "language_preference": ["zh-Hans", "en-US"],
    "recognition_level": "accurate",
    "confidence_threshold": 0.0,
    "framework": "vision"
}'

echo -e "\n"

# 示例4：健康检查
echo "📝 示例4: 健康检查"
curl --location "${SERVER_URL}/health" \
--header 'Content-Type: application/json'

echo -e "\n"

# 示例5：获取支持的语言列表
echo "📝 示例5: 获取支持的语言"
curl --location "${SERVER_URL}/supported-languages" \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer ${AUTH_TOKEN}"

echo -e "\n"

# 示例6：不同语言配置示例
echo "📝 示例6: 不同语言配置"

# 仅中文
echo "6.1 仅中文识别:"
curl --location "${SERVER_URL}/predict" \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer ${AUTH_TOKEN}" \
--data '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAZAAAADICAIAAABJdyC1AAAWDElEQVR4nO3de0xUx+IH8LMgIC9BFAVRQNAiIiIoojy1IKJYxeIDUaKRJljjq1FJr4ni20Zag0UbY6wt1tZ3AbVagZYCoggiCDQoj0IRBJGHPEVY2Jveub/5bfZx2IVFGe/389dwds6cs2v4OjM7ZxCIRCIOAIAFau/6BgAA",
    "language_preference": ["zh-Hans"]
}'

echo -e "\n"

# 繁体中文
echo "6.2 繁体中文识别:"
curl --location "${SERVER_URL}/predict" \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer ${AUTH_TOKEN}" \
--data '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAZAAAADICAIAAABJdyC1AAAWDElEQVR4nO3de0xUx+IH8LMgIC9BFAVRQNAiIiIoojy1IKJYxeIDUaKRJljjq1FJr4ni20Zag0UbY6wt1tZ3AbVagZYCoggiCDQoj0IRBJGHPEVY2Jveub/5bfZx2IVFGe/389dwds6cs2v4OjM7ZxCIRCIOAIAFau/6BgAA",
    "language_preference": ["zh-Hant"]
}'

echo -e "\n"

# 多语言
echo "6.3 多语言识别:"
curl --location "${SERVER_URL}/predict" \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer ${AUTH_TOKEN}" \
--data '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAZAAAADICAIAAABJdyC1AAAWDElEQVR4nO3de0xUx+IH8LMgIC9BFAVRQNAiIiIoojy1IKJYxeIDUaKRJljjq1FJr4ni20Zag0UbY6wt1tZ3AbVagZYCoggiCDQoj0IRBJGHPEVY2Jveub/5bfZx2IVFGe/389dwds6cs2v4OjM7ZxCIRCIOAIAFau/6BgAA",
    "language_preference": ["zh-Hans", "en-US", "ja-JP", "ko-KR"]
}'

echo -e "\n========================"
echo "✅ 所有示例请求完成"

# 使用说明
echo "
💡 使用说明:
1. 将 'your-secure-token-here' 替换为实际的认证令牌
2. 将 'image_base64' 替换为实际的图片base64数据
3. 根据需要调整服务器地址和端口
4. 推荐使用 'zh-Hans,en-US' 配置获得最佳中英文识别效果

🔧 base64 图片生成方法:
# 从文件生成
base64 -i your_image.png | tr -d '\n'

# 从剪贴板生成 (macOS)
osascript -e 'the clipboard as «class PNGf»' | xxd -r -p | base64 | tr -d '\n'

📚 更多信息请参考:
- 使用指南.md
- 中文识别优化指南.md
" 