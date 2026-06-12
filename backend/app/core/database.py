"""
数据库操作模块 - SQLite数据库管理

此模块提供SQLite数据库的初始化和操作方法，包括：
1. 数据库连接管理
2. 表创建和迁移
3. 影视数据的CRUD操作
4. 剧集数据的CRUD操作
"""

import os
import sqlite3
from typing import List, Dict, Any, Optional

from app.config.app_config import AppConfig


class DatabaseManager:
    """数据库管理器类 - 提供SQLite数据库操作接口"""

    def __init__(self):
        self.config = AppConfig()
        self.db_path = os.path.join(str(self.config.DATA_DIR), "movies.db")
        self._init_database()

    def _init_database(self):
        """初始化数据库，创建必要的表"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建影视表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    year INTEGER,
                    category TEXT DEFAULT 'movie',
                    is_series INTEGER DEFAULT 0,
                    resolution TEXT DEFAULT '',
                    codec TEXT DEFAULT '',
                    remote_provider TEXT DEFAULT '',
                    source_label TEXT DEFAULT '',
                    cover_path TEXT,
                    intro TEXT DEFAULT '',
                    actors TEXT DEFAULT '',
                    director TEXT DEFAULT '',
                    file_path TEXT,
                    created_at INTEGER
                )
            ''')
            
            # 创建剧集表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    movie_id INTEGER NOT NULL,
                    season INTEGER DEFAULT 1,
                    episode INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_category ON movies(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_episodes_movie_id ON episodes(movie_id)')
            
            conn.commit()

    def _execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """执行SQL查询"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def _fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """执行查询并返回所有结果"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def _fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """执行查询并返回单个结果"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    # ==================== 影视操作 ====================
    def add_movie(self, movie_data: Dict[str, Any]) -> int:
        """
        添加影视记录
        
        Args:
            movie_data: 影视数据字典
        
        Returns:
            新插入记录的ID
        """
        query = '''
            INSERT INTO movies (
                title, year, category, is_series, resolution, codec,
                remote_provider, source_label, cover_path, intro,
                actors, director, file_path, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            movie_data.get("title", ""),
            movie_data.get("year"),
            movie_data.get("category", "movie"),
            1 if movie_data.get("is_series", False) else 0,
            movie_data.get("resolution", ""),
            movie_data.get("codec", ""),
            movie_data.get("remote_provider", ""),
            movie_data.get("source_label", ""),
            movie_data.get("cover_path"),
            movie_data.get("intro", ""),
            movie_data.get("actors", ""),
            movie_data.get("director", ""),
            movie_data.get("file_path"),
            movie_data.get("created_at")
        )
        
        cursor = self._execute_query(query, params)
        return cursor.lastrowid

    def update_movie(self, movie_id: int, movie_data: Dict[str, Any]) -> bool:
        """
        更新影视记录
        
        Args:
            movie_id: 影视ID
            movie_data: 要更新的影视数据
        
        Returns:
            是否更新成功
        """
        # 构建动态更新语句
        update_fields = []
        params = []
        
        if "title" in movie_data:
            update_fields.append("title = ?")
            params.append(movie_data["title"])
        if "year" in movie_data:
            update_fields.append("year = ?")
            params.append(movie_data["year"])
        if "category" in movie_data:
            update_fields.append("category = ?")
            params.append(movie_data["category"])
        if "cover_path" in movie_data:
            update_fields.append("cover_path = ?")
            params.append(movie_data["cover_path"])
        if "intro" in movie_data:
            update_fields.append("intro = ?")
            params.append(movie_data["intro"])
        if "actors" in movie_data:
            update_fields.append("actors = ?")
            params.append(movie_data["actors"])
        if "director" in movie_data:
            update_fields.append("director = ?")
            params.append(movie_data["director"])
        
        if not update_fields:
            return False
        
        params.append(movie_id)
        query = f"UPDATE movies SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor = self._execute_query(query, tuple(params))
        return cursor.rowcount > 0

    def get_movie(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个影视记录
        
        Args:
            movie_id: 影视ID
        
        Returns:
            影视数据字典，不存在返回None
        """
        query = "SELECT * FROM movies WHERE id = ?"
        return self._fetch_one(query, (movie_id,))

    def get_movie_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        根据标题获取影视记录
        
        Args:
            title: 影视标题
        
        Returns:
            影视数据字典，不存在返回None
        """
        query = "SELECT * FROM movies WHERE title = ?"
        return self._fetch_one(query, (title,))

    def get_all_movies(self, category: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取所有影视记录
        
        Args:
            category: 分类筛选
            keyword: 关键词搜索
        
        Returns:
            影视数据列表
        """
        query = "SELECT * FROM movies WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if keyword:
            query += " AND (title LIKE ? OR intro LIKE ?)"
            params.append(f"%{keyword}%")
            params.append(f"%{keyword}%")
        
        query += " ORDER BY title ASC"
        return self._fetch_all(query, tuple(params))

    def delete_movie(self, movie_id: int) -> bool:
        """
        删除影视记录（级联删除剧集）
        
        Args:
            movie_id: 影视ID
        
        Returns:
            是否删除成功
        """
        query = "DELETE FROM movies WHERE id = ?"
        cursor = self._execute_query(query, (movie_id,))
        return cursor.rowcount > 0

    def delete_all_movies(self):
        """删除所有影视记录"""
        self._execute_query("DELETE FROM episodes")
        self._execute_query("DELETE FROM movies")

    def get_movie_count(self) -> int:
        """获取影视总数"""
        query = "SELECT COUNT(*) as count FROM movies"
        result = self._fetch_one(query)
        return result["count"] if result else 0

    def get_movie_count_by_category(self, category: str) -> int:
        """按分类获取影视数量"""
        query = "SELECT COUNT(*) as count FROM movies WHERE category = ?"
        result = self._fetch_one(query, (category,))
        return result["count"] if result else 0

    # ==================== 剧集操作 ====================
    def add_episode(self, episode_data: Dict[str, Any]) -> int:
        """
        添加剧集记录
        
        Args:
            episode_data: 剧集数据字典
        
        Returns:
            新插入记录的ID
        """
        query = '''
            INSERT INTO episodes (movie_id, season, episode, file_path)
            VALUES (?, ?, ?, ?)
        '''
        params = (
            episode_data["movie_id"],
            episode_data.get("season", 1),
            episode_data["episode"],
            episode_data["file_path"]
        )
        
        cursor = self._execute_query(query, params)
        return cursor.lastrowid

    def add_episodes(self, movie_id: int, episodes: List[Dict[str, Any]]):
        """
        批量添加剧集记录
        
        Args:
            movie_id: 影视ID
            episodes: 剧集列表
        """
        query = '''
            INSERT INTO episodes (movie_id, season, episode, file_path)
            VALUES (?, ?, ?, ?)
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for episode in episodes:
                cursor.execute(query, (
                    movie_id,
                    episode.get("season", 1),
                    episode["episode"],
                    episode["file_path"]
                ))
            conn.commit()

    def get_episodes_by_movie_id(self, movie_id: int) -> List[Dict[str, Any]]:
        """
        获取指定影视的所有剧集
        
        Args:
            movie_id: 影视ID
        
        Returns:
            剧集列表
        """
        query = "SELECT * FROM episodes WHERE movie_id = ? ORDER BY season ASC, episode ASC"
        return self._fetch_all(query, (movie_id,))

    def delete_episodes_by_movie_id(self, movie_id: int):
        """
        删除指定影视的所有剧集
        
        Args:
            movie_id: 影视ID
        """
        query = "DELETE FROM episodes WHERE movie_id = ?"
        self._execute_query(query, (movie_id,))

    def get_total_episodes(self) -> int:
        """获取总集数"""
        query = "SELECT COUNT(*) as count FROM episodes"
        result = self._fetch_one(query)
        return result["count"] if result else 0

    # ==================== 统计操作 ====================
    def get_library_stats(self) -> Dict[str, int]:
        """获取媒体库统计信息"""
        return {
            "total": self.get_movie_count(),
            "movies": self.get_movie_count_by_category("movie"),
            "series": self.get_movie_count_by_category("series"),
            "anime": self.get_movie_count_by_category("anime"),
            "total_episodes": self.get_total_episodes()
        }

    # ==================== 分页查询 ====================
    def get_movies_with_pagination(self, page: int, page_size: int, 
                                   category: Optional[str] = None, 
                                   keyword: Optional[str] = None) -> Dict[str, Any]:
        """
        分页获取影视列表
        
        Args:
            page: 页码
            page_size: 每页数量
            category: 分类筛选
            keyword: 关键词搜索
        
        Returns:
            包含列表和分页信息的字典
        """
        # 构建查询条件
        where_clause = "WHERE 1=1"
        params = []
        
        if category:
            where_clause += " AND category = ?"
            params.append(category)
        
        if keyword:
            where_clause += " AND (title LIKE ? OR intro LIKE ?)"
            params.append(f"%{keyword}%")
            params.append(f"%{keyword}%")
        
        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM movies {where_clause}"
        count_result = self._fetch_one(count_query, tuple(params))
        total = count_result["total"] if count_result else 0
        
        # 获取分页数据
        offset = (page - 1) * page_size
        data_query = f"""
            SELECT * FROM movies {where_clause}
            ORDER BY title ASC
            LIMIT ? OFFSET ?
        """
        data_params = list(params) + [page_size, offset]
        movies = self._fetch_all(data_query, tuple(data_params))
        
        # 获取每个影视的剧集
        for movie in movies:
            movie["episodes"] = self.get_episodes_by_movie_id(movie["id"])
        
        return {
            "list": movies,
            "pagination": {
                "page": page,
                "pageSize": page_size,
                "total": total
            }
        }


# 创建全局数据库管理器实例
db_manager = DatabaseManager()
