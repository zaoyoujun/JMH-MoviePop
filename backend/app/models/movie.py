"""
影视数据模型模块

定义影视相关的数据结构，用于SQLite存储。
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class MovieBase(BaseModel):
    """影视基础模型"""
    title: str = Field(..., description="影视标题")
    year: Optional[int] = Field(default=None, description="上映年份")
    category: str = Field(default="movie", description="分类(movie/series/anime)")
    is_series: bool = Field(default=False, description="是否为剧集")
    resolution: str = Field(default="", description="分辨率")
    codec: str = Field(default="", description="视频编码")
    remote_provider: str = Field(default="", description="远程提供者")
    source_label: str = Field(default="", description="来源标签")
    cover_path: Optional[str] = Field(default=None, description="封面路径")
    intro: str = Field(default="", description="简介")
    actors: str = Field(default="", description="演员列表(逗号分隔)")
    director: str = Field(default="", description="导演")
    file_path: Optional[str] = Field(default=None, description="单文件路径(电影)")
    created_at: Optional[int] = Field(default=None, description="创建时间戳")


class MovieCreate(MovieBase):
    """创建影视请求模型"""
    pass


class MovieUpdate(BaseModel):
    """更新影视请求模型"""
    title: Optional[str] = Field(default=None, description="影视标题")
    year: Optional[int] = Field(default=None, description="上映年份")
    category: Optional[str] = Field(default=None, description="分类")
    cover_path: Optional[str] = Field(default=None, description="封面路径")
    intro: Optional[str] = Field(default=None, description="简介")
    actors: Optional[str] = Field(default=None, description="演员列表")
    director: Optional[str] = Field(default=None, description="导演")


class MovieResponse(MovieBase):
    """影视响应模型"""
    id: int = Field(..., description="影视ID")
    episodes: List[Dict[str, Any]] = Field(default_factory=list, description="剧集列表")


class EpisodeBase(BaseModel):
    """剧集基础模型"""
    movie_id: int = Field(..., description="所属影视ID")
    season: int = Field(default=1, description="季数")
    episode: int = Field(..., description="集数")
    file_path: str = Field(..., description="文件路径")


class EpisodeResponse(EpisodeBase):
    """剧集响应模型"""
    id: int = Field(..., description="剧集ID")


class LibraryStats(BaseModel):
    """媒体库统计模型"""
    total: int = Field(default=0, description="影视总数")
    movies: int = Field(default=0, description="电影数量")
    series: int = Field(default=0, description="剧集数量")
    anime: int = Field(default=0, description="动漫数量")
    total_episodes: int = Field(default=0, description="总集数")
