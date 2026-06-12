"""
服务器管理路由模块

提供数据源管理相关的 API 接口，包括：
1. 获取资源库列表
2. 添加数据源
3. 更新数据源
4. 删除数据源
5. 重扫数据源
6. 验证连接
7. 获取数据源类型
"""

from fastapi import APIRouter, HTTPException, Path, Query, Body, Form
from typing import Optional, List, Dict, Any

# 导入统一响应格式
from app.core.response import success, error

# 导入数据源服务
from app.services.source_service import source_service

# 创建路由实例
router = APIRouter(prefix="/api/sources", tags=["服务器管理"])


@router.get("", summary="获取资源库列表")
def list_sources() -> Dict[str, Any]:
    """
    获取所有已添加的数据源列表
    
    Returns:
        包含数据源列表的成功响应
    """
    sources = source_service.get_all_sources()
    return success(data=sources, message="获取成功")


@router.get("/types", summary="获取数据源类型选项")
def get_types() -> Dict[str, Any]:
    """
    获取支持的数据源类型列表
    
    Returns:
        包含类型选项和颜色选项的成功响应
    """
    types_config = source_service.get_source_types()
    return success(data=types_config, message="获取成功")


@router.post("/verify", summary="验证连接")
def verify_connection(
    source_data: Dict[str, Any] = Body(..., description="数据源配置")
) -> Dict[str, Any]:
    """
    验证数据源连接是否可用
    
    Args:
        source_data: 数据源配置对象，包含 type、host、path 等字段
    
    Returns:
        验证结果，包含连接是否有效
    """
    result = source_service.verify_connection(source_data)
    if result.get("valid"):
        return success(data=result, message=result.get("message"))
    else:
        return error(code=-1, message=result.get("message"), data=result)


@router.get("/{source_id}", summary="获取数据源详情")
def get_source(
    source_id: str = Path(..., description="数据源ID")
) -> Dict[str, Any]:
    """
    获取指定数据源的详细信息
    
    Args:
        source_id: 数据源ID
    
    Returns:
        数据源详情
    """
    source = source_service.get_source_by_id(source_id)
    if source is None:
        return error(code=404, message="数据源不存在")
    return success(data=source, message="获取成功")


@router.post("", summary="添加数据源")
def create_source(
    name: str = Form(..., description="数据源名称"),
    type: str = Form(..., description="数据源类型"),
    path: str = Form("", description="数据源路径"),
    username: Optional[str] = Form("", description="用户名"),
    password: Optional[str] = Form("", description="密码"),
    driver: Optional[str] = Form("", description="存储驱动"),
    cookie: Optional[str] = Form("", description="Cookie"),
    mount_path: Optional[str] = Form("", description="挂载路径")
) -> Dict[str, Any]:
    """
    添加新的数据源
    
    Args:
        name: 数据源名称
        type: 数据源类型 (openlist, WebDAV, 本地存储等)
        path: 数据源路径或地址
        username: 用户名（可选）
        password: 密码（可选）
        driver: 存储驱动（用于内置OpenList）
        cookie: Cookie（用于内置OpenList）
        mount_path: 挂载路径（用于内置OpenList）
    
    Returns:
        创建成功的数据源信息
    """
    # 参数验证
    if not name or not name.strip():
        return error(code=-1, message="数据源名称不能为空")
    
    if type == "WebDAV":
        if not path or not path.strip():
            return error(code=-1, message="WebDAV数据源路径不能为空")
        # 验证路径是否为有效URL
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(path)
            if not parsed.scheme or not parsed.hostname:
                return error(code=-1, message="WebDAV路径格式不正确，请输入完整的URL")
        except:
            return error(code=-1, message="WebDAV路径格式不正确")
    
    if type == "本地存储":
        if not path or not path.strip():
            return error(code=-1, message="本地存储路径不能为空")
    
    # 根据类型构建不同的路径
    if type == "openlist":
        full_path = f"{driver}://{mount_path}"
    elif type == "WebDAV":
        full_path = path
    else:
        full_path = path
    
    new_source = {
        "name": name,
        "type": type,
        "path": full_path,
        "username": username or "",
        "password": password or "",
        "driver": driver or "",
        "cookie": cookie or "",
        "mount_path": mount_path or "",
        "files": 0,
        "movies": 0,
        "series": 0,
        "anime": 0,
        "music": 0,
        "unmatched": 0,
        "active": False
    }
    
    result = source_service.add_source(new_source)
    return success(data=result, message="添加成功")


@router.put("/{source_id}", summary="更新数据源")
def update_source(
    source_id: str = Path(..., description="数据源ID"),
    name: Optional[str] = Form(default=None, description="数据源名称"),
    path: Optional[str] = Form(default=None, description="数据源路径"),
    username: Optional[str] = Form(default=None, description="用户名"),
    password: Optional[str] = Form(default=None, description="密码"),
    driver: Optional[str] = Form(default=None, description="存储驱动"),
    cookie: Optional[str] = Form(default=None, description="Cookie"),
    mount_path: Optional[str] = Form(default=None, description="挂载路径")
) -> Dict[str, Any]:
    """
    修改指定数据源的配置
    
    Args:
        source_id: 数据源ID
        name: 新的数据源名称（可选）
        path: 新的数据源路径（可选）
        username: 新的用户名（可选）
        password: 新的密码（可选）
        driver: 存储驱动（可选）
        cookie: Cookie（可选）
        mount_path: 挂载路径（可选）
    
    Returns:
        更新结果
    """
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if path is not None:
        update_data["path"] = path
    if username is not None:
        update_data["username"] = username
    if password is not None:
        update_data["password"] = password
    if driver is not None:
        update_data["driver"] = driver
    if cookie is not None:
        update_data["cookie"] = cookie
    if mount_path is not None:
        update_data["mount_path"] = mount_path
    
    result = source_service.update_source(source_id, update_data)
    if result is None:
        return error(code=404, message="数据源不存在")
    
    return success(data=result, message="更新成功")


@router.delete("/{source_id}", summary="删除数据源")
def remove_source(
    source_id: str = Path(..., description="数据源ID")
) -> Dict[str, Any]:
    """
    删除指定的数据源
    
    Args:
        source_id: 数据源ID
    
    Returns:
        删除结果
    """
    if not source_service.delete_source(source_id):
        return error(code=404, message="数据源不存在")
    
    return success(message="删除成功")


@router.post("/{source_id}/rescan", summary="重扫数据源")
def rescan_source(
    source_id: str = Path(..., description="数据源ID")
) -> Dict[str, Any]:
    """
    重新扫描指定数据源的文件（包含封面刮削）
    
    Args:
        source_id: 数据源ID
    
    Returns:
        扫描状态和结果
    """
    source = source_service.get_source_by_id(source_id)
    if source is None:
        return error(code=404, message="数据源不存在")
    
    result = source_service.rescan_source(source_id)
    if result.get("success"):
        return success(data={
            "source_id": result.get("source_id"),
            "message": result.get("message"),
            "total": result.get("total"),
            "movies": result.get("movies"),
            "series": result.get("series"),
            "anime": result.get("anime"),
            "total_episodes": result.get("total_episodes")
        }, message=result.get("message"))
    else:
        return error(code=-1, message=result.get("message"))


@router.post("/browse", summary="浏览目录")
def browse_directory(
    host: str = Form(..., description="主机地址"),
    port: Optional[str] = Form("", description="端口"),
    protocol: str = Form("http", description="协议"),
    username: Optional[str] = Form("", description="用户名"),
    password: Optional[str] = Form("", description="密码"),
    path: Optional[str] = Form("/", description="当前路径")
) -> Dict[str, Any]:
    """
    浏览 WebDAV 目录内容
    
    Args:
        host: 主机地址
        port: 端口（可选）
        protocol: 协议 (http/https)
        username: 用户名（可选）
        password: 密码（可选）
        path: 当前目录路径
    
    Returns:
        目录内容列表
    """
    import urllib.parse
    import base64
    
    # URL解码路径，处理中文路径
    decoded_path = urllib.parse.unquote(path) if path else "/"
    
    port_str = f":{port}" if port else ""
    base_url = f"{protocol}://{host}{port_str}"
    full_url = f"{base_url}{decoded_path}"
    
    headers = {"Content-Type": "application/xml", "Depth": "1"}
    
    if username and password:
        auth_str = f"{username}:{password}"
        auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        headers["Authorization"] = f"Basic {auth_b64}"
    
    try:
        import requests
        from xml.etree import ElementTree as ET
        
        propfind_body = """<?xml version="1.0" encoding="utf-8"?>
        <D:propfind xmlns:D="DAV:">
            <D:prop>
                <D:displayname/>
                <D:getcontenttype/>
                <D:resourcetype/>
                <D:getcontentlength/>
            </D:prop>
        </D:propfind>"""
        
        response = requests.request(
            "PROPFIND",
            full_url,
            headers=headers,
            data=propfind_body.encode("utf-8"),
            timeout=10
        )
        
        if response.status_code not in [200, 207]:
            return error(code=-1, message=f"连接失败: HTTP {response.status_code}")
        
        items = []
        try:
            root = ET.fromstring(response.content)
            namespaces = {"d": "DAV:"}
            
            for response_elem in root.findall(".//d:response", namespaces):
                href = response_elem.find("d:href", namespaces)
                propstat = response_elem.find("d:propstat/d:prop", namespaces)
                
                if href is not None and propstat is not None:
                    item_path = urllib.parse.unquote(href.text)
                    if item_path == urllib.parse.unquote(path):
                        continue
                    
                    resourcetype = propstat.find("d:resourcetype", namespaces)
                    is_dir = resourcetype is not None and resourcetype.find("d:collection", namespaces) is not None
                    
                    displayname = propstat.find("d:displayname", namespaces)
                    name = displayname.text if displayname is not None else item_path.split("/")[-1]
                    
                    content_length = propstat.find("d:getcontentlength", namespaces)
                    size = int(content_length.text) if content_length is not None and content_length.text else 0
                    
                    items.append({
                        "name": name,
                        "path": item_path,
                        "isDir": is_dir,
                        "size": size
                    })
        except ET.ParseError:
            return error(code=-1, message="无法解析目录列表")
        
        return success(data={
            "currentPath": path,
            "baseUrl": base_url,
            "items": sorted(items, key=lambda x: (not x["isDir"], x["name"].lower()))
        }, message="获取成功")
        
    except Exception as e:
        return error(code=-1, message=f"错误: {str(e)}")
