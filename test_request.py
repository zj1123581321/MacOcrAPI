#!/usr/bin/env python3
"""
OCR API 测试脚本
演示如何正确发送 HTTP 请求和处理 base64 图片
"""
import base64
import requests
import json
from PIL import Image
import io


def image_to_base64(image_path):
    """将图片文件转换为 base64 字符串"""
    try:
        with open(image_path, "rb") as image_file:
            # 读取图片文件
            image_data = image_file.read()
            # 编码为 base64
            base64_string = base64.b64encode(image_data).decode('utf-8')
            return base64_string
    except Exception as e:
        print(f"图片转换失败: {e}")
        return None


def create_test_image():
    """创建一个简单的测试图片并返回 base64"""
    # 创建一个简单的测试图片（200x100 像素，白色背景，黑色文字）
    from PIL import Image, ImageDraw, ImageFont
    
    # 创建图片
    img = Image.new('RGB', (300, 150), color='white')
    draw = ImageDraw.Draw(img)
    
    # 添加文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()
    
    # 绘制文字
    draw.text((20, 50), "Hello OCR!", fill='black', font=font)
    draw.text((20, 90), "测试文本", fill='black', font=font)
    
    # 转换为 base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)  # 重置指针
    img_data = buffer.getvalue()
    
    # 验证图像数据
    print(f"✓ 图像数据大小: {len(img_data)} bytes")
    
    # 生成 base64
    base64_string = base64.b64encode(img_data).decode('utf-8')
    
    # 验证 base64 格式
    print(f"✓ Base64 长度: {len(base64_string)} 字符")
    print(f"✓ Base64 前缀: {base64_string[:50]}...")
    
    # 保存测试图片
    img.save('test_image.png')
    print("✓ 测试图片已保存为 test_image.png")
    
    return base64_string


def test_ocr_api(base_url="http://localhost:8004", image_base64=None):
    """测试 OCR API"""
    
    if not image_base64:
        print("🖼️ 创建测试图片...")
        image_base64 = create_test_image()
    
    # API 端点
    url = f"{base_url}/predict"
    
    # 请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-secure-token-here'
    }
    
    # 请求数据
    data = {
        "image_base64": image_base64,
        "recognition_level": "accurate",  # 可选
        "confidence_threshold": 0.0       # 可选
    }
    
    print(f"📤 发送请求到 {url}")
    print(f"📊 图片 base64 长度: {len(image_base64)} 字符")
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📥 响应状态: {response.status_code}")
        print(f"📥 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功!")
            print(f"📝 识别结果:")
            for i, item in enumerate(result, 1):
                print(f"  {i}. 文本: '{item['rec_txt']}'")
                print(f"     置信度: {item['score']:.4f}")
                print(f"     边界框: {item['dt_boxes']}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"错误详情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误详情: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")


def test_health_check(base_url="http://localhost:8004"):
    """测试健康检查接口"""
    url = f"{base_url}/health"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 服务健康状态:")
            print(f"  状态: {health_data['status']}")
            print(f"  版本: {health_data['version']}")
            print(f"  运行时间: {health_data['uptime']:.2f} 秒")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查错误: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("OCR Mac API 测试工具")
    print("=" * 50)
    
    # 1. 健康检查
    print("\n1️⃣ 测试服务健康状态...")
    if not test_health_check():
        print("⚠️ 服务可能未启动，请先启动服务:")
        print("   python3 main.py --port 8004")
        return
    
    # 2. 测试 OCR API
    print("\n2️⃣ 测试 OCR API...")
    test_ocr_api()
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)


if __name__ == "__main__":
    main() 