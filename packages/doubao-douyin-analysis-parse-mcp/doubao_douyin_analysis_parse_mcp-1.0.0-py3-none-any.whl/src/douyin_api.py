"""抖音视频解析 API 客户端"""

import httpx
from typing import Optional, Dict, Any


class DouyinAPIError(Exception):
    """抖音 API 调用错误"""
    pass


class DouyinAPIClient:
    """抖音视频解析 API 客户端"""
    
    def __init__(self, api_url: str = "http://175.24.234.153:8091"):
        """
        初始化抖音 API 客户端
        
        Args:
            api_url: API 服务器地址
        """
        self.api_url = api_url.rstrip('/')
        self.endpoint = f"{self.api_url}/api/hybrid/video_data"
        
    async def get_video_data(self, url: str) -> Dict[str, Any]:
        """
        获取视频数据
        
        Args:
            url: 抖音视频链接（加密或真实链接）
            
        Returns:
            包含视频信息的字典，包括真实视频 URL
            
        Raises:
            DouyinAPIError: API 调用失败时抛出
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.endpoint,
                    params={
                        "url": url,
                        "minimal": "false"
                    },
                    headers={
                        "accept": "application/json"
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data
                
        except httpx.HTTPStatusError as e:
            raise DouyinAPIError(
                f"抖音 API 返回错误状态码 {e.response.status_code}: {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise DouyinAPIError(
                f"抖音 API 请求失败: {str(e)}"
            ) from e
        except Exception as e:
            raise DouyinAPIError(
                f"解析抖音 API 响应时出错: {str(e)}"
            ) from e
    
    async def get_video_url(self, url: str) -> Optional[str]:
        """
        从加密链接获取真实视频 URL
        
        根据返回的 JSON 结构，从 data.video.bit_rate 数组中选择
        bit_rate 最小的对象，然后获取其 play_addr.url_list[0]
        
        Args:
            url: 抖音视频链接（加密或真实链接）
            
        Returns:
            真实视频 URL，如果获取失败返回 None
            
        Raises:
            DouyinAPIError: API 调用失败时抛出
        """
        response = await self.get_video_data(url)
        
        # 检查响应码
        if response.get("code") != 200:
            raise DouyinAPIError(
                f"抖音 API 返回错误码: {response.get('code')}"
            )
        
        # 获取 data 字段
        data = response.get("data")
        if not data:
            raise DouyinAPIError("API 响应中缺少 data 字段")
        
        # 获取 video 字段
        video = data.get("video")
        if not video:
            raise DouyinAPIError("API 响应中缺少 video 字段")
        
        # 获取 bit_rate 数组
        bit_rate_list = video.get("bit_rate")
        if not bit_rate_list or not isinstance(bit_rate_list, list) or len(bit_rate_list) == 0:
            raise DouyinAPIError("API 响应中 bit_rate 数组为空或不存在")
        
        # 找到 bit_rate 最小的对象
        min_bitrate_item = min(bit_rate_list, key=lambda x: x.get("bit_rate", float('inf')))
        
        # 获取 play_addr.url_list[0]
        play_addr = min_bitrate_item.get("play_addr")
        if not play_addr:
            raise DouyinAPIError("最小码率视频缺少 play_addr 字段")
        
        url_list = play_addr.get("url_list")
        if not url_list or not isinstance(url_list, list) or len(url_list) == 0:
            raise DouyinAPIError("play_addr.url_list 为空")
        
        video_url = url_list[0]
        
        if not video_url:
            raise DouyinAPIError("无法获取视频 URL")
        
        return video_url
    
    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        获取完整的视频信息（包括作者、标题、时长等）
        
        Args:
            url: 抖音视频链接（加密或真实链接）
            
        Returns:
            包含视频详细信息的字典
            
        Raises:
            DouyinAPIError: API 调用失败时抛出
        """
        response = await self.get_video_data(url)
        
        # 检查响应码
        if response.get("code") != 200:
            raise DouyinAPIError(
                f"抖音 API 返回错误码: {response.get('code')}"
            )
        
        data = response.get("data", {})
        video = data.get("video", {})
        author = data.get("author", {})
        
        # 提取关键信息
        info = {
            "video_url": await self.get_video_url(url),
            "duration": video.get("duration", 0) / 1000,  # 转换为秒
            "width": video.get("width", 0),
            "height": video.get("height", 0),
            "author_name": author.get("nickname", ""),
            "author_uid": author.get("uid", ""),
            "author_signature": author.get("signature", ""),
            "cover_url": video.get("cover", {}).get("url_list", [None])[0],
        }
        
        return info

