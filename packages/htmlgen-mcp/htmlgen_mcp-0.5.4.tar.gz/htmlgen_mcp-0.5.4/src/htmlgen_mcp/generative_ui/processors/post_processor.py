"""
PostProcessorPipeline - 后处理管道，修复常见生成错误
"""

import os
import re
from typing import List, Protocol
from ..models import PostProcessorResult


class PostProcessor(Protocol):
    """后处理器接口"""
    async def process(self, html: str) -> tuple[str, List[str]]:
        """处理 HTML，返回 (处理后的HTML, 应用的修复列表)"""
        ...


class HTMLStructureValidator:
    """验证并修复 HTML 结构"""
    
    async def process(self, html: str) -> tuple[str, List[str]]:
        fixes = []
        
        # 确保有 DOCTYPE
        if "<!DOCTYPE" not in html.upper():
            html = "<!DOCTYPE html>\n" + html
            fixes.append("Added DOCTYPE")
        
        # 确保有 <html> 标签
        if "<html" not in html.lower():
            html = html.replace("<!DOCTYPE html>", '<!DOCTYPE html>\n<html lang="zh-CN">')
            html += "\n</html>"
            fixes.append("Added html tags")
        
        # 确保有 <head> 标签
        if "<head>" not in html.lower():
            html = re.sub(
                r'(<html[^>]*>)',
                r'\1\n<head>\n<meta charset="UTF-8">\n</head>',
                html,
                flags=re.IGNORECASE
            )
            fixes.append("Added head tag")
        
        # 确保有 <body> 标签
        if "<body" not in html.lower():
            html = re.sub(
                r'(</head>)',
                r'\1\n<body>',
                html,
                flags=re.IGNORECASE
            )
            if "</body>" not in html.lower():
                html = re.sub(r'(</html>)', r'</body>\n\1', html, flags=re.IGNORECASE)
            fixes.append("Added body tag")
        
        # 确保有 viewport meta
        if 'viewport' not in html.lower():
            html = re.sub(
                r'(<head[^>]*>)',
                r'\1\n<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                html,
                flags=re.IGNORECASE
            )
            fixes.append("Added viewport meta")
        
        return html, fixes


class TailwindFixer:
    """修复 Tailwind CSS 相关问题"""
    
    TAILWIND_CDN = '<script src="https://cdn.tailwindcss.com"></script>'
    
    async def process(self, html: str) -> tuple[str, List[str]]:
        fixes = []
        
        if "cdn.tailwindcss.com" not in html:
            html = re.sub(
                r'(<head[^>]*>)',
                rf'\1\n{self.TAILWIND_CDN}',
                html,
                flags=re.IGNORECASE
            )
            fixes.append("Added Tailwind CDN")
        
        return html, fixes


class JavaScriptErrorFixer:
    """修复常见 JavaScript 错误"""
    
    async def process(self, html: str) -> tuple[str, List[str]]:
        fixes = []
        
        # 提取所有 script 标签内容进行检查
        script_pattern = r'(<script[^>]*>)([\s\S]*?)(</script>)'
        
        def fix_script(match):
            nonlocal fixes
            open_tag, content, close_tag = match.groups()
            original = content
            
            # 跳过外部脚本
            if 'src=' in open_tag:
                return match.group(0)
            
            # 修复常见问题
            # 1. 确保有错误处理
            if 'window.onerror' not in content and len(content.strip()) > 50:
                error_handler = '''
window.onerror = function(msg, url, line) {
    console.error('Error:', msg, 'at line', line);
    return false;
};
'''
                content = error_handler + content
                fixes.append("Added error handler")
            
            return open_tag + content + close_tag
        
        html = re.sub(script_pattern, fix_script, html, flags=re.IGNORECASE)
        return html, fixes


class CharacterEscaper:
    """转义特殊字符"""
    
    async def process(self, html: str) -> tuple[str, List[str]]:
        fixes = []
        
        # 修复属性中的未转义引号（简单处理）
        # 这里只做基本检查，避免破坏正常内容
        
        return html, fixes


class APIKeyInjector:
    """注入 API 密钥"""
    
    PLACEHOLDERS = [
        ("YOUR_API_KEY", "GOOGLE_MAPS_API_KEY"),
        ("YOUR_GOOGLE_MAPS_KEY", "GOOGLE_MAPS_API_KEY"),
        ("YOUR_MAPBOX_TOKEN", "MAPBOX_ACCESS_TOKEN"),
    ]
    
    async def process(self, html: str) -> tuple[str, List[str]]:
        fixes = []
        
        for placeholder, env_var in self.PLACEHOLDERS:
            if placeholder in html:
                api_key = os.getenv(env_var, "")
                if api_key:
                    html = html.replace(placeholder, api_key)
                    fixes.append(f"Injected {env_var}")
        
        return html, fixes


class PostProcessorPipeline:
    """后处理管道，依次执行所有后处理器"""
    
    def __init__(self):
        self.processors = [
            HTMLStructureValidator(),
            TailwindFixer(),
            JavaScriptErrorFixer(),
            CharacterEscaper(),
            APIKeyInjector(),
        ]
    
    async def process(self, html_content: str) -> PostProcessorResult:
        """
        依次执行所有后处理器
        
        Args:
            html_content: 原始 HTML
            
        Returns:
            PostProcessorResult 包含处理后的 HTML 和修复记录
        """
        all_fixes = []
        all_warnings = []
        
        for processor in self.processors:
            try:
                html_content, fixes = await processor.process(html_content)
                all_fixes.extend(fixes)
            except Exception as e:
                all_warnings.append(f"{processor.__class__.__name__} error: {str(e)}")
        
        return PostProcessorResult(
            html=html_content,
            fixes_applied=all_fixes,
            warnings=all_warnings,
        )


# ============================================================================
# 质量验证器 (Phase 6)
# ============================================================================

class ResponsiveDesignValidator:
    """验证响应式设计"""
    
    RESPONSIVE_CLASSES = ['sm:', 'md:', 'lg:', 'xl:', '2xl:']
    
    async def process(self, html: str) -> tuple[str, List[str]]:
        fixes = []
        warnings = []
        
        # 检查 viewport meta
        if 'viewport' not in html.lower():
            html = re.sub(
                r'(<head[^>]*>)',
                r'\1\n<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                html,
                flags=re.IGNORECASE
            )
            fixes.append("Added viewport meta tag")
        
        # 检查是否有响应式类
        has_responsive = any(cls in html for cls in self.RESPONSIVE_CLASSES)
        if not has_responsive:
            warnings.append("No responsive Tailwind classes found (sm:, md:, lg:, xl:)")
        
        return html, fixes


class PlaceholderContentDetector:
    """检测占位内容"""
    
    PLACEHOLDER_PATTERNS = [
        r'lorem\s+ipsum',
        r'\bTODO\b',
        r'\bplaceholder\b',
        r'example\.com',
        r'your[_\s]?name',
        r'your[_\s]?email',
        r'xxx+',
        r'sample\s+text',
    ]
    
    async def process(self, html: str) -> tuple[str, List[str]]:
        warnings = []
        
        for pattern in self.PLACEHOLDER_PATTERNS:
            if re.search(pattern, html, re.IGNORECASE):
                warnings.append(f"Possible placeholder content detected: {pattern}")
        
        return html, warnings


class ErrorLoggingInjector:
    """注入错误日志代码"""
    
    ERROR_HANDLER = '''
<script>
// Error logging injected by Generative UI
window.onerror = function(msg, url, line, col, error) {
    console.error('[GenUI Error]', msg, 'at', url, ':', line);
    return false;
};
window.addEventListener('unhandledrejection', function(event) {
    console.error('[GenUI Promise Error]', event.reason);
});
</script>
'''
    
    async def process(self, html: str) -> tuple[str, List[str]]:
        fixes = []
        
        # 检查是否已有错误处理
        if 'window.onerror' not in html:
            # 在 </body> 前注入
            if '</body>' in html.lower():
                html = re.sub(
                    r'(</body>)',
                    self.ERROR_HANDLER + r'\n\1',
                    html,
                    flags=re.IGNORECASE
                )
                fixes.append("Injected error logging handler")
        
        return html, fixes


class QualityValidatorPipeline:
    """质量验证管道"""
    
    def __init__(self):
        self.validators = [
            ResponsiveDesignValidator(),
            PlaceholderContentDetector(),
            ErrorLoggingInjector(),
        ]
    
    async def validate(self, html: str) -> PostProcessorResult:
        """执行所有质量验证"""
        all_fixes = []
        all_warnings = []
        
        for validator in self.validators:
            try:
                html, result = await validator.process(html)
                if isinstance(result, list):
                    # 区分 fixes 和 warnings
                    if hasattr(validator, 'PLACEHOLDER_PATTERNS'):
                        all_warnings.extend(result)
                    else:
                        all_fixes.extend(result)
            except Exception as e:
                all_warnings.append(f"{validator.__class__.__name__} error: {str(e)}")
        
        return PostProcessorResult(
            html=html,
            fixes_applied=all_fixes,
            warnings=all_warnings,
        )
