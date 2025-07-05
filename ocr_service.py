"""
OCR 服务封装模块
提供高级的 OCR 功能封装，包括性能优化和错误处理
"""
import asyncio
import base64
import io
import logging
import time
from typing import List, Optional, Tuple, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import sys
import os

# 添加 ocrmac 库的路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ocrmac-main'))

from ocrmac.ocrmac import OCR, text_from_image, livetext_from_image, convert_coordinates_pil
from models import OCRResult
from config import settings


class OCRService:
    """OCR 服务类"""
    
    def __init__(self):
        """初始化 OCR 服务"""
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=settings.workers)
        
        # 性能统计
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }
        
        self.logger.info(f"OCR 服务已初始化，使用 {settings.workers} 个工作线程")
    
    def _base64_to_image(self, base64_string: str) -> Image.Image:
        """将 Base64 字符串转换为 PIL 图像"""
        try:
            # 验证 base64 字符串格式
            if not base64_string:
                raise ValueError("base64 字符串不能为空")
            
            # 移除可能的 data URL 前缀
            if base64_string.startswith('data:image/'):
                base64_string = base64_string.split(',', 1)[1]
            
            # 添加缺失的填充
            missing_padding = len(base64_string) % 4
            if missing_padding:
                base64_string += '=' * (4 - missing_padding)
            
            self.logger.debug(f"处理 base64 字符串，长度: {len(base64_string)}")
            
            # 解码 base64
            try:
                image_data = base64.b64decode(base64_string, validate=True)
            except Exception as e:
                raise ValueError(f"base64 解码失败: {str(e)}")
            
            # 检查图像数据大小
            if len(image_data) < 100:  # 最小图像大小检查
                raise ValueError(f"图像数据太小，可能损坏 ({len(image_data)} bytes)")
            
            if len(image_data) > settings.max_image_size:
                raise ValueError(f"图像大小超过限制 ({settings.max_image_size} bytes)")
            
            self.logger.debug(f"图像数据解码成功，大小: {len(image_data)} bytes")
            
            # 创建 PIL 图像
            image_stream = io.BytesIO(image_data)
            
            try:
                # 尝试打开图像
                image = Image.open(image_stream)
                
                # 验证图像完整性
                image.verify()
                
                # 重新打开图像（verify 会关闭图像）
                image_stream.seek(0)
                image = Image.open(image_stream)
                
                # 确保图像完全加载
                image.load()
                
            except Exception as e:
                raise ValueError(f"图像文件格式无效或损坏: {str(e)}")
            
            # 检查图像尺寸
            if image.size[0] < 10 or image.size[1] < 10:
                raise ValueError(f"图像尺寸太小: {image.size}")
            
            if image.size[0] > 10000 or image.size[1] > 10000:
                raise ValueError(f"图像尺寸太大: {image.size}")
            
            # 转换为 RGB 模式（如果需要）
            if image.mode not in ['RGB', 'RGBA']:
                self.logger.debug(f"转换图像模式从 {image.mode} 到 RGB")
                image = image.convert('RGB')
            elif image.mode == 'RGBA':
                # 处理透明背景
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])
                image = rgb_image
            
            self.logger.debug(f"图像转换成功，尺寸: {image.size}，模式: {image.mode}")
            return image
            
        except ValueError:
            # 重新抛出已知的 ValueError
            raise
        except Exception as e:
            self.logger.error(f"图像转换失败: {str(e)}")
            raise ValueError(f"图像转换失败: {str(e)}")
    
    def _convert_result_format(self, 
                              ocr_results: List[Tuple[str, float, List[float]]], 
                              image_size: Tuple[int, int]) -> List[OCRResult]:
        """将 ocrmac 结果转换为 API 格式"""
        results = []
        
        for text, confidence, bbox in ocr_results:
            # 将相对坐标转换为像素坐标
            x, y, w, h = bbox
            x1, y1, x2, y2 = convert_coordinates_pil(
                (x, y, w, h), 
                image_size[0], 
                image_size[1]
            )
            
            # 创建边界框坐标 (左上，右上，右下，左下)
            dt_boxes = [
                [x1, y1],  # 左上
                [x2, y1],  # 右上
                [x2, y2],  # 右下
                [x1, y2]   # 左下
            ]
            
            result = OCRResult(
                dt_boxes=dt_boxes,
                rec_txt=text,
                score=confidence
            )
            results.append(result)
        
        return results
    
    def _perform_ocr(self, 
                     image: Image.Image, 
                     recognition_level: str,
                     language_preference: Optional[List[str]],
                     confidence_threshold: float,
                     framework: str) -> List[Tuple[str, float, List[float]]]:
        """执行 OCR 识别（同步）"""
        try:
            if framework == "livetext":
                # 使用 livetext 框架
                results = livetext_from_image(
                    image,
                    language_preference=language_preference,
                    detail=True
                )
                # livetext 返回的置信度始终为 1.0
                results = [(text, 1.0, bbox) for text, bbox in results]
            else:
                # 使用 vision 框架
                results = text_from_image(
                    image,
                    recognition_level=recognition_level,
                    language_preference=language_preference,
                    confidence_threshold=confidence_threshold,
                    detail=True
                )
            
            self.logger.debug(f"OCR 识别完成，找到 {len(results)} 个文本")
            return results
            
        except Exception as e:
            self.logger.error(f"OCR 识别失败: {str(e)}")
            raise RuntimeError(f"OCR 识别失败: {str(e)}")
    
    async def process_image(self, 
                          image_base64: str,
                          recognition_level: Optional[str] = None,
                          language_preference: Optional[List[str]] = None,
                          confidence_threshold: Optional[float] = None,
                          framework: Optional[str] = None) -> Dict[str, Any]:
        """
        异步处理图像 OCR
        
        Args:
            image_base64: Base64 编码的图像数据
            recognition_level: 识别级别
            language_preference: 语言偏好
            confidence_threshold: 置信度阈值
            framework: 使用的框架
            
        Returns:
            包含 OCR 结果的字典
        """
        start_time = time.time()
        
        try:
            # 更新统计信息
            self.stats['total_requests'] += 1
            
            # 使用默认值
            recognition_level = recognition_level or settings.recognition_level
            confidence_threshold = confidence_threshold or settings.confidence_threshold
            framework = framework or settings.framework
            language_preference = language_preference or settings.get_language_preference_list()
            
            # 转换图像
            image = self._base64_to_image(image_base64)
            image_size = image.size
            
            # 在线程池中执行 OCR
            loop = asyncio.get_event_loop()
            ocr_results = await loop.run_in_executor(
                self.executor,
                self._perform_ocr,
                image,
                recognition_level,
                language_preference,
                confidence_threshold,
                framework
            )
            
            # 转换结果格式
            results = self._convert_result_format(ocr_results, image_size)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 更新统计信息
            self.stats['successful_requests'] += 1
            self.stats['total_processing_time'] += processing_time
            self.stats['average_processing_time'] = (
                self.stats['total_processing_time'] / self.stats['total_requests']
            )
            
            self.logger.info(f"OCR 处理完成，耗时: {processing_time:.3f}s，文本数: {len(results)}")
            
            return {
                'results': results,
                'processing_time': processing_time,
                'image_size': image_size,
                'total_texts': len(results)
            }
            
        except Exception as e:
            # 更新统计信息
            self.stats['failed_requests'] += 1
            
            self.logger.error(f"OCR 处理失败: {str(e)}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }
        self.logger.info("统计信息已重置")
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)


# 全局 OCR 服务实例
ocr_service = OCRService() 