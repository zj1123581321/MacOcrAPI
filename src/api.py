"""
FastAPI 路由和处理逻辑
提供 HTTP API 接口
"""
import logging
import time
from datetime import datetime
from typing import List, Dict, Any
import platform
import psutil

from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .models import (
    OCRRequest,
    ErrorResponse,
    HealthCheckResponse,
    OCRResult,
    OCRFormatRequest,
    OCRFormatResponse,
    FormattedResult
)
from .ocr_service import ocr_service
from .config import settings
from .formatter_local import format_locally
from .formatter_llm import format_with_llm

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.log_file) if settings.log_file else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于 ocrmac 的高并发 OCR API 服务",
    debug=settings.debug
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origins] if settings.allowed_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全认证
security = HTTPBearer()

# 应用启动时间
app_start_time = time.time()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """验证认证令牌"""
    if credentials.credentials != settings.auth_token:
        raise HTTPException(
            status_code=401,
            detail="无效的认证令牌"
        )
    return credentials.credentials


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 异常处理器"""
    logger.error(f"HTTP 异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP_ERROR",
            message=exc.detail,
            code=exc.status_code,
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.error(f"请求验证异常: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="VALIDATION_ERROR",
            message=f"请求验证失败: {exc.errors()}",
            code=422,
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未捕获的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_ERROR",
            message="服务器内部错误",
            code=500,
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time = time.time()
    
    # 记录请求
    logger.info(f"收到请求: {request.method} {request.url}")
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录响应
    logger.info(f"响应完成: {response.status_code} - 耗时: {process_time:.3f}s")
    
    # 添加处理时间到响应头
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


@app.get("/", response_model=Dict[str, str])
async def root():
    """根路径"""
    return {
        "message": "欢迎使用 OCR Mac API 服务",
        "version": settings.app_version,
        "documentation": "/docs"
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """健康检查"""
    uptime = time.time() - app_start_time
    
    # 获取系统信息
    system_info = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "memory_percent": psutil.virtual_memory().percent
    }
    
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        uptime=uptime,
        system_info=system_info
    )


@app.get("/stats", response_model=Dict[str, Any])
async def get_stats(token: str = Depends(verify_token)):
    """获取服务统计信息"""
    stats = ocr_service.get_stats()
    uptime = time.time() - app_start_time
    
    return {
        "service_stats": stats,
        "uptime": uptime,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/reset-stats", response_model=Dict[str, str])
async def reset_stats(token: str = Depends(verify_token)):
    """重置统计信息"""
    ocr_service.reset_stats()
    return {"message": "统计信息已重置"}


@app.post("/predict", response_model=List[OCRResult])
async def predict(
    request: OCRRequest,
    token: str = Depends(verify_token)
):
    """
    OCR 预测接口
    
    根据您提供的示例格式，直接返回 OCR 结果列表
    """
    try:
        logger.info("开始处理 OCR 请求")
        
        # 处理图像
        result = await ocr_service.process_image(
            image_base64=request.image_base64,
            recognition_level=request.recognition_level,
            language_preference=request.language_preference,
            confidence_threshold=request.confidence_threshold,
            framework=request.framework
        )
        
        logger.info(f"OCR 处理完成，返回 {len(result['results'])} 个结果")
        
        # 直接返回结果列表，符合示例格式
        return result['results']
        
    except ValueError as e:
        logger.error(f"输入验证错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"OCR 处理错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部错误")


@app.post("/predict-format", response_model=OCRFormatResponse)
async def predict_format(
    request: OCRFormatRequest,
    token: str = Depends(verify_token)
):
    """
    带排版功能的 OCR 预测接口

    返回原始 OCR 结果 + 本地排版结果 + 可选的 LLM 排版结果
    """
    try:
        logger.info(f"开始处理带排版的 OCR 请求，enable_llm_format={request.enable_llm_format}")

        # 处理图像 OCR
        result = await ocr_service.process_image(
            image_base64=request.image_base64,
            recognition_level=request.recognition_level,
            language_preference=request.language_preference,
            confidence_threshold=request.confidence_threshold,
            framework=request.framework
        )

        ocr_results = result['results']
        image_size = result['image_size']
        processing_time = result['processing_time']

        # 本地排版（始终执行）
        local_format = format_locally(ocr_results, image_size)

        # LLM 排版（可选）
        llm_format = None
        if request.enable_llm_format:
            llm_format = await format_with_llm(ocr_results)

        logger.info(f"带排版 OCR 处理完成，返回 {len(ocr_results)} 个结果")

        return OCRFormatResponse(
            results=ocr_results,
            local_format=local_format,
            llm_format=llm_format,
            processing_time=processing_time,
            image_size=image_size
        )

    except ValueError as e:
        logger.error(f"输入验证错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"OCR 处理错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部错误")


@app.get("/supported-languages", response_model=Dict[str, List[str]])
async def get_supported_languages(token: str = Depends(verify_token)):
    """获取支持的语言列表"""
    try:
        # 导入必要的模块
        import Vision
        import objc
        
        with objc.autorelease_pool():
            req = Vision.VNRecognizeTextRequest.alloc().init()
            
            # 获取不同识别级别的支持语言
            req.setRecognitionLevel_(0)  # accurate
            accurate_languages = req.supportedRecognitionLanguagesAndReturnError_(None)[0]
            
            req.setRecognitionLevel_(1)  # fast
            fast_languages = req.supportedRecognitionLanguagesAndReturnError_(None)[0]
            
            return {
                "accurate": list(accurate_languages),
                "fast": list(fast_languages)
            }
            
    except Exception as e:
        logger.error(f"获取支持语言失败: {str(e)}")
        raise HTTPException(status_code=500, detail="无法获取支持的语言列表")


# 应用启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"{settings.app_name} v{settings.app_version} 启动完成")
    logger.info(f"服务器地址: http://{settings.host}:{settings.port}")
    logger.info(f"API 文档: http://{settings.host}:{settings.port}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info(f"{settings.app_name} 正在关闭...")
    # 这里可以添加清理代码 