"""
影视管理系统 - 影视 API 路由模块

此模块定义了影视相关的所有 API 端点，包括：
- 首页数据获取
- 影视列表查询（支持筛选、搜索、分页）
- 影视详情获取
- 播放地址获取
- 封面图片访问

所有接口均返回统一格式的响应，便于前端处理。
"""

import os
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import FileResponse, Response

from ..models import ApiResponse
from ..mock_data import (
    get_mock_movie_by_id,
    get_mock_episodes,
    get_mock_play_url,
)
from app.config.app_config import AppConfig
from app.services.scan_service import scan_service

# 获取封面目录路径
config = AppConfig()
COVER_DIR = os.path.join(str(config.DATA_DIR), "covers")

# 创建路由实例，前缀为 /api/movies，标签为 movies
router = APIRouter(prefix="/api/movies", tags=["movies"])


def _convert_movie_to_frontend(movie: dict) -> dict:
    """
    将数据库中的影视数据转换为前端期望的格式
    
    Args:
        movie: 数据库中的影视字典
    
    Returns:
        前端期望格式的影视字典
    """
    # 处理封面路径：如果是本地路径，转换为 API 访问路径
    cover_path = movie.get("cover_path", "")
    cover_url = ""
    if cover_path and cover_path != "None" and cover_path != "null":
        # 提取封面文件名
        cover_name = os.path.basename(cover_path)
        if cover_name:
            cover_url = f"/api/movies/cover/{cover_name}"
    
    return {
        "id": f"movie-{movie.get('id', '')}",
        "title": movie.get("title", ""),
        "alias": [],
        "category": movie.get("category", "movie"),
        "year": movie.get("year"),
        "sourceType": movie.get("remote_provider", "local"),
        "sourceName": movie.get("source_label", ""),
        "durationText": "",
        "coverUrl": cover_url or "https://via.placeholder.com/300x450",
        "backdropUrl": "",
        "tags": [],
        "score": 0,
        "description": movie.get("intro", ""),
        "isFavorite": False,
        "progress": None
    }


@router.get("/home", summary="获取首页数据")
async def get_home_data(
    category: Optional[str] = Query(None, description="当前分类，不传表示全部"),
    limit: int = Query(12, description="首页列表数量")
):
    """
    获取首页数据接口
    
    用于首页一次性渲染大海报轮播、统计条和默认影视列表。
    
    Args:
        category: 分类筛选，不传表示全部
        limit: 首页列表数量，默认12
    
    Returns:
        ApiResponse: 包含统计信息、轮播图和影视列表的响应
    """
    try:
        # 从扫描服务获取实际媒体库数据
        stats = scan_service.get_library_stats()
        movies_result = scan_service.get_movies(page=1, page_size=limit, category=category)
        
        # 转换数据格式（注意：get_movies 返回的键是 'list' 而不是 'movies'）
        movies = [_convert_movie_to_frontend(m) for m in movies_result.get("list", [])]
        
        # 生成轮播图（取前4个）
        hero_items = movies[:4]
        
        # 构建响应数据
        response_data = {
            "stats": {
                "total": stats.get("total", 0),
                "remote": 0,
                "local": 0,
                "favorite": 0
            },
            "hero": hero_items,
            "items": movies[:limit]
        }
        
        return ApiResponse.success(response_data)
    except Exception as e:
        # 如果获取实际数据失败，返回空数据
        return ApiResponse.success({
            "stats": {
                "total": 0,
                "remote": 0,
                "local": 0,
                "favorite": 0
            },
            "hero": [],
            "items": []
        })


@router.get("", summary="获取影视列表")
async def get_movie_list(
    category: Optional[str] = Query(None, description="分类"),
    keyword: Optional[str] = Query(None, description="按标题、别名、简介搜索"),
    sourceType: Optional[str] = Query(None, description="webdav / openlist / local"),
    favorite: Optional[bool] = Query(None, description="是否只看收藏"),
    page: int = Query(1, description="页码"),
    pageSize: int = Query(24, description="每页数量")
):
    """
    获取影视列表接口
    
    用于分类页、搜索、分页加载。支持多种筛选条件组合。
    
    Args:
        category: 分类筛选
        keyword: 搜索关键词（匹配标题、别名、简介）
        sourceType: 来源类型筛选
        favorite: 是否只显示收藏
        page: 页码，默认1
        pageSize: 每页数量，默认24
    
    Returns:
        ApiResponse: 包含影视列表和分页信息的响应
    """
    try:
        # 从扫描服务获取实际数据
        movies_result = scan_service.get_movies(page=page, page_size=pageSize, category=category, keyword=keyword)
        
        # 转换数据格式
        movies = [_convert_movie_to_frontend(m) for m in movies_result.get("list", [])]
        
        # 返回成功响应（注意：分页信息在 'pagination' 键中）
        return ApiResponse.success({
            "list": movies,
            "pagination": {
                "page": page,
                "pageSize": pageSize,
                "total": movies_result.get("pagination", {}).get("total", 0)
            }
        })
    except Exception as e:
        # 如果获取实际数据失败，返回空数据
        return ApiResponse.success({
            "list": [],
            "pagination": {
                "page": page,
                "pageSize": pageSize,
                "total": 0
            }
        })


@router.get("/{movie_id}", summary="获取影视详情")
async def get_movie_detail(movie_id: str):
    """
    获取影视详情接口
    
    用于详情页展示完整的影视信息和剧集列表。
    
    Args:
        movie_id: 影视唯一标识
    
    Returns:
        ApiResponse: 包含影视详情和剧集列表的响应
    """
    try:
        # 提取实际的电影ID（去除前缀）
        actual_id = movie_id.replace("movie-", "")
        
        # 从扫描服务获取实际数据
        movie = scan_service.get_movie_by_id(int(actual_id) if actual_id.isdigit() else 0)
        
        # 如果影视不存在，返回404错误
        if not movie:
            return ApiResponse.error(404, "movie not found")
        
        # 转换数据格式
        movie_dict = _convert_movie_to_frontend(movie)
        
        # 处理剧集列表
        episodes = movie.get("episodes", [])
        movie_dict["episodes"] = [{
            "id": f"{movie_id}-ep{e.get('episode', '')}",
            "title": f"第{e.get('episode', '')}集",
            "episodeNumber": e.get("episode", 0),
            "durationText": "",
            "playUrl": e.get("file_path", ""),
            "sourceType": movie.get("remote_provider", "local")
        } for e in episodes]
        
        # 返回成功响应
        return ApiResponse.success(movie_dict)
    except Exception as e:
        # 如果获取实际数据失败，返回错误
        return ApiResponse.error(500, str(e))


@router.get("/{movie_id}/play", summary="获取播放地址")
async def get_play_url(
    movie_id: str,
    episodeId: Optional[str] = Query(None, description="剧集/动漫可传；电影可不传")
):
    """
    获取播放地址接口
    
    用于点击"立即播放"时获取实际播放URL。
    
    Args:
        movie_id: 影视唯一标识
        episodeId: 剧集ID（可选，电影可不传）
    
    Returns:
        ApiResponse: 包含播放地址和请求头的响应
    """
    # 验证影视是否存在
    movie = get_mock_movie_by_id(movie_id)
    
    # 如果影视不存在，返回404错误
    if not movie:
        return ApiResponse.error(404, "movie not found")
    
    # 获取播放地址信息
    play_response = get_mock_play_url(movie_id, episodeId)
    
    # 返回成功响应
    return ApiResponse.success(play_response.model_dump())


@router.get("/cover/{cover_name}", summary="获取封面图片")
async def get_cover(cover_name: str):
    """
    获取封面图片接口
    
    用于前端展示影视封面。
    
    Args:
        cover_name: 封面文件名
    
    Returns:
        FileResponse: 封面图片文件
    """
    # 安全检查：防止路径遍历
    if ".." in cover_name or "/" in cover_name or "\\" in cover_name:
        return Response(status_code=400, content="Invalid cover name")
    
    # 构建封面文件路径
    cover_path = os.path.join(COVER_DIR, cover_name)
    
    # 检查文件是否存在
    if not os.path.exists(cover_path):
        return Response(status_code=404, content="Cover not found")
    
    # 获取文件扩展名，设置正确的 Content-Type
    _, ext = os.path.splitext(cover_name)
    content_type = "image/jpeg"
    if ext.lower() == ".png":
        content_type = "image/png"
    elif ext.lower() == ".webp":
        content_type = "image/webp"
    
    # 返回文件
    return FileResponse(cover_path, media_type=content_type)
