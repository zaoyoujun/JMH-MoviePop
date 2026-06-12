"""
OpenList 代理路由模块

此模块提供前端连接到真实 OpenList 服务的透明代理接口。
"""

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

# 创建路由实例
router = APIRouter(prefix="/openlist", tags=["OpenList 代理"])

# OpenList 服务地址
OPENLIST_BASE_URL = "http://127.0.0.1:5244"


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"], summary="OpenList 透明代理")
async def proxy_openlist(request: Request, path: str):
    """
    透明代理接口，将所有请求直接转发到 OpenList 服务
    
    此接口不修改任何请求头，让前端自己处理认证。
    
    Args:
        request: 原始请求对象
        path: OpenList API 的路径（不含 /openlist 前缀）
    
    Returns:
        OpenList API 的响应内容
    """
    # 构建目标 URL
    target_url = f"{OPENLIST_BASE_URL}/{path}"
    
    # 获取请求方法和查询参数
    method = request.method
    query_params = dict(request.query_params)
    
    # 获取请求体
    try:
        body = await request.json()
    except:
        body = None
    
    # 获取请求头，过滤掉 host 头
    headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method,
                target_url,
                headers=headers,
                params=query_params,
                json=body,
                follow_redirects=True
            )
            
            # 返回流式响应
            return StreamingResponse(
                content=response.aiter_bytes(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except Exception as e:
            return {"code": -1, "message": f"代理请求失败: {str(e)}"}
