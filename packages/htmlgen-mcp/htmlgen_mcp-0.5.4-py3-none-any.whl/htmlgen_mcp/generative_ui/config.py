"""
Gemini API 配置模块

支持的环境变量:
- GOOGLE_API_KEY: Google AI API 密钥
- GENERATIVE_UI_BASE_URL: API 基础地址 (可选，用于代理或自定义端点)
- GENERATIVE_UI_MODEL: 使用的模型名称 (默认: gemini-2.0-flash-exp)
- GENERATIVE_UI_FALLBACK_MODEL: 备用模型 (默认: gemini-1.5-flash)
"""

import os
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class GeminiConfig:
    """Gemini API 配置"""
    
    # API 配置
    api_key: str
    base_url: Optional[str] = None  # 自定义 API 端点
    
    # 模型配置
    primary_model: str = "gemini-3-pro-preview-11-2025"
    fallback_model: str = "gemini-2.5-pro"
    
    # 重试配置
    max_retries: int = 3
    retry_delays: tuple = (1, 2, 4)  # 指数退避延迟（秒）
    
    # 生成配置
    temperature: float = 0.7
    max_output_tokens: int = 1024
    
    @classmethod
    def from_env(cls) -> "GeminiConfig":
        """从环境变量创建配置"""
        api_key = os.getenv("GOOGLE_API_KEY", "")
        base_url = os.getenv("GENERATIVE_UI_BASE_URL") or os.getenv("GOOGLE_API_BASE_URL")
        
        return cls(
            api_key=api_key,
            base_url=base_url,
            primary_model=os.getenv("GENERATIVE_UI_MODEL", "gemini-3-pro-preview-11-2025"),
            fallback_model=os.getenv("GENERATIVE_UI_FALLBACK_MODEL", "gemini-2.5-pro"),
            max_retries=int(os.getenv("GENERATIVE_UI_MAX_RETRIES", "3")),
            temperature=float(os.getenv("GENERATIVE_UI_TEMPERATURE", "0.7")),
            max_output_tokens=int(os.getenv("GENERATIVE_UI_MAX_TOKENS", "8192")),
        )
    
    @property
    def is_configured(self) -> bool:
        """检查是否已配置 API Key"""
        return bool(self.api_key)
    
    def get_model_list(self) -> List[str]:
        """获取模型列表（按优先级排序）"""
        models = [self.primary_model]
        if self.fallback_model and self.fallback_model != self.primary_model:
            models.append(self.fallback_model)
        return models


# 支持的模型列表
SUPPORTED_MODELS = [
    "gemini-3-pro-preview-11-2025",
    "gemini-2.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]


def get_config() -> GeminiConfig:
    """获取全局配置实例"""
    return GeminiConfig.from_env()


def validate_model(model: str) -> bool:
    """验证模型名称是否支持"""
    return model in SUPPORTED_MODELS or model.startswith("gemini-")
