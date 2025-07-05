"""
主应用程序入口
使用 uvicorn 启动 FastAPI 服务器
"""
import uvicorn
import argparse
import logging
import sys
import os

from config import settings

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="OCR Mac API 服务")
    parser.add_argument("--host", default=settings.host, help="服务器地址")
    parser.add_argument("--port", type=int, default=settings.port, help="服务器端口")
    parser.add_argument("--workers", type=int, default=settings.workers, help="工作进程数")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    parser.add_argument("--reload", action="store_true", help="自动重载")
    parser.add_argument("--log-level", default=settings.log_level, help="日志级别")
    
    args = parser.parse_args()
    
    # 检查 macOS 系统
    if sys.platform != "darwin":
        logger.error("此应用程序只能在 macOS 系统上运行")
        sys.exit(1)
    
    # 检查必要的依赖
    try:
        import Vision
        import objc
        from PIL import Image
        logger.info("必要的依赖检查通过")
    except ImportError as e:
        logger.error(f"缺少必要的依赖: {e}")
        logger.error("请运行 'pip install -r requirements.txt' 安装依赖")
        sys.exit(1)
    
    # 启动服务器
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")
    logger.info(f"服务器地址: http://{args.host}:{args.port}")
    logger.info(f"API 文档: http://{args.host}:{args.port}/docs")
    
    try:
        uvicorn.run(
            "api:app",
            host=args.host,
            port=args.port,
            workers=args.workers if not args.debug else 1,
            reload=args.reload,
            log_level=args.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 