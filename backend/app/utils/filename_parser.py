import os
import re
from typing import List, Dict, Any


def parse_video_filename(file_path: str) -> Dict[str, Any]:
    """
    从文件名解析影视信息
    
    Args:
        file_path: 文件路径
    
    Returns:
        解析后的信息，包含 title, year, season, episode, resolution, codec 等
    """
    result = {
        "title": "",
        "year": None,
        "season": None,
        "episode": None,
        "resolution": "",
        "codec": "",
        "is_series": False,
        "category": "movie",
        "file_path": file_path,
        "media_type": "video",
        "franchise": "",
        "sort_bucket": "",
        "sort_title": "",
        "release_group": "",
        "subtitle_info": "",
        "audio_info": "",
        "year_hint": None,
    }
    
    filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    # 提取年份
    year_match = re.search(r"[(（](\d{4})[)）]", name_without_ext)
    if year_match:
        result["year"] = int(year_match.group(1))
        result["year_hint"] = int(year_match.group(1))
    
    # 提取季数和集数
    season_episode_match = re.search(r"(?:第)?(\d+)[季季Ss][._ -]*(?:第)?(\d+)[集Ee]?", name_without_ext, re.IGNORECASE)
    if season_episode_match:
        result["season"] = int(season_episode_match.group(1))
        result["episode"] = int(season_episode_match.group(2)) if season_episode_match.group(2) else None
        result["is_series"] = True
        result["category"] = "series"
    
    # 提取分辨率
    resolution_match = re.search(r"(4K|2160p|1080p|720p|480p)", name_without_ext, re.IGNORECASE)
    if resolution_match:
        result["resolution"] = resolution_match.group(1).upper()
    
    # 提取编码
    codec_match = re.search(r"(H264|H.264|H265|H.265|HEVC|AVC|VP9)", name_without_ext, re.IGNORECASE)
    if codec_match:
        result["codec"] = codec_match.group(1).upper()
    
    # 提取标题（去除特殊字符和信息）
    clean_title = re.sub(r"[(（]\d{4}[)）]", "", name_without_ext)
    clean_title = re.sub(r"(?:第)?\d+[季季Ss][._ -]*\d*[集Ee]?", "", clean_title, flags=re.IGNORECASE)
    clean_title = re.sub(r"(4K|2160p|1080p|720p|480p)", "", clean_title, flags=re.IGNORECASE)
    clean_title = re.sub(r"(H264|H.264|H265|H.265|HEVC|AVC|VP9)", "", clean_title, flags=re.IGNORECASE)
    clean_title = re.sub(r"[\._\-[\](){}]", " ", clean_title)
    clean_title = re.sub(r"\s+", " ", clean_title).strip()
    
    result["title"] = clean_title
    result["sort_title"] = clean_title.lower()
    
    # 根据路径判断分类
    path_lower = file_path.lower()
    if any(keyword in path_lower for keyword in ["动漫", "动画", "anime", "cartoon"]):
        result["category"] = "anime"
        result["is_series"] = True
    elif any(keyword in path_lower for keyword in ["电视剧", "剧集", "series", "season"]):
        result["category"] = "series"
        result["is_series"] = True
    
    # 提取发布组
    group_match = re.search(r"-([A-Za-z0-9]+)$", name_without_ext)
    if group_match:
        result["release_group"] = group_match.group(1)
    
    return result


def merge_series_videos(video_files: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    将视频文件合并为影视条目
    
    Args:
        video_files: 视频文件列表
    
    Returns:
        合并后的影视列表
    """
    movies = {}
    
    for video in video_files:
        parsed = parse_video_filename(video["file_path"])
        title_key = parsed["title"]
        
        if title_key not in movies:
            movies[title_key] = {
                "title": parsed["title"],
                "year": parsed["year"],
                "category": parsed["category"],
                "is_series": parsed["is_series"],
                "resolution": parsed["resolution"],
                "codec": parsed["codec"],
                "remote_provider": video["remote_provider"],
                "source_label": video["source_label"],
                "episodes": [],
                "episode_files": [],
                "cover_path": None,
                "intro": "",
                "actors": [],
                "director": "",
                "path": video["file_path"],
                "media_type": parsed["media_type"],
                "franchise": parsed["franchise"],
                "sort_bucket": parsed["sort_bucket"],
                "sort_title": parsed["sort_title"],
                "release_group": parsed["release_group"],
                "subtitle_info": parsed["subtitle_info"],
                "audio_info": parsed["audio_info"],
                "year_hint": parsed["year_hint"],
            }
        
        if parsed["is_series"] and parsed["episode"]:
            movies[title_key]["episodes"].append({
                "episode": parsed["episode"],
                "season": parsed["season"] or 1,
                "file_path": video["file_path"]
            })
            movies[title_key]["episode_files"].append(video["file_path"])
        else:
            movies[title_key]["file_path"] = video["file_path"]
    
    # 对剧集排序
    for movie in movies.values():
        movie["episodes"].sort(key=lambda e: (e["season"], e["episode"]))
    
    return list(movies.values())