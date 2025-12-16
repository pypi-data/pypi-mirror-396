"""抖音视频解析 MCP 服务器"""

import os
import asyncio
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from dotenv import load_dotenv

from src.link_extractor import extract_douyin_link
from src.douyin_api import DouyinAPIClient, DouyinAPIError
from src.doubao_api import DoubaoAPIClient, DoubaoAPIError


# 加载环境变量
load_dotenv()

# 从环境变量获取配置
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
DOUBAO_API_ENDPOINT = os.getenv(
    "DOUBAO_API_ENDPOINT", 
    "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
)
DOUBAO_MODEL = os.getenv("DOUBAO_MODEL", "doubao-1.5-vision-pro-32k")

# 创建服务器实例
server = Server("douyin-video-analyzer")

# 初始化 API 客户端（延迟初始化）
douyin_client = DouyinAPIClient()
doubao_client = None


def get_doubao_client() -> DoubaoAPIClient:
    """获取豆包 API 客户端，如果没有初始化则进行初始化"""
    global doubao_client
    
    if doubao_client is None:
        if not DOUBAO_API_KEY:
            raise ValueError(
                "未设置豆包 API Key。请设置 DOUBAO_API_KEY 环境变量。"
            )
        
        doubao_client = DoubaoAPIClient(
            api_key=DOUBAO_API_KEY,
            api_endpoint=DOUBAO_API_ENDPOINT,
            model=DOUBAO_MODEL
        )
    
    return doubao_client


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    列出可用的工具
    """
    return [
        Tool(
            name="analyze_douyin_video",
            description=(
                "分析抖音视频内容。可以接收抖音口令或直接的抖音链接。"
                "自动提取链接、获取视频并使用 AI 进行详细分析，"
                "返回视频描述、大纲、教程步骤等结构化内容。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": (
                            "抖音口令或链接。例如：'0.05 09/23 III:/ e@B.tE 今年农户都不易啊... "
                            "https://v.douyin.com/DGHl69ciWp4/ 复制此链接...' 或直接 "
                            "'https://v.douyin.com/DGHl69ciWp4/'"
                        )
                    }
                },
                "required": ["text"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    处理工具调用
    """
    if name != "analyze_douyin_video":
        raise ValueError(f"未知工具: {name}")
    
    text = arguments.get("text", "")
    if not text:
        return [TextContent(
            type="text",
            text="错误：未提供文本内容"
        )]
    
    try:
        # 步骤 1: 提取抖音链接
        link = extract_douyin_link(text)
        if not link:
            return [TextContent(
                type="text",
                text=f"错误：无法从文本中提取抖音链接。\n\n输入的文本：{text}"
            )]
        
        result_parts = [f"✓ 成功提取链接: {link}\n"]
        
        # 步骤 2: 获取视频真实 URL
        try:
            video_url = await douyin_client.get_video_url(link)
            result_parts.append(f"✓ 成功获取视频 URL\n")
        except DouyinAPIError as e:
            return [TextContent(
                type="text",
                text=f"错误：获取视频 URL 失败\n\n{str(e)}"
            )]
        
        # 步骤 3: 使用豆包分析视频
        try:
            client = get_doubao_client()
            analysis = await client.analyze_video(video_url)
            result_parts.append(f"✓ 视频分析完成\n\n{'='*50}\n\n{analysis}")
            
            return [TextContent(
                type="text",
                text="\n".join(result_parts)
            )]
            
        except DoubaoAPIError as e:
            return [TextContent(
                type="text",
                text=f"错误：视频分析失败\n\n{str(e)}"
            )]
        except ValueError as e:
            return [TextContent(
                type="text",
                text=f"配置错误：{str(e)}"
            )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"未知错误：{str(e)}"
        )]


async def main():
    """启动 MCP 服务器"""
    # 使用 stdio 传输运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="douyin-video-analyzer",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())


