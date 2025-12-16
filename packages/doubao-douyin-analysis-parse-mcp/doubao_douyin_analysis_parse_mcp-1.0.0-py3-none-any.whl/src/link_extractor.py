"""从抖音口令或文本中提取视频链接"""

import re
from typing import Optional


def extract_douyin_link(text: str) -> Optional[str]:
    """
    从文本中提取抖音视频链接
    
    支持的格式：
    - https://v.douyin.com/xxx/
    - http://v.douyin.com/xxx/
    - https://www.douyin.com/xxx
    
    Args:
        text: 包含抖音链接的文本（可能是口令）
        
    Returns:
        提取到的链接，如果未找到返回 None
        
    Example:
        >>> text = "0.05 09/23 III:/ e@B.tE 今年农户都不易啊 https://v.douyin.com/DGHl69ciWp4/ 复制此链接..."
        >>> extract_douyin_link(text)
        'https://v.douyin.com/DGHl69ciWp4/'
    """
    # 正则表达式匹配抖音链接
    # 支持 v.douyin.com 和 www.douyin.com
    pattern = r'https?://(?:v\.|www\.)?douyin\.com/[A-Za-z0-9]+/?'
    
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    
    return None


def is_douyin_link(text: str) -> bool:
    """
    判断文本是否是抖音链接
    
    Args:
        text: 要判断的文本
        
    Returns:
        如果是抖音链接返回 True，否则返回 False
    """
    return extract_douyin_link(text) is not None


