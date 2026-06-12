import hashlib
import os
import re
import time
from http.cookies import SimpleCookie
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from app.config.app_config import AppConfig

# ==================== 全局配置与请求头 ====================
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
IMDB_BASE = "https://www.imdb.com"


# ==================== 翻译辅助函数 ====================
def is_chinese(text):
    """判断文本是否主要为中文（避免重复翻译）"""
    if not text:
        return True
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    return len(chinese_chars) / len(text) > 0.3


def translate_to_chinese(text):
    """自动翻译非中文文本为中文"""
    if not text or is_chinese(text):
        return text
    try:
        translated = GoogleTranslator(source='auto', target='zh-CN').translate(text)
        return translated
    except Exception as e:
        return text


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


# ==================== 核心刮削类 ====================
class CoverScraper:
    def __init__(self):
        self.config = AppConfig()
        self.save_dir = os.path.join(str(self.config.DATA_DIR), "covers")
        self.tmdb_api_base = getattr(self.config, "TMDB_API_BASE", "https://api.themoviedb.org/3")
        self.tmdb_image_base = getattr(self.config, "TMDB_IMAGE_BASE", TMDB_IMG_BASE)
        self._last_candidate_diagnostics = []
        self._tmdb_disabled_until = 0
        self._tmdb_failure_reason = ""
        os.makedirs(self.save_dir, exist_ok=True)

    def _build_douban_headers(self):
        headers = HEADERS.copy()
        headers["Referer"] = DOUBAN_BASE
        headers["Origin"] = DOUBAN_BASE
        headers["Sec-Fetch-Dest"] = "document"
        headers["Sec-Fetch-Mode"] = "navigate"
        headers["Sec-Fetch-Site"] = "same-site"
        headers["Upgrade-Insecure-Requests"] = "1"
        cookie = str(getattr(self.config, "DOUBAN_COOKIE", "") or "").strip()
        if cookie:
            headers["Cookie"] = cookie
        return headers

    def _apply_douban_cookie(self, session, cookie_value):
        raw_cookie = str(cookie_value or "").strip()
        if not raw_cookie:
            return
        try:
            parsed = SimpleCookie()
            parsed.load(raw_cookie)
            for morsel in parsed.values():
                session.cookies.set(
                    morsel.key,
                    morsel.value,
                    domain=".douban.com",
                    path=morsel["path"] or "/",
                )
        except Exception as exc:
            pass

    def _tmdb_is_temporarily_disabled(self):
        return time.time() < float(self._tmdb_disabled_until or 0)

    def _disable_tmdb_temporarily(self, reason, cooldown=180):
        self._tmdb_disabled_until = time.time() + cooldown
        self._tmdb_failure_reason = str(reason or "")

    def _reset_tmdb_availability(self):
        self._tmdb_disabled_until = 0
        self._tmdb_failure_reason = ""

    def _is_probably_valid_cover(self, file_path):
        try:
            if not file_path or not os.path.exists(file_path):
                return False
            if os.path.getsize(file_path) < 2048:
                return False
            with open(file_path, "rb") as fh:
                header = fh.read(32)
            return (
                header.startswith(b"\xff\xd8\xff")
                or header.startswith(b"\x89PNG\r\n\x1a\n")
                or header.startswith(b"RIFF")
                or header.startswith(b"WEBP", 8)
            )
        except Exception:
            return False

    def _solve_douban_challenge(self, session, response):
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form", id="sec")
            if not form:
                return False

            tok_input = form.find("input", {"name": "tok"})
            cha_input = form.find("input", {"name": "cha"})
            red_input = form.find("input", {"name": "red"})
            if not tok_input or not cha_input or not red_input:
                return False

            difficulty = 4
            difficulty_match = re.search(r"process\(data,\s*difficulty\s*=\s*(\d+)\)", response.text)
            if difficulty_match:
                difficulty = int(difficulty_match.group(1))

            tok = tok_input.get("value", "")
            cha = cha_input.get("value", "")
            red = red_input.get("value", "")
            nonce = 0
            prefix = "0" * difficulty
            while True:
                nonce += 1
                digest = hashlib.sha512(f"{cha}{nonce}".encode("utf-8")).hexdigest()
                if digest.startswith(prefix):
                    break

            challenge_headers = dict(session.headers)
            challenge_headers.update({
                "Referer": response.url,
                "Origin": "https://sec.douban.com",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
            })
            challenge_url = urljoin(response.url, form.get("action") or "/c")
            challenge_response = session.post(
                challenge_url,
                data={"tok": tok, "cha": cha, "sol": str(nonce), "red": red},
                headers=challenge_headers,
                timeout=20,
                allow_redirects=False,
            )
            return challenge_response.status_code in {200, 302, 303}
        except Exception as exc:
            return False

    def _douban_get(self, url):
        session = requests.Session()
        headers = self._build_douban_headers()
        if "/j/subject_suggest" in str(url):
            headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
            headers["X-Requested-With"] = "XMLHttpRequest"
            headers["Sec-Fetch-Dest"] = "empty"
            headers["Sec-Fetch-Mode"] = "cors"
            headers["Sec-Fetch-Site"] = "same-origin"
            headers["Referer"] = f"{DOUBAN_BASE}/"
        session.headers.update(headers)
        cookie = str(getattr(self.config, "DOUBAN_COOKIE", "") or "").strip()
        self._apply_douban_cookie(session, cookie)
        response = session.get(url, timeout=15, allow_redirects=True)
        if "sec.douban.com" in response.url or 'id="sec"' in response.text:
            solved = self._solve_douban_challenge(session, response)
            if solved:
                response = session.get(url, timeout=15, allow_redirects=True)
        return session, response

    def _get_douban_detail_soup(self, detail_url):
        try:
            _session, response = self._douban_get(detail_url)
            response.raise_for_status()
            response.encoding = "utf-8"
            return BeautifulSoup(response.text, "html.parser")
        except Exception as exc:
            return None

    def _has_tmdb_api_key(self):
        return bool(getattr(self.config, "TMDB_API_KEY", "").strip())

    def _tmdb_media_type(self, is_series):
        return "tv" if is_series else "movie"

    def _build_tmdb_locator(self, media_type, item_id):
        return f"tmdb://{media_type}/{item_id}"

    def _parse_tmdb_locator(self, detail_url):
        if not isinstance(detail_url, str) or not detail_url.startswith("tmdb://"):
            return None, None
        parts = detail_url.replace("tmdb://", "", 1).split("/", 1)
        if len(parts) != 2:
            return None, None
        media_type, item_id = parts
        if media_type not in {"movie", "tv"} or not item_id.isdigit():
            return None, None
        return media_type, item_id

    def _tmdb_api_get(self, path, params=None):
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

    def _tmdb_api_detail(self, detail_url):
        media_type, item_id = self._parse_tmdb_locator(detail_url)
        if not media_type or not item_id:
            return None
        try:
            return self._tmdb_api_get(f"/{media_type}/{item_id}")
        except Exception as exc:
            return None

    def _fetch_tmdb_list(self, query, is_series=False):
        """TMDB搜索"""
        if self._tmdb_is_temporarily_disabled():
            return []
        try:
            media_type = self._tmdb_media_type(is_series)
            params = {"query": query, "language": "zh-CN"}
            result = self._tmdb_api_get(f"/search/{media_type}", params)
            return result.get("results", [])[:8]
        except Exception:
            return []

    def _get_tmdb_cover(self, tmdb_url):
        """从TMDB URL提取封面"""
        if not tmdb_url or "themoviedb.org" not in tmdb_url:
            return None
        try:
            response = requests.get(tmdb_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            meta = soup.find("meta", property="og:image")
            if meta:
                return meta.get("content")
        except Exception:
            pass
        return None

    def _download_cover(self, url, name):
        """下载封面图片"""
        if not url or not name:
            return None
        try:
            # 根据图片来源添加正确的 Referer 头
            headers = HEADERS.copy()
            if "doubanio.com" in url or "douban.com" in url:
                headers["Referer"] = DOUBAN_BASE
            elif "anibk.com" in url:
                headers["Referer"] = ANIBK_BASE
            elif "themoviedb.org" in url or "tmdb.org" in url:
                headers["Referer"] = TMDB_BASE
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            valid_name = "".join([c for c in name if c.isalnum() or c in (" ", "-", "_")])
            ext = ".jpg"
            if url.lower().endswith(".png"):
                ext = ".png"
            elif url.lower().endswith(".webp"):
                ext = ".webp"
            
            save_path = os.path.join(self.save_dir, f"{valid_name}{ext}")
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            if self._is_probably_valid_cover(save_path):
                return save_path
            else:
                os.remove(save_path)
                return None
        except Exception:
            return None

    def _parse_douban_cover(self, soup):
        """解析豆瓣封面"""
        if not soup:
            return None
        meta = soup.find("meta", property="og:image")
        if meta:
            return meta.get("content")
        return None

    def _parse_douban_intro(self, soup):
        """解析豆瓣简介"""
        if not soup:
            return None
        intro_tag = soup.find("span", property="v:summary")
        if intro_tag:
            text = intro_tag.get_text(strip=True)
            return translate_to_chinese(text)
        return None

    def _parse_douban_year(self, soup):
        """解析豆瓣年份"""
        if not soup:
            return None
        year_tag = soup.find("span", class_="year")
        if year_tag:
            match = re.search(r'\d{4}', year_tag.get_text())
            if match:
                return match.group()
        return None

    def search_candidates(self, movie_data, custom_name=None):
        """搜索候选结果"""
        candidates = []
        name = custom_name or movie_data.get("name", "")
        parsed = clean_title_for_search(name)
        clean_name = parsed["clean_name"]
        
        # AniBK搜索（动漫）
        if self._is_anime_content(movie_data):
            try:
                search_url = ANIBK_SEARCH + quote(clean_name)
                response = requests.get(search_url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                items = soup.find_all("li", class_="search-item")[:6]
                for item in items:
                    title_tag = item.find("h3")
                    if title_tag:
                        candidates.append({
                            "title": title_tag.get_text(strip=True),
                            "url": urljoin(ANIBK_BASE, title_tag.find("a")["href"]) if title_tag.find("a") else "",
                            "source": "AniBK",
                            "match_score": 80
                        })
            except Exception:
                pass
        
        # 豆瓣搜索
        try:
            search_url = f"{DOUBAN_BASE}/j/subject_suggest?q={quote(clean_name)}"
            response = requests.get(search_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            results = response.json()[:6]
            for item in results:
                candidates.append({
                    "title": item.get("title", ""),
                    "url": f"{DOUBAN_BASE}/subject/{item.get('id', '')}/",
                    "source": "Douban",
                    "match_score": 75
                })
        except Exception:
            pass
        
        # TMDB搜索
        try:
            is_series = movie_data.get("is_series", False)
            tmdb_results = self._fetch_tmdb_list(clean_name, is_series)[:6]
            for item in tmdb_results:
                candidates.append({
                    "title": item.get("title", "") or item.get("name", ""),
                    "url": f"tmdb://{'tv' if is_series else 'movie'}/{item.get('id', '')}",
                    "source": "TMDB",
                    "match_score": 70
                })
        except Exception:
            pass
        
        return candidates

    def _is_anime_content(self, movie_data):
        haystacks = [
            str(movie_data.get("type", "") or "").strip().lower(),
            str(movie_data.get("title", "") or "").strip().lower(),
            str(movie_data.get("name", "") or "").strip().lower(),
            str(movie_data.get("path", "") or "").strip().lower(),
        ]
        keywords = ["动画", "动漫", "anime", "anibk", "番剧", "/动漫/", "/动画/"]
        return any(keyword in haystack for haystack in haystacks for keyword in keywords)

    def download_by_candidate(self, candidate, movie_data):
        """根据候选结果下载封面和元数据"""
        cover_path = None
        intro_text = None
        year = None
        source = candidate.get("source", "")
        
        if source == "Douban":
            soup = self._get_douban_detail_soup(candidate.get("url", ""))
            if soup:
                cover_url = self._parse_douban_cover(soup)
                cover_path = self._download_cover(cover_url, candidate.get("title", ""))
                intro_text = self._parse_douban_intro(soup)
                year = self._parse_douban_year(soup)
        
        elif source == "AniBK":
            try:
                response = requests.get(candidate.get("url", ""), headers=HEADERS, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                
                # 解析封面
                cover_tag = soup.find("div", class_="film-poster")
                if cover_tag:
                    img_tag = cover_tag.find("img")
                    if img_tag:
                        cover_url = img_tag.get("src")
                        cover_path = self._download_cover(cover_url, candidate.get("title", ""))
                
                # 解析简介
                intro_tag = soup.find("div", class_="film-detail")
                if intro_tag:
                    intro_text = intro_tag.get_text(strip=True)[:500]
                    intro_text = translate_to_chinese(intro_text)
            except Exception:
                pass
        
        elif source == "TMDB":
            tmdb_data = self._tmdb_api_detail(candidate.get("url", ""))
            if tmdb_data:
                poster_path = tmdb_data.get("poster_path")
                if poster_path:
                    cover_url = f"{self.tmdb_image_base}{poster_path}"
                    cover_path = self._download_cover(cover_url, candidate.get("title", ""))
                
                overview = tmdb_data.get("overview", "")
                if overview:
                    intro_text = translate_to_chinese(overview)
                
                release_date = tmdb_data.get("release_date", "") or tmdb_data.get("first_air_date", "")
                if release_date:
                    year = release_date[:4]
        
        return cover_path, intro_text, year

    def _movie_flow(self, clean_base, year, is_anime, valid_name):
        """电影搜索流程"""
        queries = [clean_base]
        if year:
            queries.append(f"{clean_base} {year}")
        
        for query in queries:
            # 豆瓣搜索
            try:
                search_url = f"{DOUBAN_BASE}/j/subject_suggest?q={quote(query)}"
                response = requests.get(search_url, headers=HEADERS, timeout=10)
                results = response.json()[:3]
                for item in results:
                    detail_url = f"{DOUBAN_BASE}/subject/{item.get('id', '')}/"
                    soup = self._get_douban_detail_soup(detail_url)
                    if soup:
                        cover_url = self._parse_douban_cover(soup)
                        cover_path = self._download_cover(cover_url, valid_name)
                        intro_text = self._parse_douban_intro(soup)
                        year_text = self._parse_douban_year(soup)
                        if cover_path:
                            return cover_path, intro_text, year_text
            except Exception:
                pass
            
            # TMDB搜索
            try:
                tmdb_results = self._fetch_tmdb_list(query, is_series=False)[:3]
                for item in tmdb_results:
                    poster_path = item.get("poster_path")
                    if poster_path:
                        cover_url = f"{self.tmdb_image_base}{poster_path}"
                        cover_path = self._download_cover(cover_url, valid_name)
                        overview = translate_to_chinese(item.get("overview", ""))
                        release_date = item.get("release_date", "")[:4] if item.get("release_date") else ""
                        if cover_path:
                            return cover_path, overview, release_date
            except Exception:
                pass
        
        return None, None, None

    def _s1_flow(self, clean_base, year, target_season, is_anime, valid_name, movie_data):
        """第一季搜索流程"""
        # 先尝试精准搜索
        queries = [clean_base]
        if year:
            queries.append(f"{clean_base} {year}")
        
        for query in queries:
            # AniBK（动漫优先）
            if is_anime:
                try:
                    search_url = ANIBK_SEARCH + quote(query)
                    response = requests.get(search_url, headers=HEADERS, timeout=10)
                    soup = BeautifulSoup(response.text, "html.parser")
                    items = soup.find_all("li", class_="search-item")[:3]
                    for item in items:
                        title_tag = item.find("h3")
                        if title_tag and title_tag.find("a"):
                            detail_url = urljoin(ANIBK_BASE, title_tag.find("a")["href"])
                            response_detail = requests.get(detail_url, headers=HEADERS, timeout=10)
                            soup_detail = BeautifulSoup(response_detail.text, "html.parser")
                            
                            cover_tag = soup_detail.find("div", class_="film-poster")
                            if cover_tag and cover_tag.find("img"):
                                cover_url = cover_tag.find("img").get("src")
                                cover_path = self._download_cover(cover_url, f"{valid_name}_S{target_season}")
                                if cover_path:
                                    return cover_path, None, None
                except Exception:
                    pass
            
            # 豆瓣搜索
            try:
                search_url = f"{DOUBAN_BASE}/j/subject_suggest?q={quote(query)}"
                response = requests.get(search_url, headers=HEADERS, timeout=10)
                results = response.json()[:3]
                for item in results:
                    detail_url = f"{DOUBAN_BASE}/subject/{item.get('id', '')}/"
                    soup = self._get_douban_detail_soup(detail_url)
                    if soup:
                        cover_url = self._parse_douban_cover(soup)
                        cover_path = self._download_cover(cover_url, f"{valid_name}_S{target_season}")
                        intro_text = self._parse_douban_intro(soup)
                        year_text = self._parse_douban_year(soup)
                        if cover_path:
                            return cover_path, intro_text, year_text
            except Exception:
                pass
            
            # TMDB搜索
            try:
                is_series = movie_data.get("is_series", True)
                tmdb_results = self._fetch_tmdb_list(query, is_series=is_series)[:3]
                for item in tmdb_results:
                    poster_path = item.get("poster_path")
                    if poster_path:
                        cover_url = f"{self.tmdb_image_base}{poster_path}"
                        cover_path = self._download_cover(cover_url, f"{valid_name}_S{target_season}")
                        overview = translate_to_chinese(item.get("overview", ""))
                        release_date = item.get("release_date", "")[:4] if item.get("release_date") else item.get("first_air_date", "")[:4] if item.get("first_air_date") else ""
                        if cover_path:
                            return cover_path, overview, release_date
            except Exception:
                pass
        
        return None, None, None

    def _season_specific_search_anibk(self, clean_base, target_season, valid_name):
        """AniBK季数精准搜索"""
        try:
            search_url = ANIBK_SEARCH + quote(f"{clean_base} 第{target_season}季")
            response = requests.get(search_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.find_all("li", class_="search-item")[:3]
            for item in items:
                title_tag = item.find("h3")
                if title_tag and title_tag.find("a"):
                    detail_url = urljoin(ANIBK_BASE, title_tag.find("a")["href"])
                    response_detail = requests.get(detail_url, headers=HEADERS, timeout=10)
                    soup_detail = BeautifulSoup(response_detail.text, "html.parser")
                    
                    cover_tag = soup_detail.find("div", class_="film-poster")
                    if cover_tag and cover_tag.find("img"):
                        cover_url = cover_tag.find("img").get("src")
                        cover_path = self._download_cover(cover_url, f"{valid_name}_S{target_season}")
                        if cover_path:
                            return cover_path, None, None
        except Exception:
            pass
        return None, None, None

    def _season_specific_search_tmdb(self, clean_base, target_season, is_series, valid_name):
        """TMDB季数精准搜索"""
        try:
            tmdb_results = self._fetch_tmdb_list(clean_base, is_series=is_series)[:3]
            for item in tmdb_results:
                tmdb_id = item.get("id")
                if tmdb_id:
                    season_data = self._tmdb_api_get(f"/tv/{tmdb_id}/season/{target_season}")
                    if season_data:
                        poster_path = season_data.get("poster_path")
                        if poster_path:
                            cover_url = f"{self.tmdb_image_base}{poster_path}"
                            cover_path = self._download_cover(cover_url, f"{valid_name}_S{target_season}")
                            overview = translate_to_chinese(season_data.get("overview", ""))
                            air_date = season_data.get("air_date", "")[:4] if season_data.get("air_date") else ""
                            if cover_path:
                                return cover_path, overview, air_date
        except Exception:
            pass
        return None, None, None

    def search_cover(self, movie_data, custom_name=None, force_update_meta=False):
        """
        增强版：刮削封面 + 剧情简介（自动翻译） + 年份
        """
        name = custom_name or movie_data.get("name", movie_data.get("title", ""))
        is_anime = self._is_anime_content(movie_data)
        target_season = movie_data.get("season", 0)
        is_movie = not movie_data.get("is_series", False) and target_season == 0
        current_year = movie_data.get("year", 2024)
        current_intro = movie_data.get("intro", "")

        valid_name = "".join([c for c in name if c.isalnum() or c in (" ", "-", "_")])
        local_cover_path = None
        
        # 检查本地已有封面
        for suffix in ["jpg", "png", "webp"]:
            local_path = os.path.join(self.save_dir, f"{valid_name}.{suffix}")
            local_path_season = os.path.join(self.save_dir, f"{valid_name}_S{target_season}.{suffix}")
            if os.path.exists(local_path):
                local_cover_path = local_path
                break
            if os.path.exists(local_path_season):
                local_cover_path = local_path_season
                break

        # 验证本地封面有效性
        if local_cover_path and not self._is_probably_valid_cover(local_cover_path):
            try:
                os.remove(local_cover_path)
            except OSError:
                pass
            local_cover_path = None

        # 如果有本地封面且不需要强制更新，仍然需要获取简介和年份
        # 但不需要重新下载封面
        if local_cover_path and not force_update_meta:
            cover_path = local_cover_path
            # 继续获取简介和年份，不直接返回

        parsed = clean_title_for_search(movie_data.get("title", ""))
        clean_base = parsed["clean_name"] or name
        year = movie_data.get("year", "")

        cover_path = local_cover_path
        intro_text = current_intro
        scraped_year = current_year

        # 先走统一候选搜索
        candidates = self.search_candidates(movie_data, custom_name=custom_name)
        for candidate in candidates[:6]:
            candidate_score = float(candidate.get("match_score") or 0)
            candidate_source = str(candidate.get("source") or "")
            if candidate_score < 20:
                continue
            if candidate_source == "AniBK" and not is_anime:
                continue
            new_cover, new_intro, new_year = self.download_by_candidate(candidate, movie_data)
            if new_cover:
                cover_path = new_cover
            if new_intro:
                intro_text = new_intro
            if new_year:
                scraped_year = new_year
            if new_cover or new_intro or new_year:
                return cover_path, intro_text, scraped_year

        # 分情况处理
        if is_movie:
            new_cover, new_intro, new_year = self._movie_flow(clean_base, year, is_anime, valid_name)
            if new_cover:
                cover_path = new_cover
            if new_intro:
                intro_text = new_intro
            if new_year:
                scraped_year = new_year
            return cover_path, intro_text, scraped_year

        elif target_season >= 2:
            new_cover, new_intro, new_year = None, None, None
            if is_anime:
                new_cover, new_intro, new_year = self._season_specific_search_anibk(clean_base, target_season, valid_name)
            if not new_cover and not is_anime:
                new_cover, new_intro, new_year = self._season_specific_search_tmdb(clean_base, target_season, movie_data.get("is_series", False), valid_name)
            if not new_cover:
                new_cover, new_intro, new_year = self._s1_flow(clean_base, year, target_season, is_anime, valid_name, movie_data)

            if new_cover:
                cover_path = new_cover
            if new_intro:
                intro_text = new_intro
            if new_year:
                scraped_year = new_year
            return cover_path, intro_text, scraped_year

        elif target_season <= 1:
            new_cover, new_intro, new_year = self._s1_flow(clean_base, year, target_season, is_anime, valid_name, movie_data)
            if new_cover:
                cover_path = new_cover
            if new_intro:
                intro_text = new_intro
            if new_year:
                scraped_year = new_year
            return cover_path, intro_text, scraped_year

        return cover_path, intro_text, scraped_year