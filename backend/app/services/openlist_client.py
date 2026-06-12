"""
OpenList 客户端服务

提供与 OpenList 管理后台 API 交互的客户端功能。
"""

import json
import time
from typing import Any, List, Dict, Optional

import requests

from app.config.app_config import AppConfig


class OpenListAdminClient:
    """
    OpenList 管理后台 API 客户端
    
    提供与 OpenList 管理接口的交互能力，包括存储管理、文件浏览等功能。
    """

    def __init__(self, config: Optional[AppConfig] = None):
        self._config = config or AppConfig()
        self._base_url = f"http://127.0.0.1:{self._config.OPENLIST_PORT}"
        self._session = requests.Session()
        self._token: str = ""
        self._token_expires: float = 0

    def _login(self, password: str) -> str:
        """
        登录 OpenList 管理后台
        
        Args:
            password: 管理员密码
        
        Returns:
            登录成功返回 token
        
        Raises:
            RuntimeError: 登录失败时抛出
        """
        resp = self._session.post(
            f"{self._base_url}/api/auth/login",
            json={"username": "admin", "password": password},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 200:
            raise RuntimeError(f"OpenList 登录失败: {data.get('message', '未知错误')}")
        self._token = data["data"]["token"]
        self._token_expires = time.time() + 3600
        return self._token

    def _ensure_token(self, password: Optional[str] = None) -> None:
        """确保 token 有效，过期则重新登录"""
        pwd = password or self._config.OPENLIST_ADMIN_PASSWORD
        if not self._token or time.time() > self._token_expires - 60:
            self._login(pwd)

    def _auth_headers(self, password: Optional[str] = None) -> Dict[str, str]:
        """获取认证请求头"""
        self._ensure_token(password)
        return {"Authorization": self._token}

    def _check_response(self, resp: requests.Response) -> Dict[str, Any]:
        """检查响应是否成功"""
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 200:
            raise RuntimeError(f"OpenList API 错误: {data.get('message', '未知错误')}")
        return data

    def get_status(self) -> Dict[str, Any]:
        """获取 OpenList 服务状态"""
        try:
            resp = self._session.get(f"{self._base_url}/api/public/settings", timeout=5)
            resp.raise_for_status()
            return {"status": "running", "code": 200}
        except Exception as e:
            return {"status": "stopped", "code": -1, "error": str(e)}

    def list_storages(self, password: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取存储列表
        
        Args:
            password: 管理员密码（可选，默认使用配置中的密码）
        
        Returns:
            存储配置列表
        """
        resp = self._session.get(
            f"{self._base_url}/api/admin/storage/list",
            headers=self._auth_headers(password),
            timeout=10,
        )
        data = self._check_response(resp)
        items = data.get("data", {}).get("content", [])
        result = []
        for item in items or []:
            addition = item.get("addition", "{}")
            if isinstance(addition, str):
                try:
                    addition = json.loads(addition)
                except (json.JSONDecodeError, TypeError):
                    addition = {}
            result.append({
                "id": item.get("id"),
                "mount_path": item.get("mount_path", ""),
                "order": item.get("order", 0),
                "driver": item.get("driver", ""),
                "cache_expiration": item.get("cache_expiration", 30),
                "status": item.get("status", "work"),
                "addition": addition,
                "modified": item.get("modified", ""),
            })
        return result

    def add_storage(self, storage_config: Dict[str, Any], password: Optional[str] = None) -> Dict[str, Any]:
        """
        添加存储配置
        
        Args:
            storage_config: 存储配置字典
            password: 管理员密码（可选）
        
        Returns:
            添加结果
        """
        mount_path = storage_config.get("mount_path", "")
        existing_storages = self.list_storages(password)
        for storage in existing_storages:
            if storage.get("mount_path") == mount_path:
                storage_config["id"] = storage.get("id")
                return self.update_storage(storage_config, password)

        addition = storage_config.get("addition", {})
        if isinstance(addition, dict):
            addition = json.dumps(addition, ensure_ascii=False)
        
        payload = {
            "mount_path": mount_path,
            "order": storage_config.get("order", 0),
            "driver": storage_config.get("driver", ""),
            "cache_expiration": storage_config.get("cache_expiration", 30),
            "status": "work",
            "addition": addition,
        }
        
        resp = self._session.post(
            f"{self._base_url}/api/admin/storage/create",
            headers=self._auth_headers(password),
            json=payload,
            timeout=15,
        )
        return self._check_response(resp)

    def update_storage(self, storage_config: Dict[str, Any], password: Optional[str] = None) -> Dict[str, Any]:
        """
        更新存储配置
        
        Args:
            storage_config: 存储配置字典（必须包含 id）
            password: 管理员密码（可选）
        
        Returns:
            更新结果
        """
        addition = storage_config.get("addition", {})
        if isinstance(addition, dict):
            addition = json.dumps(addition, ensure_ascii=False)
        
        payload = {
            "id": storage_config.get("id"),
            "mount_path": storage_config.get("mount_path", ""),
            "order": storage_config.get("order", 0),
            "driver": storage_config.get("driver", ""),
            "cache_expiration": storage_config.get("cache_expiration", 30),
            "status": storage_config.get("status", "work"),
            "addition": addition,
        }
        
        resp = self._session.post(
            f"{self._base_url}/api/admin/storage/update",
            headers=self._auth_headers(password),
            json=payload,
            timeout=15,
        )
        return self._check_response(resp)

    def delete_storage(self, storage_id: int, password: Optional[str] = None) -> Dict[str, Any]:
        """
        删除存储配置
        
        Args:
            storage_id: 存储 ID
            password: 管理员密码（可选）
        
        Returns:
            删除结果
        """
        resp = self._session.post(
            f"{self._base_url}/api/admin/storage/delete",
            headers=self._auth_headers(password),
            json={"id": storage_id},
            timeout=10,
        )
        return self._check_response(resp)

    def enable_storage(self, storage_id: int, password: Optional[str] = None) -> Dict[str, Any]:
        """启用存储"""
        resp = self._session.post(
            f"{self._base_url}/api/admin/storage/enable",
            headers=self._auth_headers(password),
            json={"id": storage_id},
            timeout=10,
        )
        return self._check_response(resp)

    def disable_storage(self, storage_id: int, password: Optional[str] = None) -> Dict[str, Any]:
        """禁用存储"""
        resp = self._session.post(
            f"{self._base_url}/api/admin/storage/disable",
            headers=self._auth_headers(password),
            json={"id": storage_id},
            timeout=10,
        )
        return self._check_response(resp)

    @staticmethod
    def get_supported_drivers() -> List[Dict[str, Any]]:
        """获取支持的存储驱动列表"""
        return [
            {
                "driver": "Quark",
                "label": "夸克网盘",
                "fields": [
                    {"key": "cookie", "label": "Cookie", "type": "textarea", "required": True, 
                     "placeholder": "从浏览器 F12 → Network → Request Headers 复制", 
                     "help": "登录 drive.quark.cn 后复制 Cookie"},
                    {"key": "root_folder_id", "label": "根目录 ID", "placeholder": "默认为 0 表示根目录"},
                ],
            },
            {
                "driver": "BaiduNetdisk",
                "label": "百度网盘",
                "fields": [
                    {"key": "refresh_token", "label": "Refresh Token", "required": True},
                    {"key": "root_folder_path", "label": "根目录路径", "placeholder": "/"},
                ],
            },
            {
                "driver": "WebDav",
                "label": "WebDAV",
                "fields": [
                    {"key": "address", "label": "地址", "required": True, "placeholder": "http://example.com/dav"},
                    {"key": "username", "label": "用户名"},
                    {"key": "password", "label": "密码", "type": "password"},
                    {"key": "root_folder_path", "label": "根目录路径", "placeholder": "/"},
                ],
            },
        ]

    def list_files(
        self,
        path: str = "/",
        page: int = 1,
        per_page: int = 0,
        refresh: bool = False,
        password: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        列出目录文件
        
        Args:
            path: 目录路径
            page: 页码
            per_page: 每页数量（0表示全部）
            refresh: 是否刷新缓存
            password: 管理员密码（可选）
        
        Returns:
            文件列表
        """
        import urllib.parse
        encoded_path = urllib.parse.quote(path, safe='/')
        resp = self._session.post(
            f"{self._base_url}/api/fs/list",
            headers=self._auth_headers(password),
            json={"path": encoded_path, "password": "", "page": page, 
                  "per_page": per_page, "refresh": bool(refresh)},
            timeout=15,
        )
        return self._check_response(resp)
