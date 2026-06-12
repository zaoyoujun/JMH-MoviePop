"""
影视管理系统 - 主应用入口模块

此模块是 FastAPI 应用的主入口，负责：
1. 创建 FastAPI 应用实例
2. 配置 CORS 中间件
3. 注册路由
4. 提供健康检查接口

运行方式：python run.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入影视 API 路由
from app.api.routes import movies_router, openlist_router, sources_router, scan_router

# 创建 FastAPI 应用实例
app = FastAPI(
    title="JMH-MoviePop API",           # API 标题
    description="影视管理系统后端 API",  # API 描述
    version="1.0.0"                      # API 版本
)

# 配置 CORS 中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 允许所有来源（生产环境应限制具体域名）
    allow_credentials=True,     # 允许携带凭证
    allow_methods=["*"],        # 允许所有 HTTP 方法
    allow_headers=["*"],        # 允许所有请求头
)

# 注册影视 API 路由
app.include_router(movies_router)

# 注册 OpenList 代理路由
app.include_router(openlist_router)

# 注册服务器管理路由（Mock）
app.include_router(sources_router)

# 注册扫描管理路由
app.include_router(scan_router)


@app.get("/", summary="根路径")
async def root():
    """
    根路径接口
    
    返回服务运行状态信息。
    
    Returns:
        dict: 欢迎消息
    """
    return {"message": "JMH-MoviePop API is running"}


@app.get("/health", summary="健康检查")
async def health_check():
    """
    健康检查接口
    
    用于监控服务状态，返回服务健康状况。
    
    Returns:
        dict: 健康状态信息
    """
    return {"status": "healthy"}
