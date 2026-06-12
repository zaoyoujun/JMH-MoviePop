"""
统一响应格式模块

提供标准的 API 响应格式封装，确保所有接口返回格式一致。
"""

from typing import Any, Optional, TypeVar, Generic
from pydantic import BaseModel, Field

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """
    统一响应格式模型
    
    所有 API 接口都应返回此格式的数据。
    
    Attributes:
        code: 状态码，0表示成功，其他表示失败
        message: 响应消息
        data: 响应数据，可以是任意类型
    """
    code: int = Field(default=0, description="状态码，0表示成功")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")


class ErrorResponse(BaseModel):
    """错误响应格式"""
    code: int = Field(default=-1, description="错误码")
    message: str = Field(default="error", description="错误信息")
    data: Optional[Any] = Field(default=None, description="错误详情")


def success(data: Any = None, message: str = "success") -> dict:
    """
    成功响应快捷方法
    
    Args:
        data: 响应数据
        message: 成功消息
    
    Returns:
        dict: 标准成功响应格式
    """
    return {
        "code": 0,
        "message": message,
        "data": data
    }


def error(code: int = -1, message: str = "error", data: Any = None) -> dict:
    """
    错误响应快捷方法
    
    Args:
        code: 错误码
        message: 错误消息
        data: 错误详情
    
    Returns:
        dict: 标准错误响应格式
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }
