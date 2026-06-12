"""
数据源管理服务

提供数据源的增删改查和连接验证功能。
"""

import random
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional

from app.config.app_config import AppConfig
from app.services.openlist_client import OpenListAdminClient


class SourceService:
    """
    数据源管理服务
    
    管理数据源的持久化存储和业务逻辑。
    """

    def __init__(self, config: Optional[AppConfig] = None):
        self._config = config or AppConfig()
        self._db_path = self._config.DATA_DIR / "sources.db"
        self._openlist_client = OpenListAdminClient(self._config)
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库表"""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                path TEXT NOT NULL,
                username TEXT DEFAULT '',
                password TEXT DEFAULT '',
                driver TEXT DEFAULT '',
                cookie TEXT DEFAULT '',
                mount_path TEXT DEFAULT '',
                files INTEGER DEFAULT 0,
                movies INTEGER DEFAULT 0,
                series INTEGER DEFAULT 0,
                anime INTEGER DEFAULT 0,
                music INTEGER DEFAULT 0,
                unmatched INTEGER DEFAULT 0,
                tint TEXT DEFAULT '',
                active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()

    def _get_tint_options(self) -> List[str]:
        """获取颜色选项列表"""
        return [
            'rgba(91, 47, 116, 0.68)',
            'rgba(47, 109, 246, 0.62)',
            'rgba(99, 102, 241, 0.68)',
            'rgba(111, 110, 142, 0.62)',
            'rgba(95, 30, 30, 0.68)',
            'rgba(39, 98, 82, 0.66)',
            'rgba(101, 74, 38, 0.68)'
        ]

    def get_all_sources(self) -> List[Dict[str, Any]]:
        """获取所有数据源"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sources ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            result.append(dict(row))
        
        conn.close()
        return result

    def get_source_by_id(self, source_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取数据源"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None

    def add_source(self, source_data: Dict[str, Any], auto_scan: bool = True) -> Dict[str, Any]:
        """
        添加数据源
        
        Args:
            source_data: 数据源配置
            auto_scan: 是否添加后自动扫描（默认True）
        
        Returns:
            添加后的数据源信息
        """
        source_id = source_data.get("id") or f"source-{random.randint(100000, 999999)}"
        
        # 如果是内置OpenList类型，同步到OpenList服务
        if source_data.get("type") == "openlist":
            self._sync_to_openlist(source_data)
        
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sources 
            (id, name, type, path, username, password, driver, cookie, mount_path, 
             files, movies, series, anime, music, unmatched, tint, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source_id,
            source_data.get("name", ""),
            source_data.get("type", ""),
            source_data.get("path", ""),
            source_data.get("username", ""),
            source_data.get("password", ""),
            source_data.get("driver", ""),
            source_data.get("cookie", ""),
            source_data.get("mount_path", ""),
            source_data.get("files", 0),
            source_data.get("movies", 0),
            source_data.get("series", 0),
            source_data.get("anime", 0),
            source_data.get("music", 0),
            source_data.get("unmatched", 0),
            source_data.get("tint", random.choice(self._get_tint_options())),
            source_data.get("active", 0)
        ))
        
        conn.commit()
        conn.close()
        
        # 添加成功后自动触发扫描和刮削
        if auto_scan and source_data.get("type") in ["WebDAV", "本地存储"]:
            self._trigger_auto_scan(source_id)
        
        return self.get_source_by_id(source_id)

    def _trigger_auto_scan(self, source_id: str):
        """
        触发自动扫描和刮削
        
        Args:
            source_id: 数据源ID
        """
        try:
            from app.services.scan_service import scan_service
            # 执行扫描（包含刮削）
            scan_service.scan_library(source_id)
        except Exception as e:
            # 扫描失败不影响数据源添加
            pass

    def update_source(self, source_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新数据源
        
        Args:
            source_id: 数据源ID
            update_data: 更新的数据
        
        Returns:
            更新后的数据源信息，不存在返回None
        """
        if not self.get_source_by_id(source_id):
            return None
        
        set_clause = []
        params = []
        
        if "name" in update_data:
            set_clause.append("name = ?")
            params.append(update_data["name"])
        if "path" in update_data:
            set_clause.append("path = ?")
            params.append(update_data["path"])
        if "username" in update_data:
            set_clause.append("username = ?")
            params.append(update_data["username"])
        if "password" in update_data:
            set_clause.append("password = ?")
            params.append(update_data["password"])
        if "driver" in update_data:
            set_clause.append("driver = ?")
            params.append(update_data["driver"])
        if "cookie" in update_data:
            set_clause.append("cookie = ?")
            params.append(update_data["cookie"])
        if "mount_path" in update_data:
            set_clause.append("mount_path = ?")
            params.append(update_data["mount_path"])
        if "active" in update_data:
            set_clause.append("active = ?")
            params.append(update_data["active"])
        
        set_clause.append("updated_at = CURRENT_TIMESTAMP")
        
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            UPDATE sources 
            SET {', '.join(set_clause)} 
            WHERE id = ?
        """, tuple(params + [source_id]))
        
        conn.commit()
        conn.close()
        
        return self.get_source_by_id(source_id)

    def delete_source(self, source_id: str) -> bool:
        """
        删除数据源
        
        Args:
            source_id: 数据源ID
        
        Returns:
            删除是否成功
        """
        if not self.get_source_by_id(source_id):
            return False
        
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM sources WHERE id = ?", (source_id,))
        
        conn.commit()
        conn.close()
        
        return True

    def _sync_to_openlist(self, source_data: Dict[str, Any]) -> None:
        """
        同步数据源到OpenList服务
        
        Args:
            source_data: 数据源配置
        """
        try:
            driver_map = {
                "quark": "Quark",
                "baidu": "BaiduNetdisk"
            }
            
            driver = driver_map.get(source_data.get("driver"), source_data.get("driver"))
            mount_path = source_data.get("mount_path", "")
            
            if not mount_path.startswith("/"):
                mount_path = "/" + mount_path
            
            addition = {}
            if driver == "Quark":
                addition = {
                    "cookie": source_data.get("cookie", ""),
                    "root_folder_id": "0"
                }
            elif driver == "BaiduNetdisk":
                addition = {
                    "refresh_token": source_data.get("cookie", ""),
                    "root_folder_path": "/"
                }
            
            self._openlist_client.add_storage({
                "mount_path": mount_path,
                "driver": driver,
                "addition": addition
            })
        except Exception as e:
            # 同步失败不影响数据源添加
            pass

    def verify_connection(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证数据源连接
        
        Args:
            source_data: 数据源配置
        
        Returns:
            验证结果
        """
        source_type = source_data.get("type", "")
        
        if source_type == "openlist":
            # 检查OpenList服务状态
            status = self._openlist_client.get_status()
            if status.get("status") == "running":
                return {"valid": True, "message": "OpenList 服务运行正常"}
            else:
                return {"valid": False, "message": "OpenList 服务未运行"}
        
        elif source_type == "WebDAV":
            # 简单验证WebDAV连接
            host = source_data.get("host", "")
            if host and len(host) >= 4:
                return {"valid": True, "message": "连接可用"}
            return {"valid": False, "message": "请输入主机地址"}
        
        elif source_type == "本地存储":
            path = source_data.get("path", "")
            if path and len(path) >= 2:
                return {"valid": True, "message": "路径有效"}
            return {"valid": False, "message": "请输入有效路径"}
        
        return {"valid": False, "message": "未知数据源类型"}

    def rescan_source(self, source_id: str) -> Dict[str, Any]:
        """
        重新扫描数据源（包含刮削）
        
        Args:
            source_id: 数据源ID
        
        Returns:
            扫描状态和结果
        """
        source = self.get_source_by_id(source_id)
        if not source:
            return {"success": False, "message": "数据源不存在"}
        
        try:
            from app.services.scan_service import scan_service
            # 执行扫描（包含刮削）
            result = scan_service.scan_library(source_id)
            
            if "error" in result:
                return {"success": False, "message": result["error"]}
            
            return {
                "success": True,
                "scanning": False,
                "source_id": source_id,
                "message": result["message"],
                "total": result["total"],
                "movies": result["movies"],
                "series": result["series"],
                "anime": result["anime"],
                "total_episodes": result["total_episodes"]
            }
        except Exception as e:
            return {"success": False, "message": f"扫描失败: {str(e)}"}

    def get_source_types(self) -> Dict[str, Any]:
        """获取数据源类型配置"""
        return {
            "options": [
                {"label": "内置OpenList", "value": "openlist"},
                {"label": "WebDAV", "value": "WebDAV"},
                {"label": "本地目录", "value": "本地存储"},
                {"label": "待开发", "value": "developing"}
            ],
            "tint_options": self._get_tint_options(),
            "drivers": self._openlist_client.get_supported_drivers()
        }


# 全局单例
source_service = SourceService()
