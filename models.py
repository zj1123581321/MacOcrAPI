"""
数据模型定义
包含 API 请求和响应的数据结构
"""
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field, validator
import base64
import binascii


class OCRRequest(BaseModel):
    """OCR 请求模型"""
    
    image_base64: str = Field(..., description="Base64 编码的图像数据")
    recognition_level: Optional[str] = Field(
        None, 
        description="识别级别 ('accurate' 或 'fast')"
    )
    language_preference: Optional[List[str]] = Field(
        None, 
        description="语言偏好列表，如 ['en-US', 'zh-Hans']"
    )
    confidence_threshold: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0, 
        description="置信度阈值 (0.0-1.0)"
    )
    framework: Optional[str] = Field(
        None, 
        description="使用的框架 ('vision' 或 'livetext')"
    )
    
    @validator('image_base64')
    def validate_base64(cls, v):
        """验证 Base64 图像数据"""
        if not v:
            raise ValueError("图像数据不能为空")
        
        try:
            # 尝试解码 base64
            base64.b64decode(v, validate=True)
        except (binascii.Error, ValueError):
            raise ValueError("无效的 Base64 图像数据")
        
        return v
    
    @validator('recognition_level')
    def validate_recognition_level(cls, v):
        """验证识别级别"""
        if v is not None and v not in ['accurate', 'fast']:
            raise ValueError("识别级别必须是 'accurate' 或 'fast'")
        return v
    
    @validator('framework')
    def validate_framework(cls, v):
        """验证框架选择"""
        if v is not None and v not in ['vision', 'livetext']:
            raise ValueError("框架必须是 'vision' 或 'livetext'")
        return v


class BoundingBox(BaseModel):
    """边界框模型"""
    
    x: float = Field(..., description="X 坐标 (0-1)")
    y: float = Field(..., description="Y 坐标 (0-1)")
    width: float = Field(..., description="宽度 (0-1)")
    height: float = Field(..., description="高度 (0-1)")


class OCRResult(BaseModel):
    """单个 OCR 结果"""
    
    dt_boxes: List[List[float]] = Field(..., description="检测框坐标")
    rec_txt: str = Field(..., description="识别的文本")
    score: float = Field(..., description="置信度分数")


class OCRResponse(BaseModel):
    """OCR 响应模型"""
    
    results: List[OCRResult] = Field(..., description="OCR 结果列表")
    processing_time: float = Field(..., description="处理时间（秒）")
    image_size: Tuple[int, int] = Field(..., description="图像尺寸 (width, height)")
    total_texts: int = Field(..., description="识别的文本总数")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    code: int = Field(..., description="错误代码")
    timestamp: str = Field(..., description="时间戳")


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="应用版本")
    uptime: float = Field(..., description="运行时间（秒）")
    system_info: dict = Field(..., description="系统信息") 