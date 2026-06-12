"""
Mock 数据模块

提供接口测试用的模拟数据，包括：
1. 影视数据
2. 数据源（服务器）数据
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# ========== 影视数据 ==========

# Mock 影视数据
_mock_movies = [
    {
        "id": "movie-001",
        "title": "肖申克的救赎",
        "alias": ["The Shawshank Redemption"],
        "category": "movie",
        "year": 1994,
        "sourceType": "local",
        "sourceName": "本地媒体",
        "durationText": "142分钟",
        "coverUrl": "https://example.com/covers/shawshank.jpg",
        "backdropUrl": "https://example.com/backdrops/shawshank.jpg",
        "tags": ["剧情", "犯罪"],
        "score": 9.7,
        "description": "一场谋杀案使银行家安迪蒙冤入狱，他在狱中的好友瑞德帮他策划了一场越狱行动。",
        "isFavorite": True,
        "progress": {"currentEpisode": 0, "totalEpisodes": 1, "percent": 0}
    },
    {
        "id": "movie-002",
        "title": "泰坦尼克号",
        "alias": ["Titanic"],
        "category": "movie",
        "year": 1997,
        "sourceType": "webdav",
        "sourceName": "夸克",
        "durationText": "194分钟",
        "coverUrl": "https://example.com/covers/titanic.jpg",
        "backdropUrl": "https://example.com/backdrops/titanic.jpg",
        "tags": ["剧情", "爱情", "灾难"],
        "score": 9.4,
        "description": "1912年泰坦尼克号沉没时期的爱情故事。",
        "isFavorite": False,
        "progress": None
    },
    {
        "id": "series-001",
        "title": "绝命毒师",
        "alias": ["Breaking Bad"],
        "category": "series",
        "year": 2008,
        "sourceType": "openlist",
        "sourceName": "百度",
        "durationText": "共5季",
        "coverUrl": "https://example.com/covers/breakingbad.jpg",
        "backdropUrl": "https://example.com/backdrops/breakingbad.jpg",
        "tags": ["剧情", "犯罪", "悬疑"],
        "score": 9.5,
        "description": "一位高中化学老师得知自己身患绝症，利用自己的知识制造毒品，最终成为大毒枭的故事。",
        "isFavorite": True,
        "progress": {"currentEpisode": 10, "totalEpisodes": 62, "percent": 16}
    },
    {
        "id": "anime-001",
        "title": "进击的巨人",
        "alias": ["Attack on Titan"],
        "category": "anime",
        "year": 2013,
        "sourceType": "openlist",
        "sourceName": "115网盘",
        "durationText": "共4季",
        "coverUrl": "https://example.com/covers/aot.jpg",
        "backdropUrl": "https://example.com/backdrops/aot.jpg",
        "tags": ["动作", "动画", "奇幻"],
        "score": 9.2,
        "description": "人类与巨人的战争，讲述艾伦·耶格尔加入调查兵团的故事。",
        "isFavorite": True,
        "progress": {"currentEpisode": 45, "totalEpisodes": 87, "percent": 52}
    },
    {
        "id": "movie-003",
        "title": "盗梦空间",
        "alias": ["Inception"],
        "category": "movie",
        "year": 2010,
        "sourceType": "local",
        "sourceName": "本地媒体",
        "durationText": "148分钟",
        "coverUrl": "https://example.com/covers/inception.jpg",
        "backdropUrl": "https://example.com/backdrops/inception.jpg",
        "tags": ["科幻", "动作", "悬疑"],
        "score": 9.3,
        "description": "造梦师柯布和他的团队在梦境中执行任务，却陷入层层嵌套的梦境陷阱。",
        "isFavorite": False,
        "progress": None
    }
]


def get_mock_movies() -> List[Dict]:
    """获取所有 Mock 影视数据"""
    return [m.copy() for m in _mock_movies]


def get_mock_movie_by_id(movie_id: str) -> Optional[Dict]:
    """根据ID获取 Mock 影视数据"""
    for m in _mock_movies:
        if m["id"] == movie_id:
            return m.copy()
    return None


def get_mock_hero_items() -> List[Dict]:
    """获取首页轮播图数据"""
    heroes = []
    for m in _mock_movies[:4]:
        heroes.append({
            "id": m["id"],
            "title": m["title"],
            "category": m["category"],
            "year": m["year"],
            "sourceType": m["sourceType"],
            "sourceName": m["sourceName"],
            "durationText": m["durationText"],
            "backdropUrl": m["backdropUrl"],
            "tags": m["tags"]
        })
    return heroes


def get_mock_library_stats() -> Dict:
    """获取媒体库统计数据"""
    return {
        "total": 1689,
        "remote": 1245,
        "local": 444,
        "favorite": 89
    }


def get_mock_episodes(movie_id: str) -> List[Dict]:
    """获取剧集列表"""
    movie = get_mock_movie_by_id(movie_id)
    if not movie or movie["category"] != "series":
        return []
    
    # 生成模拟剧集
    episodes = []
    for i in range(1, 13):
        episodes.append({
            "id": f"{movie_id}-ep{i}",
            "title": f"第{i}集",
            "episodeNumber": i,
            "durationText": "45分钟",
            "playUrl": f"http://example.com/play/{movie_id}/ep{i}.mp4",
            "sourceType": movie["sourceType"]
        })
    return episodes


def get_mock_play_url(movie_id: str, episode_id: Optional[str] = None) -> Dict:
    """获取播放地址"""
    movie = get_mock_movie_by_id(movie_id)
    if not movie:
        return {"id": movie_id, "playUrl": "", "headers": {}, "sourceType": ""}
    
    if movie["category"] == "movie":
        play_url = f"http://example.com/play/{movie_id}/movie.mp4"
    else:
        ep_id = episode_id or f"{movie_id}-ep1"
        play_url = f"http://example.com/play/{movie_id}/{ep_id}.mp4"
    
    return {
        "id": movie_id,
        "episodeId": episode_id,
        "playUrl": play_url,
        "headers": {},
        "sourceType": movie["sourceType"]
    }


# ========== 数据源（服务器）数据 ==========

# 数据源类型分组
SOURCE_TYPE_GROUPS = [
    {
        "id": "server",
        "label": "服务器",
        "options": [
            {"value": "openlist", "label": "OpenList"},
            {"value": "WebDAV", "label": "WebDAV"},
            {"value": "FTP", "label": "FTP"}
        ]
    },
    {
        "id": "network",
        "label": "网络存储",
        "options": [
            {"value": "SMB", "label": "SMB"},
            {"value": "NFS", "label": "NFS"}
        ]
    },
    {
        "id": "cloud",
        "label": "云盘存储",
        "options": [
            {"value": "openlist", "label": "115网盘", "badge": "115"}
        ]
    },
    {
        "id": "local",
        "label": "本地存储",
        "options": [
            {"value": "本地存储", "label": "本地目录"}
        ]
    },
    {
        "id": "developing",
        "label": "开发中",
        "options": [
            {"value": "开发中", "label": "更多来源即将支持"}
        ]
    }
]

# 可选颜色列表
TINT_OPTIONS = [
    "rgba(111, 110, 142, 0.62)",
    "rgba(95, 30, 30, 0.68)",
    "rgba(45, 83, 102, 0.66)",
    "rgba(91, 47, 116, 0.68)",
    "rgba(39, 98, 82, 0.66)",
    "rgba(101, 74, 38, 0.68)"
]

# 内存中的数据源列表（Mock 数据）
_mock_sources: List[Dict[str, Any]] = [
    {
        "id": "webdav-kui",
        "name": "夸克",
        "type": "WebDAV",
        "files": 1497,
        "movies": 0,
        "series": 0,
        "anime": 0,
        "music": 0,
        "unmatched": 0,
        "path": "http://118.89.62.59:5050/动漫 (+3)",
        "username": "",
        "password": "",
        "tint": "rgba(111, 110, 142, 0.62)",
        "active": False
    },
    {
        "id": "local-media",
        "name": "本地媒体",
        "type": "本地存储",
        "files": 1497,
        "movies": 0,
        "series": 0,
        "anime": 0,
        "music": 0,
        "unmatched": 168,
        "path": "D:/Media/Library",
        "username": "",
        "password": "",
        "tint": "rgba(95, 30, 30, 0.68)",
        "active": True
    },
    {
        "id": "baidu-openlist",
        "name": "百度",
        "type": "内置openlist",
        "files": 2345,
        "movies": 0,
        "series": 0,
        "anime": 0,
        "music": 0,
        "unmatched": 245,
        "path": "OpenList / baidu",
        "username": "",
        "password": "",
        "tint": "rgba(45, 83, 102, 0.66)",
        "active": False
    },
    {
        "id": "115-openlist",
        "name": "115网盘",
        "type": "openlist",
        "files": 3689,
        "movies": 0,
        "series": 0,
        "anime": 0,
        "music": 0,
        "unmatched": 312,
        "path": "OpenList / 115",
        "username": "",
        "password": "",
        "tint": "rgba(91, 47, 116, 0.68)",
        "active": False
    }
]


def get_mock_sources() -> List[Dict[str, Any]]:
    """获取所有 Mock 数据源"""
    return _mock_sources.copy()


def get_mock_source_by_id(source_id: str) -> Dict[str, Any] | None:
    """根据ID获取 Mock 数据源"""
    for source in _mock_sources:
        if source["id"] == source_id:
            return source.copy()
    return None


def add_mock_source(source_data: Dict[str, Any]) -> Dict[str, Any]:
    """添加 Mock 数据源"""
    source_data["id"] = f"source-{uuid.uuid4().hex[:10]}"
    _mock_sources.insert(0, source_data)
    return source_data.copy()


def update_mock_source(source_id: str, update_data: Dict[str, Any]) -> Dict[str, Any] | None:
    """更新 Mock 数据源"""
    for i, source in enumerate(_mock_sources):
        if source["id"] == source_id:
            _mock_sources[i].update(update_data)
            return _mock_sources[i].copy()
    return None


def delete_mock_source(source_id: str) -> bool:
    """删除 Mock 数据源"""
    for i, source in enumerate(_mock_sources):
        if source["id"] == source_id:
            _mock_sources.pop(i)
            return True
    return False


def get_source_types() -> Dict[str, Any]:
    """获取数据源类型配置"""
    return {
        "groups": SOURCE_TYPE_GROUPS,
        "tints": TINT_OPTIONS
    }
