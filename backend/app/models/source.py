"""
数据源模型模块

定义数据源相关的数据结构。
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class SourceBase(BaseModel):
    """数据源基础模型"""
    name: str = Field(..., description="数据源名称")
    type: str = Field(..., description="数据源类型")
    path: str = Field(..., description="数据源路径")
    username: Optional[str] = Field(default="", description="用户名")
    password: Optional[str] = Field(default="", description="密码")


class SourceCreate(SourceBase):
    """创建数据源请求模型"""
    pass


class SourceUpdate(BaseModel):
    """更新数据源请求模型"""
    name: Optional[str] = Field(default=None, description="数据源名称")
    path: Optional[str] = Field(default=None, description="数据源路径")
    username: Optional[str] = Field(default=None, description="用户名")
    password: Optional[str] = Field(default=None, description="密码")


class SourceResponse(SourceBase):
    """数据源响应模型"""
    id: str = Field(..., description="数据源ID")
    files: int = Field(default=0, description="文件总数")
    movies: int = Field(default=0, description="电影数量")
    series: int = Field(default=0, description="剧集数量")
    anime: int = Field(default=0, description="动漫数量")
    music: int = Field(default=0, description="音乐数量")
    unmatched: int = Field(default=0, description="未匹配数量")
    tint: str = Field(default="", description="卡片颜色")
    active: bool = Field(default=False, description="是否激活")


class SourceTypeOption(BaseModel):
    """数据源类型选项"""
    value: str = Field(..., description="类型值")
    label: str = Field(..., description="显示名称")
    badge: Optional[str] = Field(default=None, description="徽章")


class SourceTypeGroup(BaseModel):
    """数据源类型分组"""
    id: str = Field(..., description="分组ID")
    label: str = Field(..., description="分组名称")
    options: List[SourceTypeOption] = Field(default_factory=list, description="选项列表")


class SourceTypesResponse(BaseModel):
    """数据源类型列表响应"""
    groups: List[SourceTypeGroup] = Field(default_factory=list, description="类型分组")
    tints: List[str] = Field(default_factory=list, description="可选颜色列表")


class VerifyRequest(BaseModel):
    """验证连接请求模型"""
    type: str = Field(..., description="数据源类型")
    path: str = Field(..., description="数据源路径")
    username: Optional[str] = Field(default="", description="用户名")
    password: Optional[str] = Field(default="", description="密码")


class VerifyResponse(BaseModel):
    """验证连接响应模型"""
    valid: bool = Field(..., description="是否有效")
    files: Optional[int] = Field(default=None, description="文件数量")
    storages: Optional[List[str]] = Field(default=None, description="存储列表")
