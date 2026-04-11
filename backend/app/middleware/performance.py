"""
性能监控中间件
"""
import time
from fastapi import Request, Response
from loguru import logger


async def performance_middleware(request: Request, call_next) -> Response:
    """性能监控中间件"""
    # 记录请求开始时间
    start_time = time.time()
    
    # 处理请求
    response = await call_next(request)
    
    # 计算请求处理时间
    process_time = time.time() - start_time
    
    # 将处理时间添加到响应头
    response.headers["X-Process-Time"] = str(process_time)
    
    # 记录请求信息和处理时间
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
    )
    
    # 对于处理时间超过1秒的请求，记录警告
    if process_time > 1.0:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} - {process_time:.4f}s"
        )
    
    return response
