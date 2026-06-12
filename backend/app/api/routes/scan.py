"""
扫描API路由模块

提供媒体库扫描相关的API接口，包括：
1. 开始扫描媒体库
2. 刷新媒体库
3. 获取媒体库统计信息
4. 获取影视列表（支持分页、筛选、搜索）
5. 获取影视详情
"""

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Query

from app.core.response import success, error
from app.services.scan_service import scan_service

router = APIRouter(prefix="/api/scan", tags=["扫描管理"])


@router.post("/start", summary="开始扫描媒体库")
async def start_scan(
    source_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    开始扫描媒体库
    
    Args:
        source_id: 可选，指定要扫描的数据源ID，不指定则扫描所有数据源
    
    Returns:
        扫描结果，包含影视数量和统计信息
    """
    try:
        # 执行扫描
        result = scan_service.scan_library(source_id)
        
        if "error" in result:
            return error(400, result["error"])
        
        return success({
            "message": result["message"],
            "total": result["total"],
            "movies": result["movies"],
            "series": result["series"],
            "anime": result["anime"],
            "total_episodes": result["total_episodes"]
        })
    except Exception as e:
        return error(500, f"扫描失败: {str(e)}")


@router.post("/refresh", summary="刷新媒体库")
async def refresh_library():
    """
    刷新媒体库（强制重新扫描所有数据源）
    
    Returns:
        刷新结果，包含影视数量和统计信息
    """
    try:
        result = scan_service.refresh_library()
        
        if "error" in result:
            return error(400, result["error"])
        
        return success({
            "message": result["message"],
            "total": result["total"],
            "movies": result["movies"],
            "series": result["series"],
            "anime": result["anime"],
            "total_episodes": result["total_episodes"]
        })
    except Exception as e:
        return error(500, f"刷新失败: {str(e)}")


@router.get("/stats", summary="获取媒体库统计信息")
async def get_library_stats():
    """
    获取媒体库统计信息
    
    Returns:
        媒体库统计，包含影视总数、电影数量、剧集数量、动漫数量、总集数
    """
    try:
        stats = scan_service.get_library_stats()
        return success(stats)
    except Exception as e:
        return error(500, f"获取统计信息失败: {str(e)}")


@router.get("/movies", summary="获取影视列表")
async def get_movies(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(24, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类筛选(movie/series/anime)"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
):
    """
    分页获取影视列表
    
    Args:
        page: 页码，默认1
        page_size: 每页数量，默认24，最大100
        category: 分类筛选，可选值: movie(电影), series(剧集), anime(动漫)
        keyword: 关键词搜索，匹配标题或简介
    
    Returns:
        包含影视列表和分页信息的响应
    """
    try:
        result = scan_service.get_movies(page, page_size, category, keyword)
        return success(result)
    except Exception as e:
        return error(500, f"获取影视列表失败: {str(e)}")


@router.get("/movies/{movie_id}", summary="获取影视详情")
async def get_movie_detail(movie_id: int):
    """
    根据ID获取影视详情
    
    Args:
        movie_id: 影视ID
    
    Returns:
        影视详情信息，包含剧集列表
    """
    try:
        movie = scan_service.get_movie_by_id(movie_id)
        
        if not movie:
            return error(404, "影视不存在")
        
        return success(movie)
    except Exception as e:
        return error(500, f"获取影视详情失败: {str(e)}")
