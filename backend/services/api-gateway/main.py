"""
API网关 - 微服务入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import loguru

from app.core.config import settings


# 创建FastAPI应用
app = FastAPI(
    title="API Gateway",
    version=settings.APP_VERSION,
    description="API网关 - 心灵伴侣AI",
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 服务地址映射
SERVICE_URLS = {
    "auth": "http://auth-service:8000",
    "chat": "http://chat-service:8000",
    "member": "http://member-service:8000",
    "user": "http://user-service:8000",
    "mbti": "http://mbti-service:8000",
    "diary": "http://diary-service:8000",
    "knowledge": "http://knowledge-service:8000",
}


async def forward_request(service: str, path: str, method: str, headers: dict, body: bytes):
    """转发请求到微服务"""
    service_url = SERVICE_URLS.get(service)
    if not service_url:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Service {service} not found"}
        )

    url = f"{service_url}{path}"
    loguru.logger.info(f"Forwarding request to {url}")

    try:
        async with httpx.AsyncClient() as client:
            kwargs = {
                "headers": headers,
                "timeout": 30.0,
            }
            if body:
                kwargs["content"] = body

            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            elif method == "PUT":
                response = await client.put(url, **kwargs)
            elif method == "DELETE":
                response = await client.delete(url, **kwargs)
            else:
                return JSONResponse(
                    status_code=405,
                    content={"detail": f"Method {method} not allowed"}
                )

            return JSONResponse(
                status_code=response.status_code,
                content=response.json(),
                headers=dict(response.headers)
            )
    except Exception as e:
        loguru.error(f"Error forwarding request: {e}")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Service {service} unavailable"}
        )


@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_route(request: Request, path: str):
    """认证服务路由"""
    headers = dict(request.headers)
    body = await request.body()
    return await forward_request("auth", f"/api/v1/auth/{path}", request.method, headers, body)


@app.api_route("/api/v1/chat/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def chat_route(request: Request, path: str):
    """聊天服务路由"""
    headers = dict(request.headers)
    body = await request.body()
    return await forward_request("chat", f"/api/v1/chat/{path}", request.method, headers, body)


@app.api_route("/api/v1/member/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def member_route(request: Request, path: str):
    """会员服务路由"""
    headers = dict(request.headers)
    body = await request.body()
    return await forward_request("member", f"/api/v1/member/{path}", request.method, headers, body)


@app.api_route("/api/v1/payment/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def payment_route(request: Request, path: str):
    """支付服务路由"""
    headers = dict(request.headers)
    body = await request.body()
    return await forward_request("member", f"/api/v1/payment/{path}", request.method, headers, body)


@app.api_route("/api/v1/user/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_route(request: Request, path: str):
    """用户服务路由"""
    headers = dict(request.headers)
    body = await request.body()
    return await forward_request("user", f"/api/v1/user/{path}", request.method, headers, body)


@app.api_route("/api/v1/mbti/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def mbti_route(request: Request, path: str):
    """MBTI服务路由"""
    headers = dict(request.headers)
    body = await request.body()
    return await forward_request("mbti", f"/api/v1/mbti/{path}", request.method, headers, body)


@app.api_route("/api/v1/diary/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def diary_route(request: Request, path: str):
    """日记服务路由"""
    headers = dict(request.headers)
    body = await request.body()
    return await forward_request("diary", f"/api/v1/diary/{path}", request.method, headers, body)


@app.api_route("/api/v1/knowledge/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def knowledge_route(request: Request, path: str):
    """知识库服务路由"""
    headers = dict(request.headers)
    body = await request.body()
    return await forward_request("knowledge", f"/api/v1/knowledge/{path}", request.method, headers, body)


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "api-gateway",
        "version": settings.APP_VERSION,
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "API Gateway",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
