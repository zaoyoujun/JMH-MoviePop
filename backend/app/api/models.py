"""
影视管理系统 - 数据模型定义模块

此模块定义了所有 API 接口使用的数据结构，基于 Pydantic 实现类型安全验证。
"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class Progress(BaseModel):
    """
    播放进度模型
    
    Attributes:
        currentEpisode: 当前播放到第几集
        totalEpisodes: 总集数
        percent: 播放进度百分比
    """
    currentEpisode: int
    totalEpisodes: int
    percent: int


class MovieItem(BaseModel):
    """
    影视条目基础模型
    
    Attributes:
        id: 影视唯一标识
        title: 标题
        alias: 别名列表
        category: 分类 (movie/series/anime/variety/music/shorts/documentary/other)
        year: 上映年份
        sourceType: 来源类型 (webdav/openlist/local)
        sourceName: 来源名称
        durationText: 时长文本描述
        coverUrl: 封面图片URL
        backdropUrl: 背景图片URL
        tags: 标签列表
        score: 评分
        description: 简介描述
        isFavorite: 是否收藏
        progress: 播放进度
        updatedAt: 更新时间
    """
    id: str
    title: str
    alias: List[str] = []
    category: str
    year: int
    sourceType: str
    sourceName: str
    durationText: str
    coverUrl: str
    backdropUrl: str
    tags: List[str] = []
    score: Optional[float] = None
    description: Optional[str] = None
    isFavorite: bool = False
    progress: Optional[Progress] = None
    updatedAt: datetime


class Episode(BaseModel):
    """
    剧集模型
    
    Attributes:
        id: 剧集唯一标识
        title: 剧集标题
        episodeNumber: 集数编号
        durationText: 时长文本描述
        playUrl: 播放地址
        sourceType: 来源类型
    """
    id: str
    title: str
    episodeNumber: int
    durationText: str
    playUrl: str
    sourceType: str


class LibraryStats(BaseModel):
    """
    媒体库统计模型
    
    Attributes:
        total: 总数量
        remote: 远程来源数量
        local: 本地来源数量
        favorite: 收藏数量
    """
    total: int
    remote: int
    local: int
    favorite: int


class HeroItem(BaseModel):
    """
    首页轮播图条目模型
    
    Attributes:
        id: 影视唯一标识
        title: 标题
        category: 分类
        year: 上映年份
        sourceType: 来源类型
        sourceName: 来源名称
        durationText: 时长文本描述
        backdropUrl: 背景图片URL
        tags: 标签列表
    """
    id: str
    title: str
    category: str
    year: int
    sourceType: str
    sourceName: str
    durationText: str
    backdropUrl: str
    tags: List[str] = []


class Pagination(BaseModel):
    """
    分页信息模型
    
    Attributes:
        page: 当前页码
        pageSize: 每页数量
        total: 总数量
    """
    page: int
    pageSize: int
    total: int


class HomeResponse(BaseModel):
    """
    首页响应数据模型
    
    Attributes:
        stats: 媒体库统计
        hero: 轮播图列表
        items: 影视列表
    """
    stats: LibraryStats
    hero: List[HeroItem]
    items: List[MovieItem]


class MovieListResponse(BaseModel):
    """
    影视列表响应数据模型
    
    Attributes:
        list: 影视列表
        pagination: 分页信息
    """
    list: List[MovieItem]
    pagination: Pagination


class MovieDetailResponse(BaseModel):
    """
    影视详情响应数据模型
    
    Attributes:
        id: 影视唯一标识
        title: 标题
        alias: 别名列表
        category: 分类
        year: 上映年份
        sourceType: 来源类型
        sourceName: 来源名称
        durationText: 时长文本描述
        coverUrl: 封面图片URL
        backdropUrl: 背景图片URL
        tags: 标签列表
        score: 评分
        description: 简介描述
        isFavorite: 是否收藏
        episodes: 剧集列表
        progress: 播放进度
        updatedAt: 更新时间
    """
    id: str
    title: str
    alias: List[str] = []
    category: str
    year: int
    sourceType: str
    sourceName: str
    durationText: str
    coverUrl: str
    backdropUrl: str
    tags: List[str] = []
    score: Optional[float] = None
    description: Optional[str] = None
    isFavorite: bool = False
    episodes: List[Episode] = []
    progress: Optional[Progress] = None
    updatedAt: datetime


class PlayResponse(BaseModel):
    """
    播放地址响应数据模型
    
    Attributes:
        id: 影视唯一标识
        episodeId: 剧集ID（可选）
        playUrl: 播放URL
        headers: 请求头信息
        sourceType: 来源类型
    """
    id: str
    episodeId: Optional[str] = None
    playUrl: str
    headers: Dict[str, str] = {}
    sourceType: str


class ApiResponse(BaseModel):
    """
    统一 API 响应模型
    
    Attributes:
        code: 响应码 (0=成功, 400=参数错误, 404=资源不存在, 500=服务器错误)
        message: 响应消息
        data: 响应数据
    """
    code: int
    message: str
    data: Optional[dict] = None

    @classmethod
    def success(cls, data: dict = None):
        """
        创建成功响应
        
        Args:
            data: 响应数据
        
        Returns:
            ApiResponse: 成功响应对象
        """
        return cls(code=0, message="ok", data=data)

    @classmethod
    def error(cls, code: int, message: str):
        """
        创建错误响应
        
        Args:
            code: 错误码
            message: 错误消息
        
        Returns:
            ApiResponse: 错误响应对象
        """
        return cls(code=code, message=message, data=None)
