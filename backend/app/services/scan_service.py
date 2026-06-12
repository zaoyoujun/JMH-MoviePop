"""
扫描服务模块 - 影视刮削与媒体库管理

此模块提供以下核心功能：
1. 远程文件扫描（WebDAV）
2. 本地文件扫描
3. 文件名解析（提取影视信息）
4. 封面刮削（从多个数据源获取封面）
5. 媒体库管理（使用SQLite存储）

支持的数据源：
- WebDAV 远程存储
- 本地文件系统
- OpenList 内置服务
"""

import hashlib
import os
import re
import time
from typing import List, Dict, Any, Optional
from urllib.parse import quote, unquote, urlparse

import requests
from bs4 import BeautifulSoup

from app.config.app_config import AppConfig
from app.core.database import db_manager
from app.core.cover_scraper import CoverScraper

# ==================== 全局配置 ====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive"
}

ANIBK_BASE = "https://www.anibk.com"
ANIBK_SEARCH = f"{ANIBK_BASE}/list/---------?order=20&kw="
BANGUMI_API = "https://api.bgm.tv"
TMDB_BASE = "https://www.themoviedb.org"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"
DOUBAN_BASE = "https://movie.douban.com"

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm", ".m4v"}


# ==================== 翻译辅助函数 ====================
def is_chinese(text):
    """判断文本是否主要为中文（避免重复翻译）"""
    if not text:
        return True
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    # 中文字符占比 > 30% 则认为是中文
    return len(chinese_chars) / len(text) > 0.3


def translate_to_chinese(text):
    """自动翻译非中文文本为中文"""
    if not text or is_chinese(text):
        return text  # 空文本或已是中文直接返回
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source='auto', target='zh-CN').translate(text)
        return translated
    except Exception:
        return text  # 翻译失败时返回原文


def normalize_chinese_punctuation(text):
    if not text:
        return text
    text = text.replace("：", ":")
    text = text.replace("（", "(")
    text = text.replace("）", ")")
    text = text.replace("【", "[")
    text = text.replace("】", "]")
    text = text.replace("，", ",")
    text = text.replace("。", ".")
    text = text.replace("、", " ")
    return text


def clean_title_for_search(title):
    title = normalize_chinese_punctuation(title)
    season_num = None
    year = None
    season_match = re.search(r'第(\d+)季|Season\s*(\d+)|S(\d{1,2})', title, re.IGNORECASE)
    if season_match:
        season_num = next((g for g in season_match.groups() if g), None)
        if season_num:
            season_num = int(season_num)
    year_match = re.search(r'[(（](\d{4})[)）]', title)
    if year_match:
        year = year_match.group(1)
    clean_name = re.sub(r'第\d+季|Season\s*\d+|S\d{1,2}', '', title, flags=re.IGNORECASE)
    clean_name = re.sub(r'[(（]\d{4}[)）]', '', clean_name)
    clean_name = re.sub(r'[_\-\[\]().]', ' ', clean_name)
    clean_name = re.sub(r'\s+', ' ', clean_name).strip()
    return {
        "clean_name": clean_name,
        "season": season_num,
        "year": year,
        "original_title": title
    }


class ScanService:
    """扫描服务类 - 提供媒体库扫描和影视刮削功能"""

    def __init__(self):
        self.config = AppConfig()
        self.cache_dir = str(self.config.DATA_DIR)
        self.cover_dir = os.path.join(self.cache_dir, "covers")
        self.tmdb_api_base = getattr(self.config, "TMDB_API_BASE", "https://api.themoviedb.org/3")
        self.tmdb_image_base = getattr(self.config, "TMDB_IMAGE_BASE", TMDB_IMG_BASE)
        
        # 确保目录存在
        os.makedirs(self.cover_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # TMDB 限流控制
        self._tmdb_disabled_until = 0
        self._tmdb_failure_reason = ""
        
        # 初始化封面刮削器
        self.cover_scraper = CoverScraper()

    # ==================== TMDB 限流控制 ====================
    def _tmdb_is_temporarily_disabled(self):
        return time.time() < float(self._tmdb_disabled_until or 0)

    def _disable_tmdb_temporarily(self, reason, cooldown=180):
        self._tmdb_disabled_until = time.time() + cooldown
        self._tmdb_failure_reason = str(reason or "")

    def _reset_tmdb_availability(self):
        self._tmdb_disabled_until = 0
        self._tmdb_failure_reason = ""

    # ==================== WebDAV 扫描功能 ====================
    def scan_webdav(self, host: str, port: str, protocol: str, 
                    username: str, password: str, paths: List[str]) -> List[Dict[str, str]]:
        """
        扫描WebDAV服务器上的视频文件
        
        Args:
            host: 主机地址
            port: 端口
            protocol: 协议 (http/https)
            username: 用户名
            password: 密码
            paths: 要扫描的路径列表
        
        Returns:
            视频文件列表，每个文件包含 file_path, remote_provider, source_label
        """
        results = []
        base_url = f"{protocol}://{host}{':' + port if port else ''}"
        print(f"DEBUG: [WebDAV] 基础URL: {base_url}")
        print(f"DEBUG: [WebDAV] 是否使用认证: {bool(username and password)}")
        
        try:
            session = requests.Session()
            session.verify = False
            
            # 设置认证
            if username and password:
                session.auth = (username, password)
                print(f"DEBUG: [WebDAV] 使用用户名: {username}")
            
            for path in paths:
                print(f"DEBUG: [WebDAV] 扫描路径: {path}")
                files = self._webdav_list_files(session, base_url, path)
                print(f"DEBUG: [WebDAV] 路径 {path} 发现 {len(files)} 个文件")
                results.extend([
                    {
                        "file_path": file,
                        "remote_provider": "webdav",
                        "source_label": "WebDAV"
                    }
                    for file in files
                ])
        except Exception as e:
            print(f"ERROR: [WebDAV] 扫描失败: {e}")
        
        return results

    def _encode_path(self, path: str) -> str:
        """对路径进行URL编码，参考核心代码实现"""
        normalized = self._normalize_path(path)
        segments = [quote(segment) for segment in normalized.lstrip("/").split("/") if segment]
        return "/" + "/".join(segments) if segments else "/"

    def _webdav_list_files(self, session, base_url: str, path: str, depth: int = 5) -> List[str]:
        """递归列出WebDAV目录中的视频文件"""
        files = []
        normalized_path = self._normalize_path(path)
        encoded_path = self._encode_path(normalized_path)
        url = f"{base_url}{encoded_path}"
        print(f"DEBUG: [WebDAV] 访问路径: {url}")
        print(f"DEBUG: [WebDAV] 递归深度: {depth}")
        
        try:
            body = """<?xml version="1.0" encoding="utf-8" ?>
<d:propfind xmlns:d="DAV:">
    <d:prop><d:resourcetype /></d:prop>
</d:propfind>"""
            
            # 使用深度为1，服务器可能不支持更大的深度
            response = session.request(
                "PROPFIND",
                url,
                headers={"Depth": "1", "Content-Type": "application/xml; charset=utf-8"},
                data=body,
                timeout=20
            )
            response.raise_for_status()
            print(f"DEBUG: [WebDAV] 请求成功，状态码: {response.status_code}")
            
            entries = self._parse_webdav_response(response.text, base_url)
            print(f"DEBUG: [WebDAV] 解析到 {len(entries)} 个条目")
            
            for entry in entries:
                print(f"DEBUG: [WebDAV] 条目: {entry['name']} | 路径: {entry['path']} | 是否目录: {entry['is_dir']}")
                if entry["is_dir"]:
                    if depth > 0:
                        print(f"DEBUG: [WebDAV] 递归扫描子目录: {entry['path']}")
                        sub_files = self._webdav_list_files(session, base_url, entry["path"], depth - 1)
                        print(f"DEBUG: [WebDAV] 子目录 {entry['path']} 发现 {len(sub_files)} 个文件")
                        files.extend(sub_files)
                else:
                    ext = os.path.splitext(entry["path"])[1].lower()
                    print(f"DEBUG: [WebDAV] 文件扩展名: {ext}")
                    if ext in VIDEO_EXTENSIONS:
                        files.append(entry["path"])
                        print(f"DEBUG: [WebDAV] 添加视频文件: {entry['path']}")
        except Exception as e:
            print(f"ERROR: [WebDAV] 扫描失败: {e}")
        
        # 去重：移除重复的文件路径
        unique_files = list(dict.fromkeys(files))
        if len(unique_files) != len(files):
            print(f"DEBUG: [WebDAV] 去重前: {len(files)} 个文件，去重后: {len(unique_files)} 个文件")
        
        print(f"DEBUG: [WebDAV] 路径 {path} 扫描完成，共发现 {len(unique_files)} 个视频文件")
        return unique_files

    def _normalize_path(self, path: str) -> str:
        """标准化路径，确保以/开头"""
        path = str(path or "/").strip()
        if not path.startswith("/"):
            path = "/" + path
        return path

    def _parse_webdav_response(self, response_text: str, base_url: str) -> List[Dict[str, Any]]:
        """解析WebDAV PROPFIND响应"""
        entries = []
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(response_text)
            ns = {"d": "DAV:"}
            
            # 获取基础路径（base_url 的路径部分）
            base_parsed = urlparse(base_url)
            base_path = base_parsed.path.rstrip("/")
            
            for item in root.findall("d:response", ns):
                href_text = item.findtext("d:href", default="", namespaces=ns)
                
                # 使用urlparse提取路径，处理各种URL格式
                href_parsed = urlparse(href_text)
                entry_path = unquote(href_parsed.path or "/")
                
                # 移除基础路径前缀
                if base_path and entry_path.startswith(base_path):
                    entry_path = entry_path[len(base_path):]
                
                # 确保路径以/开头
                if not entry_path.startswith("/"):
                    entry_path = "/" + entry_path
                
                entry_path = entry_path.rstrip("/")
                
                # 跳过根目录本身
                if entry_path == "/" or entry_path == "":
                    continue
                
                prop = item.find("d:propstat/d:prop", ns) if item is not None else None
                resource_type = prop.find("d:resourcetype", ns) if prop is not None else None
                is_dir = resource_type is not None and resource_type.find("d:collection", ns) is not None
                
                # 回退判断：路径以 / 结尾也视为目录
                if not is_dir and href_text.rstrip().endswith("/"):
                    is_dir = True
                
                entries.append({
                    "path": entry_path,
                    "is_dir": is_dir,
                    "name": os.path.basename(entry_path)
                })
        except Exception as e:
            print(f"ERROR: [WebDAV] 解析响应失败: {e}")
        
        return entries

    # ==================== 文件名解析 ====================
    def parse_video_filename(self, file_path: str) -> Dict[str, Any]:
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
            "file_path": file_path
        }
        
        filename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        # 提取年份
        year_match = re.search(r"[(（](\d{4})[)）]", name_without_ext)
        if year_match:
            result["year"] = int(year_match.group(1))
        
        # 提取季数和集数（支持 S01E01、S1E1、第1季第1集 等格式）
        # 先尝试匹配 S01E01 格式
        season_episode_match = re.search(r"[季Ss](\d+)[._ -]*[集Ee](\d+)", name_without_ext, re.IGNORECASE)
        # 如果没匹配到，尝试匹配 第1季第1集 格式
        if not season_episode_match:
            season_episode_match = re.search(r"第(\d+)季[._ -]*第(\d+)集", name_without_ext)
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
        clean_title = re.sub(r"[季Ss]\d+[._ -]*[集Ee]\d+", "", clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r"第\d+季[._ -]*第\d+集", "", clean_title)
        clean_title = re.sub(r"(4K|2160p|1080p|720p|480p)", "", clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r"(H264|H.264|H265|H.265|HEVC|AVC|VP9)", "", clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r"[\._\-[\](){}]", " ", clean_title)
        clean_title = re.sub(r"\s+", " ", clean_title).strip()
        
        result["title"] = clean_title
        
        # 根据路径判断分类
        path_lower = file_path.lower()
        if any(keyword in path_lower for keyword in ["动漫", "动画", "anime", "cartoon"]):
            result["category"] = "anime"
            result["is_series"] = True
        elif any(keyword in path_lower for keyword in ["电视剧", "剧集", "series", "season"]):
            result["category"] = "series"
            result["is_series"] = True
        
        return result

    def merge_series_videos(self, video_files: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        将视频文件合并为影视条目
        
        Args:
            video_files: 视频文件列表
        
        Returns:
            合并后的影视列表
        """
        movies = {}
        
        for video in video_files:
            parsed = self.parse_video_filename(video["file_path"])
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
                    "cover_path": None,
                    "intro": "",
                    "actors": [],
                    "director": ""
                }
            
            if parsed["is_series"] and parsed["episode"]:
                movies[title_key]["episodes"].append({
                    "episode": parsed["episode"],
                    "season": parsed["season"] or 1,
                    "file_path": video["file_path"]
                })
            else:
                movies[title_key]["file_path"] = video["file_path"]
        
        # 对剧集排序
        for movie in movies.values():
            movie["episodes"].sort(key=lambda e: (e["season"], e["episode"]))
        
        # 输出识别结果日志
        print("INFO: ==================================================")
        print("INFO: [识别结果]")
        for movie in movies.values():
            title = movie["title"]
            episodes_count = len(movie.get("episodes", []))
            category = movie.get("category", "movie")
            season = movie.get("episodes", [{}])[0].get("season", 1) if episodes_count > 0 else 1
            
            # 确定类型显示
            if category == "anime":
                type_display = "动漫"
            elif category == "series":
                type_display = "剧集"
            elif episodes_count == 1 and "剧场版" in title or "OVA" in title or "OAD" in title:
                type_display = "番外"
            else:
                type_display = "电影"
            
            # 确定刮削源
            if category == "anime":
                scrape_source = "动漫科"
            else:
                scrape_source = "TMDB"
            
            # 季数显示
            if episodes_count > 0:
                season_display = f"第{season}季"
            else:
                season_display = "单季"
            
            # 特殊处理动漫电影
            if episodes_count == 1 and ("剧场版" in title or "OVA" in title or "OAD" in title) and category == "anime":
                print(f'INFO: 扫描到《{title}》，判断为动漫电影，开始从动漫科刮削')
                print(f'INFO: 搜索名：{title}')
            else:
                print(f'INFO: 《{title}》{season_display} | 集数: {episodes_count} | 类型: {type_display} | 选择刮削源: {scrape_source}')
                print(f'INFO: 搜索名: {title}')
        
        return list(movies.values())

    # ==================== 封面刮削 - 增强版 ====================
    def _is_anime_content(self, movie_data):
        haystacks = [
            str(movie_data.get("type", "") or "").strip().lower(),
            str(movie_data.get("title", "") or "").strip().lower(),
            str(movie_data.get("name", "") or "").strip().lower(),
            str(movie_data.get("path", "") or "").strip().lower(),
        ]
        keywords = ["动画", "动漫", "anime", "anibk", "番剧", "/动漫/", "/动画/"]
        return any(keyword in haystack for haystack in haystacks for keyword in keywords)

    def _fetch_tmdb_list(self, query, is_series=False):
        """获取TMDB搜索结果"""
        try:
            api_key = getattr(self.config, "TMDB_API_KEY", "").strip()
            if not api_key:
                return []
            
            media_type = "tv" if is_series else "movie"
            search_url = f"{self.tmdb_api_base}/search/{media_type}?api_key={api_key}&query={quote(query)}&language=zh-CN"
            
            response = requests.get(search_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title") or item.get("name", ""),
                    "url": f"tmdb://{media_type}/{item.get('id', '')}",
                    "match_score": 80,
                    "source": "TMDB"
                })
            return results
        except Exception:
            return []

    def _fetch_anibk_list(self, query):
        """获取动漫科搜索结果"""
        try:
            url = f"{ANIBK_SEARCH}{quote(query)}"
            response = requests.get(url, headers=HEADERS, timeout=12)
            response.raise_for_status()
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            
            items = soup.find_all("div", class_="bk-content")
            results = []
            for item in items[:6]:
                link = item.find("a", href=True)
                if link:
                    results.append({
                        "title": link.get_text(strip=True),
                        "url": f"{ANIBK_BASE}{link['href']}",
                        "match_score": 75,
                        "source": "AniBK"
                    })
            return results
        except Exception:
            return []

    def _download_cover(self, cover_url, name):
        """下载封面到本地"""
        try:
            if not cover_url:
                return None
            
            valid_name = "".join([c for c in name if c.isalnum() or c in (" ", "-", "_")])
            cover_path = os.path.join(self.cover_dir, f"{valid_name}.jpg")
            
            headers = HEADERS.copy()
            if ANIBK_BASE in cover_url:
                headers["Referer"] = ANIBK_BASE
            elif "doubanio.com" in cover_url or "douban.com" in cover_url:
                headers["Referer"] = DOUBAN_BASE
            elif "themoviedb.org" in cover_url:
                headers["Referer"] = TMDB_BASE
            
            response = requests.get(cover_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            with open(cover_path, "wb") as f:
                f.write(response.content)
            
            # 验证封面有效性
            if os.path.getsize(cover_path) < 2048:
                os.remove(cover_path)
                return None
            
            return cover_path
        except Exception:
            return None

    def _get_anibk_cover(self, detail_url):
        """提取动漫科封面"""
        try:
            headers = HEADERS.copy()
            headers["Referer"] = ANIBK_BASE
            res = requests.get(detail_url, headers=headers, timeout=12)
            res.raise_for_status()
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            cover_box = soup.find("div", class_="bk-main-pic") or soup.find("div", class_="rbox-pic")
            if cover_box:
                img = cover_box.find("img", src=True)
                if img and img["src"]:
                    return img["src"]
            return None
        except Exception:
            return None

    def _get_anibk_intro(self, detail_url):
        """提取动漫科简介 + 自动翻译"""
        try:
            headers = HEADERS.copy()
            headers["Referer"] = ANIBK_BASE
            res = requests.get(detail_url, headers=headers, timeout=12)
            res.raise_for_status()
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            intro_container = soup.find("div", class_="bkir-content")
            if not intro_container:
                return ""
            full_intro = []
            for p in intro_container.find_all("p"):
                text = p.get_text(strip=True)
                if text:
                    full_intro.append(text)
            intro = "".join(full_intro) if full_intro else ""
            return translate_to_chinese(intro)
        except Exception:
            return ""

    def _fetch_anibk_year(self, detail_url):
        """提取动漫科年份"""
        try:
            headers = HEADERS.copy()
            headers["Referer"] = ANIBK_BASE
            res = requests.get(detail_url, headers=headers, timeout=12)
            res.raise_for_status()
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            page_text = soup.get_text()
            
            date_match = re.search(r'(上映时间|发行时间|首播时间|播出时间)\s*[：:]\s*(\d{4})', page_text)
            if date_match:
                return int(date_match.group(2))
            
            full_date_match = re.search(r'(\d{4})-\d{2}-\d{2}', page_text)
            if full_date_match:
                return int(full_date_match.group(1))
            
            return None
        except Exception:
            return None

    def _get_tmdb_cover(self, detail_url):
        """提取TMDB封面"""
        try:
            if detail_url.startswith("tmdb://"):
                parts = detail_url.replace("tmdb://", "", 1).split("/", 1)
                if len(parts) == 2:
                    media_type, item_id = parts
                    api_key = getattr(self.config, "TMDB_API_KEY", "").strip()
                    if api_key:
                        detail_data = self._tmdb_api_get(f"/{media_type}/{item_id}")
                        if detail_data:
                            poster_path = detail_data.get("poster_path")
                            if poster_path:
                                return f"{self.tmdb_image_base.rstrip('/')}/{poster_path.lstrip('/')}"
            
            headers = HEADERS.copy()
            headers["Referer"] = TMDB_BASE
            res = requests.get(detail_url, headers=headers, timeout=12)
            res.raise_for_status()
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            og_img = soup.find("meta", property="og:image")
            if og_img and og_img.get("content"):
                return og_img["content"]
            return None
        except Exception:
            return None

    def _get_tmdb_intro(self, detail_url):
        """提取TMDB简介 + 自动翻译"""
        try:
            if detail_url.startswith("tmdb://"):
                parts = detail_url.replace("tmdb://", "", 1).split("/", 1)
                if len(parts) == 2:
                    media_type, item_id = parts
                    api_key = getattr(self.config, "TMDB_API_KEY", "").strip()
                    if api_key:
                        detail_data = self._tmdb_api_get(f"/{media_type}/{item_id}")
                        if detail_data:
                            intro = detail_data.get("overview", "").strip()
                            return translate_to_chinese(intro)
            
            headers = HEADERS.copy()
            headers["Referer"] = TMDB_BASE
            res = requests.get(detail_url, headers=headers, timeout=12)
            res.raise_for_status()
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            og_desc = soup.find("meta", property="og:description")
            if og_desc and og_desc.get("content"):
                return translate_to_chinese(og_desc["content"].strip())
            return ""
        except Exception:
            return ""

    def _fetch_tmdb_year(self, detail_url):
        """提取TMDB年份"""
        try:
            if detail_url.startswith("tmdb://"):
                parts = detail_url.replace("tmdb://", "", 1).split("/", 1)
                if len(parts) == 2:
                    media_type, item_id = parts
                    api_key = getattr(self.config, "TMDB_API_KEY", "").strip()
                    if api_key:
                        detail_data = self._tmdb_api_get(f"/{media_type}/{item_id}")
                        if detail_data:
                            release_date = detail_data.get("release_date") or detail_data.get("first_air_date") or ""
                            year_match = re.search(r"(\d{4})", release_date)
                            if year_match:
                                return int(year_match.group(1))
            return None
        except Exception:
            return None

    def _tmdb_api_get(self, path, params=None):
        """调用TMDB API"""
        if self._tmdb_is_temporarily_disabled():
            raise RuntimeError(self._tmdb_failure_reason or "TMDB is temporarily unavailable")
        api_key = getattr(self.config, "TMDB_API_KEY", "").strip()
        if not api_key:
            raise ValueError("TMDB API key is not configured")
        
        query = {"api_key": api_key, "language": "zh-CN"}
        if params:
            query.update(params)
        
        try:
            response = requests.get(f"{self.tmdb_api_base}{path}", params=query, timeout=4)
            response.raise_for_status()
            self._reset_tmdb_availability()
            return response.json()
        except Exception as exc:
            self._disable_tmdb_temporarily(exc)
            raise

    def scrape_cover(self, movie_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        刮削影视封面和元数据（增强版）
        
        Args:
            movie_data: 影视基本信息
        
        Returns:
            更新后的影视信息（包含封面路径、简介和年份）
        """
        name = movie_data.get("title", "")
        
        # 输出刮削详情开始日志
        episodes_count = len(movie_data.get("episodes", []))
        target_season = movie_data.get("season", 1) if episodes_count > 0 else 0
        media_type = "series" if episodes_count > 0 else "movie"
        print(f"INFO: [刮削详情] 目标: {name} | 季数: {target_season or 1} | 类型: {media_type}")
        
        # 准备刮削数据
        scrape_data = {
            "title": name,
            "name": name,
            "year": movie_data.get("year"),
            "season": target_season,
            "is_series": movie_data.get("is_series", episodes_count > 0),
            "type": movie_data.get("category", "movie"),
            "path": movie_data.get("file_path", "")
        }
        
        # 使用 CoverScraper 进行刮削
        cover_path, intro_text, scraped_year = self.cover_scraper.search_cover(scrape_data)
        
        # 更新影视数据
        if cover_path:
            movie_data["cover_path"] = cover_path
            print(f"INFO: 封面下载成功: {name}_S{target_season or 1}")
        if intro_text:
            movie_data["intro"] = intro_text[:500] if len(intro_text) > 500 else intro_text
            print(f"INFO: 简介提取成功，长度: {len(movie_data['intro'])} 字符")
        if scraped_year:
            movie_data["year"] = scraped_year
            print(f"INFO: 年份提取成功: {scraped_year}")
        
        if cover_path or intro_text or scraped_year:
            print(f"INFO: 刮削成功 | 标题: {name}")
        else:
            print(f"INFO: 刮削无结果 | 标题: {name}")
        
        return movie_data

    # ==================== 完整扫描流程 ====================
    def scan_library(self, source_id: Optional[str] = None) -> Dict[str, Any]:
        """
        执行完整的媒体库扫描流程
        
        Args:
            source_id: 可选，指定要扫描的数据源ID
        
        Returns:
            扫描结果，包含影视列表和统计信息
        """
        # 获取所有数据源
        from app.services.source_service import SourceService
        source_service = SourceService()
        
        if source_id:
            sources = [source_service.get_source_by_id(source_id)]
            if not sources[0]:
                return {"error": "数据源不存在"}
        else:
            sources = source_service.get_all_sources()
        
        # 输出扫描开始日志
        print(f"INFO: [扫描] 开始扫描远程媒体源")
        
        # 扫描所有数据源
        all_video_files = []
        for source in sources:
            if source["type"] == "WebDAV":
                # 解析URL获取连接信息
                url = source.get("path", "")
                print(f"INFO: [扫描] 数据源: {source.get('name')} | 原始URL: {url}")
                
                # 先解码URL，处理中文路径
                try:
                    url = unquote(url)
                    print(f"INFO: [扫描] 解码后URL: {url}")
                except Exception as e:
                    print(f"WARNING: [扫描] URL解码失败: {e}")
                
                parsed_url = urlparse(url)
                
                host = parsed_url.hostname or ""
                port = parsed_url.port or ""
                protocol = parsed_url.scheme or "http"
                
                # 获取挂载路径，处理逗号分隔的多个路径
                raw_path = parsed_url.path or "/"
                try:
                    raw_path = unquote(raw_path)
                except Exception as e:
                    print(f"WARNING: [扫描] 路径解码失败: {e}")
                
                # 拆分逗号分隔的多个路径
                paths = [p.strip() for p in raw_path.split(',') if p.strip()]
                
                # 清理路径：移除开头的多余斜杠和结尾的斜杠
                cleaned_paths = []
                for p in paths:
                    # 移除开头可能的多余斜杠
                    while p.startswith('//'):
                        p = p[1:]
                    # 移除结尾的斜杠
                    p = p.rstrip('/')
                    # 确保以/开头
                    if not p.startswith('/'):
                        p = '/' + p
                    if p:
                        cleaned_paths.append(p)
                
                paths = cleaned_paths if cleaned_paths else ["/"]
                
                print(f"INFO: [扫描] 主机: {host} | 端口: {port} | 协议: {protocol} | 挂载路径: {paths}")
                
                # 确保端口号有效
                port_str = str(port) if port else ""
                
                # 扫描每个挂载路径
                for mount_path in paths:
                    print(f"INFO: [扫描] 开始扫描路径: {mount_path}")
                    files = self.scan_webdav(
                        host=host,
                        port=port_str,
                        protocol=protocol,
                        username=source.get("username", ""),
                        password=source.get("password", ""),
                        paths=[mount_path]
                    )
                    print(f"INFO: [扫描] 路径 {mount_path} 扫描完成，发现 {len(files)} 个视频文件")
                    all_video_files.extend(files)
        
        # 输出扫描完成日志
        print(f"INFO: [完成] 远程扫描完成 | 视频文件总数: {len(all_video_files)} 个")
        
        # 合并视频文件为影视条目
        movies = self.merge_series_videos(all_video_files)
        
        # 清空旧数据
        db_manager.delete_all_movies()
        
        # 保存新数据到SQLite
        for movie in movies:
            # 对每个影视进行封面刮削
            self.scrape_cover(movie)
            
            # 添加影视记录
            movie_data = {
                "title": movie["title"],
                "year": movie["year"],
                "category": movie["category"],
                "is_series": movie["is_series"],
                "resolution": movie["resolution"],
                "codec": movie["codec"],
                "remote_provider": movie["remote_provider"],
                "source_label": movie["source_label"],
                "cover_path": movie["cover_path"],
                "intro": movie["intro"],
                "actors": ",".join(movie["actors"]) if isinstance(movie["actors"], list) else movie["actors"],
                "director": movie["director"],
                "file_path": movie.get("file_path"),
                "created_at": int(time.time())
            }
            
            movie_id = db_manager.add_movie(movie_data)
            
            # 添加剧集记录
            if movie.get("episodes"):
                db_manager.add_episodes(movie_id, movie["episodes"])
        
        # 获取统计信息
        stats = db_manager.get_library_stats()
        
        # 输出统计日志
        print(f"INFO: [统计] 远程媒体源扫描完成 | 识别总数: {stats['total']} 部")
        print(f"INFO: ==================================================")
        
        return {
            "total": stats["total"],
            "movies": stats["movies"],
            "series": stats["series"],
            "anime": stats["anime"],
            "total_episodes": stats["total_episodes"],
            "message": f"扫描完成，共发现 {stats['total']} 部影视"
        }

    def refresh_library(self) -> Dict[str, Any]:
        """刷新媒体库（强制重新扫描）"""
        return self.scan_library()

    def get_library_stats(self) -> Dict[str, Any]:
        """获取媒体库统计信息"""
        return db_manager.get_library_stats()

    def get_movies(self, page: int = 1, page_size: int = 24, 
                   category: Optional[str] = None, keyword: Optional[str] = None) -> Dict[str, Any]:
        """
        分页获取影视列表
        
        Args:
            page: 页码
            page_size: 每页数量
            category: 分类筛选
            keyword: 关键词搜索
        
        Returns:
            包含影视列表和分页信息的字典
        """
        return db_manager.get_movies_with_pagination(page, page_size, category, keyword)

    def get_movie_by_id(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取影视详情
        
        Args:
            movie_id: 影视ID
        
        Returns:
            影视详情字典
        """
        movie = db_manager.get_movie(movie_id)
        if movie:
            movie["episodes"] = db_manager.get_episodes_by_movie_id(movie_id)
        return movie


# 创建全局扫描服务实例
scan_service = ScanService()
