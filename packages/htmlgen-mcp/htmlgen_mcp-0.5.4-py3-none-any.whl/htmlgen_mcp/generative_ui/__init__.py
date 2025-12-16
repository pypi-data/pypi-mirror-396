"""
Generative UI Module - 基于 Google Research 论文的交互式网页生成

核心组件:
- GenerativeUIAgent: 单次生成完整交互式 HTML 页面
- SystemPromptBuilder: 构建精心设计的 System Prompt
- ToolEndpointsService: 图片搜索/生成等工具端点
- PostProcessorPipeline: 后处理修复管道
"""

from .agent import GenerativeUIAgent
from .models import GenerationResult, GenerationStyle, PageMetadata

__all__ = [
    "GenerativeUIAgent",
    "GenerationResult",
    "GenerationStyle",
    "PageMetadata",
]
