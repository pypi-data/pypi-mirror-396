"""豆包视频理解 API 客户端"""

import httpx
from typing import Optional, Dict, Any
from src.prompts import get_video_analysis_prompt


class DoubaoAPIError(Exception):
    """豆包 API 调用错误"""
    pass


class DoubaoAPIClient:
    """豆包视频理解 API 客户端"""
    
    def __init__(
        self, 
        api_key: str,
        api_endpoint: str = "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        model: str = "doubao-1.5-vision-pro-32k"
    ):
        """
        初始化豆包 API 客户端
        
        Args:
            api_key: 豆包 API 密钥
            api_endpoint: API 端点地址
            model: 使用的模型名称
        """
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.model = model
        
    async def analyze_video(self, video_url: str) -> str:
        """
        分析视频内容
        
        Args:
            video_url: 视频的真实 URL
            
        Returns:
            AI 生成的结构化视频分析结果
            
        Raises:
            DoubaoAPIError: API 调用失败时抛出
        """
        try:
            # 构建请求数据
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "video_url",
                                "video_url": {
                                    "url": video_url
                                }
                            },
                            {
                                "type": "text",
                                "text": get_video_analysis_prompt()
                            }
                        ]
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.api_endpoint,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                # 提取 AI 生成的内容
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
                
                raise DoubaoAPIError(
                    f"无法从豆包 API 响应中提取内容。响应数据: {data}"
                )
                
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = f": {error_data}"
            except:
                error_detail = f": {e.response.text}"
            
            raise DoubaoAPIError(
                f"豆包 API 返回错误状态码 {e.response.status_code}{error_detail}"
            ) from e
        except httpx.RequestError as e:
            raise DoubaoAPIError(
                f"豆包 API 请求失败: {str(e)}"
            ) from e
        except Exception as e:
            raise DoubaoAPIError(
                f"调用豆包 API 时出错: {str(e)}"
            ) from e
    
    async def analyze_video_with_custom_prompt(
        self, 
        video_url: str, 
        custom_prompt: str
    ) -> str:
        """
        使用自定义提示词分析视频内容
        
        Args:
            video_url: 视频的真实 URL
            custom_prompt: 自定义的提示词
            
        Returns:
            AI 生成的视频分析结果
            
        Raises:
            DoubaoAPIError: API 调用失败时抛出
        """
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "video_url",
                                "video_url": {
                                    "url": video_url
                                }
                            },
                            {
                                "type": "text",
                                "text": custom_prompt
                            }
                        ]
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.api_endpoint,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
                
                raise DoubaoAPIError(
                    f"无法从豆包 API 响应中提取内容。响应数据: {data}"
                )
                
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = f": {error_data}"
            except:
                error_detail = f": {e.response.text}"
            
            raise DoubaoAPIError(
                f"豆包 API 返回错误状态码 {e.response.status_code}{error_detail}"
            ) from e
        except httpx.RequestError as e:
            raise DoubaoAPIError(
                f"豆包 API 请求失败: {str(e)}"
            ) from e
        except Exception as e:
            raise DoubaoAPIError(
                f"调用豆包 API 时出错: {str(e)}"
            ) from e


