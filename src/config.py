"""
配置管理模块
提供应用程序的配置管理功能
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用程序配置"""
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8004
    workers: int = 4
    
    # 安全配置
    auth_token: str = "test"
    allowed_origins: str = "*"  # 简化为字符串，在使用时转换为列表
    
    # OCR 配置
    recognition_level: str = "accurate"  # accurate 或 fast
    language_preference: Optional[str] = None  # 用逗号分隔的语言列表，如 "en-US,zh-Hans"
    confidence_threshold: float = 0.0
    framework: str = "vision"  # vision 或 livetext
    
    def get_language_preference_list(self) -> Optional[List[str]]:
        """将逗号分隔的语言字符串转换为列表"""
        if not self.language_preference:
            return None
        return [lang.strip() for lang in self.language_preference.split(",") if lang.strip()]
    
    # 应用配置
    app_name: str = "OCR Mac API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # 性能配置
    max_image_size: int = 10 * 1024 * 1024  # 10MB
    max_image_width: int = 20000  # 最大图像宽度
    max_image_height: int = 20000  # 最大图像高度
    request_timeout: int = 30  # 30秒
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings() 