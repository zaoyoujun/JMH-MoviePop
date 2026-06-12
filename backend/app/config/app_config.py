"""
应用配置模块

提供全局配置管理，包括 OpenList 相关配置。
"""

import json
import os
from pathlib import Path


class AppConfig:
    """
    应用配置类
    
    管理所有应用配置项，支持从配置文件读取和保存。
    """
    
    def __init__(self):
        self._data_dir = self._get_data_dir()
        self._config_file = self._data_dir / "config.json"
        self._config = self._load_config()
    
    def _get_data_dir(self) -> Path:
        """获取数据目录路径"""
        base_dir = Path(__file__).parent.parent.parent
        data_dir = base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        default_config = {
            "OPENLIST_ENABLED": True,
            "OPENLIST_PORT": 5244,
            "OPENLIST_AUTO_START": True,
            "OPENLIST_ADMIN_PASSWORD": "admin",
            "OPENLIST_BINARY_VERSION": "",
            "OPENLIST_SOURCE_MODE": "builtin",
            "USE_PROXY": False,
            "PROXY_URL": "",
            "SCAN_MAX_DEPTH": 2,
            "REMOTE_PROFILES": {},
        }
        
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except Exception:
                pass
        
        return default_config
    
    def normalize_remote_provider(self, provider: str) -> str:
        """标准化远程提供者类型"""
        value = str(provider or "").strip().lower()
        if value in {"webdav", "openlist"}:
            return value
        return "webdav"
    
    def normalize_openlist_source_mode(self, mode: str) -> str:
        """标准化OpenList源模式"""
        value = str(mode or "").strip().lower()
        if value in {"builtin", "external"}:
            return value
        return "builtin"
    
    def get_remote_profiles(self) -> dict:
        """获取远程配置文件"""
        return self._config.get("REMOTE_PROFILES", {})
    
    def save_remote_profiles(self, profiles: dict) -> None:
        """保存远程配置文件"""
        self._config["REMOTE_PROFILES"] = profiles
        self.save_config()
    
    def save_config(self) -> None:
        """保存配置到文件"""
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    @property
    def DATA_DIR(self) -> Path:
        return self._data_dir
    
    @property
    def OPENLIST_ENABLED(self) -> bool:
        return self._config.get("OPENLIST_ENABLED", True)
    
    @OPENLIST_ENABLED.setter
    def OPENLIST_ENABLED(self, value: bool):
        self._config["OPENLIST_ENABLED"] = value
    
    @property
    def OPENLIST_PORT(self) -> int:
        return self._config.get("OPENLIST_PORT", 5244)
    
    @OPENLIST_PORT.setter
    def OPENLIST_PORT(self, value: int):
        self._config["OPENLIST_PORT"] = value
    
    @property
    def OPENLIST_AUTO_START(self) -> bool:
        return self._config.get("OPENLIST_AUTO_START", True)
    
    @OPENLIST_AUTO_START.setter
    def OPENLIST_AUTO_START(self, value: bool):
        self._config["OPENLIST_AUTO_START"] = value
    
    @property
    def OPENLIST_ADMIN_PASSWORD(self) -> str:
        return self._config.get("OPENLIST_ADMIN_PASSWORD", "admin")
    
    @OPENLIST_ADMIN_PASSWORD.setter
    def OPENLIST_ADMIN_PASSWORD(self, value: str):
        self._config["OPENLIST_ADMIN_PASSWORD"] = value
    
    @property
    def OPENLIST_BINARY_VERSION(self) -> str:
        return self._config.get("OPENLIST_BINARY_VERSION", "")
    
    @OPENLIST_BINARY_VERSION.setter
    def OPENLIST_BINARY_VERSION(self, value: str):
        self._config["OPENLIST_BINARY_VERSION"] = value
    
    @property
    def USE_PROXY(self) -> bool:
        return self._config.get("USE_PROXY", False)
    
    @USE_PROXY.setter
    def USE_PROXY(self, value: bool):
        self._config["USE_PROXY"] = value
    
    @property
    def PROXY_URL(self) -> str:
        return self._config.get("PROXY_URL", "")
    
    @PROXY_URL.setter
    def PROXY_URL(self, value: str):
        self._config["PROXY_URL"] = value
    
    @property
    def SCAN_MAX_DEPTH(self) -> int:
        return self._config.get("SCAN_MAX_DEPTH", 2)
    
    @SCAN_MAX_DEPTH.setter
    def SCAN_MAX_DEPTH(self, value: int):
        self._config["SCAN_MAX_DEPTH"] = value
    
    @property
    def OPENLIST_SOURCE_MODE(self) -> str:
        return self._config.get("OPENLIST_SOURCE_MODE", "builtin")
    
    @OPENLIST_SOURCE_MODE.setter
    def OPENLIST_SOURCE_MODE(self, value: str):
        self._config["OPENLIST_SOURCE_MODE"] = value
    
    @property
    def VIDEO_FORMATS(self) -> list:
        """支持的视频格式列表"""
        return [".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm", ".m4v"]
