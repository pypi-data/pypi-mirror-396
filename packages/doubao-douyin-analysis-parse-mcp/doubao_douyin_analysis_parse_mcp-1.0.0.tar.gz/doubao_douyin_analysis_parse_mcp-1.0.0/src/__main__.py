"""允许使用 python -m src 运行服务器"""

from src.douyin_mcp_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())


