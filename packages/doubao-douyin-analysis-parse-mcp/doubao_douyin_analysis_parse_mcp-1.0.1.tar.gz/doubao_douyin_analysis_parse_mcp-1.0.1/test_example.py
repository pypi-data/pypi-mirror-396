"""
测试示例 - 用于验证抖音 API 解析功能

使用方法：
1. 确保已安装依赖：pip install -e .
2. 设置环境变量或创建 .env 文件
3. 运行：python test_example.py
"""

import asyncio
from src.link_extractor import extract_douyin_link
from src.douyin_api import DouyinAPIClient


async def test_link_extraction():
    """测试链接提取功能"""
    print("=" * 60)
    print("测试 1: 链接提取功能")
    print("=" * 60)
    
    # 测试完整口令
    text1 = "0.05 09/23 III:/ e@B.tE 今年农户都不易啊 https://v.douyin.com/DGHl69ciWp4/ 复制此链接"
    link1 = extract_douyin_link(text1)
    print(f"✓ 口令文本提取成功：{link1}")
    
    # 测试纯链接
    text2 = "https://v.douyin.com/DGHl69ciWp4/"
    link2 = extract_douyin_link(text2)
    print(f"✓ 纯链接提取成功：{link2}")
    
    print()


async def test_video_url_extraction():
    """测试视频 URL 提取功能"""
    print("=" * 60)
    print("测试 2: 视频 URL 提取功能")
    print("=" * 60)
    
    # 使用测试链接（请替换为实际的抖音链接）
    test_url = "https://v.douyin.com/DGHl69ciWp4/"
    
    client = DouyinAPIClient()
    
    try:
        print(f"正在解析链接: {test_url}")
        video_url = await client.get_video_url(test_url)
        print(f"✓ 视频 URL 获取成功")
        print(f"  视频地址: {video_url[:80]}...")
        print()
        
        # 获取完整视频信息
        print("正在获取完整视频信息...")
        video_info = await client.get_video_info(test_url)
        print(f"✓ 视频信息获取成功")
        print(f"  时长: {video_info['duration']:.1f} 秒")
        print(f"  尺寸: {video_info['width']}x{video_info['height']}")
        print(f"  作者: {video_info['author_name']}")
        print(f"  签名: {video_info['author_signature'][:50]}...")
        print()
        
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        print()


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("抖音视频解析测试")
    print("=" * 60)
    print()
    
    # 测试 1: 链接提取
    await test_link_extraction()
    
    # 测试 2: 视频 URL 提取
    print("⚠️  注意: 测试 2 需要实际的抖音链接和网络连接")
    user_input = input("是否继续测试视频 URL 提取功能? (y/n): ")
    if user_input.lower() == 'y':
        await test_video_url_extraction()
    else:
        print("跳过视频 URL 提取测试")
    
    print()
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


