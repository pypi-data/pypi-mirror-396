"""
ToolEndpointsService - 提供图片搜索、图片生成等工具端点
"""

import re
import urllib.parse
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ImageRef:
    """图片引用"""
    original_src: str
    query: str
    is_generated: bool
    aspect: str = "1:1"


class ToolEndpointsService:
    """提供图片搜索、图片生成等工具端点"""
    
    # Pollinations API 端点
    POLLINATIONS_IMAGE_URL = "https://image.pollinations.ai/prompt/{prompt}"
    POLLINATIONS_SEARCH_URL = "https://image.pollinations.ai/prompt/{query}"
    
    def __init__(
        self,
        enable_search: bool = True,
        enable_image_gen: bool = True,
    ):
        self.enable_search = enable_search
        self.enable_image_gen = enable_image_gen
    
    async def resolve_assets(self, html_content: str) -> Dict[str, str]:
        """
        解析 HTML 中的资源引用并获取实际 URL
        
        Args:
            html_content: HTML 内容
            
        Returns:
            Dict[原始引用, 实际URL]
        """
        assets = {}
        image_refs = self._extract_image_refs(html_content)
        
        for ref in image_refs:
            if ref.is_generated:
                url = await self._generate_image(ref.query, ref.aspect)
            else:
                url = await self._search_image(ref.query)
            assets[ref.original_src] = url
        
        return assets
    
    def resolve_html(self, html_content: str) -> str:
        """
        将 HTML 中的 /image 和 /gen 引用替换为实际 URL
        
        Args:
            html_content: 原始 HTML
            
        Returns:
            替换后的 HTML
        """
        # 替换 /gen?prompt=xxx
        def replace_gen(match):
            src = match.group(1)
            params = self._parse_params(src)
            prompt = params.get("prompt", "placeholder")
            aspect = params.get("aspect", "1:1")
            return f'src="{self._get_gen_url(prompt, aspect)}"'
        
        html_content = re.sub(
            r'src="(/gen\?[^"]+)"',
            replace_gen,
            html_content
        )
        
        # 替换 /image?query=xxx
        def replace_image(match):
            src = match.group(1)
            params = self._parse_params(src)
            query = params.get("query", "placeholder")
            return f'src="{self._get_search_url(query)}"'
        
        html_content = re.sub(
            r'src="(/image\?[^"]+)"',
            replace_image,
            html_content
        )
        
        return html_content

    def _extract_image_refs(self, html_content: str) -> List[ImageRef]:
        """提取 HTML 中的图片引用"""
        refs = []
        
        # 匹配 /gen?prompt=xxx
        gen_pattern = r'src="(/gen\?[^"]+)"'
        for match in re.finditer(gen_pattern, html_content):
            src = match.group(1)
            params = self._parse_params(src)
            refs.append(ImageRef(
                original_src=src,
                query=params.get("prompt", ""),
                is_generated=True,
                aspect=params.get("aspect", "1:1"),
            ))
        
        # 匹配 /image?query=xxx
        image_pattern = r'src="(/image\?[^"]+)"'
        for match in re.finditer(image_pattern, html_content):
            src = match.group(1)
            params = self._parse_params(src)
            refs.append(ImageRef(
                original_src=src,
                query=params.get("query", ""),
                is_generated=False,
            ))
        
        return refs
    
    def _parse_params(self, url: str) -> Dict[str, str]:
        """解析 URL 参数"""
        if "?" not in url:
            return {}
        query_string = url.split("?", 1)[1]
        params = {}
        for part in query_string.split("&"):
            if "=" in part:
                key, value = part.split("=", 1)
                params[key] = urllib.parse.unquote(value)
        return params
    
    async def _search_image(self, query: str) -> str:
        """搜索图片，返回 URL"""
        encoded = urllib.parse.quote(query)
        return self.POLLINATIONS_SEARCH_URL.format(query=encoded)
    
    async def _generate_image(self, prompt: str, aspect: str = "1:1") -> str:
        """生成图片，返回 URL"""
        encoded = urllib.parse.quote(prompt)
        base_url = self.POLLINATIONS_IMAGE_URL.format(prompt=encoded)
        
        # 添加宽高参数
        width, height = self._aspect_to_dimensions(aspect)
        return f"{base_url}?width={width}&height={height}"
    
    def _get_gen_url(self, prompt: str, aspect: str = "1:1") -> str:
        """同步获取生成图片 URL"""
        encoded = urllib.parse.quote(prompt)
        base_url = self.POLLINATIONS_IMAGE_URL.format(prompt=encoded)
        width, height = self._aspect_to_dimensions(aspect)
        return f"{base_url}?width={width}&height={height}"
    
    def _get_search_url(self, query: str) -> str:
        """同步获取搜索图片 URL"""
        encoded = urllib.parse.quote(query)
        return self.POLLINATIONS_SEARCH_URL.format(query=encoded)
    
    def _aspect_to_dimensions(self, aspect: str) -> tuple:
        """将宽高比转换为像素尺寸"""
        aspects = {
            "1:1": (512, 512),
            "3:4": (384, 512),
            "4:3": (512, 384),
            "9:16": (288, 512),
            "16:9": (512, 288),
        }
        return aspects.get(aspect, (512, 512))
    
    def get_endpoint_docs(self) -> str:
        """返回端点使用文档"""
        return """
**Image Endpoints:**
1. /image?query=URL_ENCODED_QUERY - Search for real images
2. /gen?prompt=URL_ENCODED_PROMPT&aspect=RATIO - Generate AI images
   Supported aspects: 1:1, 3:4, 4:3, 9:16, 16:9
"""
