"""
OpenList 服务模块

此模块提供与 OpenList 服务交互的功能，包括：
1. OpenList API 客户端封装
2. 文件系统操作
3. 媒体文件搜索和管理
"""

import requests
import urllib3
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OpenListService:
    """
    OpenList 服务客户端
    
    提供与 OpenList API 交互的方法。
    使用 requests.Session 保持会话状态。
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:5244"):
        """
        初始化 OpenList 服务客户端
        
        Args:
            base_url: OpenList 服务的基础 URL
        """
        self.base_url = base_url.rstrip('/')
        self.username = "admin"
        self.password = "3BnQBIOR"
        self.token = None
        # 创建 session 对象保持会话状态
        self.session = requests.Session()
    
    def login(self, username: str = None, password: str = None) -> bool:
        """
        登录 OpenList 服务
        
        Args:
            username: 用户名，默认为 admin
            password: 密码，默认为初始密码
        
        Returns:
            bool: 登录是否成功
        """
        try:
            user = username or self.username
            pwd = password or self.password
            
            print(f"[DEBUG] Attempting login with username: {user}")
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": user, "password": pwd}
            )
            
            print(f"[DEBUG] Login response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    self.token = data.get("data", {}).get("token")
                    print(f"[DEBUG] Login successful, token: {self.token[:20]}...")
                    return True
            return False
        except Exception as e:
            print(f"[DEBUG] Login error: {e}")
            return False
    
    def ensure_login(self) -> bool:
        """
        确保已登录，如果未登录则自动登录
        
        Returns:
            bool: 是否登录成功
        """
        if self.token:
            return True
        return self.login()
    
    def get_file_list(self, path: str = "/", page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """
        获取文件列表
        
        Args:
            path: 目录路径
            page: 页码
            per_page: 每页数量
        
        Returns:
            Dict: 文件列表数据
        """
        self.ensure_login()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        print(f"[DEBUG] Fetching file list with token: {self.token[:20]}...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/fs/list",
                params={"path": path, "page": page, "per_page": per_page},
                headers=headers
            )
            print(f"[DEBUG] File list response: {response.text}")
            return response.json()
        except Exception as e:
            print(f"[DEBUG] File list error: {e}")
            return {"code": -1, "message": str(e), "data": None}
    
    def get_file_info(self, path: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            path: 文件路径
        
        Returns:
            Dict: 文件信息
        """
        self.ensure_login()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = self.session.get(
                f"{self.base_url}/api/fs/get",
                params={"path": path},
                headers=headers
            )
            return response.json()
        except Exception as e:
            return {"code": -1, "message": str(e), "data": None}
    
    def search_files(self, keyword: str, parent_path: str = "/") -> Dict[str, Any]:
        """
        搜索文件
        
        Args:
            keyword: 搜索关键词
            parent_path: 父目录路径
        
        Returns:
            Dict: 搜索结果
        """
        self.ensure_login()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = self.session.get(
                f"{self.base_url}/api/fs/search",
                params={"keyword": keyword, "parent": parent_path},
                headers=headers
            )
            return response.json()
        except Exception as e:
            return {"code": -1, "message": str(e), "data": None}
    
    def get_download_link(self, path: str) -> Optional[str]:
        """
        获取下载链接
        
        Args:
            path: 文件路径
        
        Returns:
            Optional[str]: 下载链接，如果获取失败返回 None
        """
        self.ensure_login()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = self.session.get(
                f"{self.base_url}/api/fs/get",
                params={"path": path},
                headers=headers
            )
            data = response.json()
            if data.get("code") == 200:
                file_info = data.get("data", {})
                return file_info.get("url")
            return None
        except Exception:
            return None
    
    def list_storages(self) -> Dict[str, Any]:
        """
        获取存储列表
        
        Returns:
            Dict: 存储列表数据
        """
        self.ensure_login()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = self.session.get(f"{self.base_url}/api/admin/storage/list", headers=headers)
            return response.json()
        except Exception as e:
            return {"code": -1, "message": str(e), "data": None}
    
    def proxy_request(self, method: str, path: str, **kwargs) -> requests.Response:
        """
        代理请求到 OpenList
        
        Args:
            method: HTTP 方法
            path: 请求路径
            **kwargs: 其他请求参数
        
        Returns:
            requests.Response: 响应对象
        """
        self.ensure_login()
        
        url = urljoin(self.base_url, path)
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.token}'
        
        return self.session.request(method, url, headers=headers, **kwargs)


# 全局 OpenList 服务实例
openlist_service = OpenListService()
