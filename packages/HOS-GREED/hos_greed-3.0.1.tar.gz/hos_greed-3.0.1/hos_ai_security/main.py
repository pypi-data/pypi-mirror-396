import socket
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router as api_router
from .config.config import settings


def find_available_port(start_port: int = 50000) -> int:
    """查找从指定端口开始的第一个可用端口"""
    port = start_port
    while True:
        try:
            # 尝试创建socket并绑定到指定端口
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
                return port
        except OSError:
            # 端口被占用，尝试下一个
            port += 1

# 创建FastAPI应用
app = FastAPI(
    title="AI安全赋能平台",
    version="3.0.0",
    description="轻量化AI安全平台，适合中小型企业",
    debug=settings.debug
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应设置具体的允许来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含统一API路由 - 轻量化设计核心
app.include_router(api_router)

# 根路径
@app.get("/")
async def root():
    return {
        "message": "安全智能体系统",
        "version": settings.app_version,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# 命令行入口点
def main():
    """主入口函数，用于命令行启动应用"""
    import uvicorn
    # 查找从50000开始的可用端口
    port = find_available_port(50000)
    print(f"Starting HOS AI Security server on port {port}...")
    print(f"Documentation available at: http://localhost:{port}/docs")
    print(f"API endpoint: http://localhost:{port}/api/v3/ai-security")
    uvicorn.run(
        "hos_ai_security.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug
    )

# 启动应用（仅用于开发环境）
if __name__ == "__main__":
    main()
