"""
数据模型定义
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from enum import Enum
import time


class GenerationStyle(Enum):
    """生成风格枚举"""
    DEFAULT = "default"
    CLASSIC = "classic"
    WIZARD_GREEN = "wizard_green"
    MINIMAL = "minimal"


@dataclass
class GenerationResult:
    """生成结果"""
    html: str
    assets: Dict[str, bytes] = field(default_factory=dict)
    model: str = ""
    prompt: str = ""
    generation_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """是否生成成功"""
        return bool(self.html) and not self.errors


@dataclass
class PageMetadata:
    """页面元数据"""
    page_id: str
    prompt: str
    style: str
    created_at: float = field(default_factory=time.time)
    output_path: str = ""
    deployed_url: Optional[str] = None
    model: str = ""
    generation_time: float = 0.0


@dataclass
class PostProcessorResult:
    """后处理结果"""
    html: str
    fixes_applied: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def had_fixes(self) -> bool:
        """是否应用了修复"""
        return len(self.fixes_applied) > 0


@dataclass
class ImageAsset:
    """图片资源"""
    url: str
    query: str
    is_generated: bool = False
    base64_data: Optional[str] = None
    error: Optional[str] = None
