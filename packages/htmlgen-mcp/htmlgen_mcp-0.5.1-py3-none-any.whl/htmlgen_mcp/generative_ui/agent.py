"""
GenerativeUIAgent - 基于 Generative UI 论文的单次生成 Agent

核心思想：通过精心设计的 System Prompt，让 LLM 一次性生成完整的交互式 HTML 页面。
支持 yunwu.ai 等 Gemini API 代理服务。
"""

from __future__ import annotations

import os
import re
import time
import asyncio
import aiohttp
import json
from typing import Optional, AsyncIterator, Dict, Any

from .models import GenerationResult, GenerationStyle
from .prompts.system_prompt_builder import SystemPromptBuilder
from .tools.endpoints_service import ToolEndpointsService
from .processors.post_processor import PostProcessorPipeline


class GenerativeUIAgent:
    """基于 Generative UI 论文的单次生成 Agent"""
    
    # 支持的模型列表（按优先级排序）
    SUPPORTED_MODELS = [
        "gemini-3-pro-preview-11-2025",  # Gemini 3 Pro Preview
        "gemini-2.5-pro",                # Gemini 2.5 Pro
        "gemini-2.0-flash-exp",          # Gemini 2.0 Flash
        "gemini-1.5-pro",                # Gemini 1.5 Pro
    ]
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # 指数退避
    
    def __init__(
        self,
        model: Optional[str] = None,
        style: str = "default",
        enable_search: bool = True,
        enable_image_gen: bool = True,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        enable_fallback: bool = True,
    ):
        """
        初始化 GenerativeUIAgent
        
        Args:
            model: 使用的模型名称，默认从环境变量读取
            style: 生成风格 (default/classic/wizard_green/minimal)
            enable_search: 是否启用搜索功能
            enable_image_gen: 是否启用图片生成
            api_key: Google API Key，默认从环境变量读取
            base_url: API 基础地址，默认从环境变量读取（用于代理或自定义端点）
            enable_fallback: 是否启用模型回退
        """
        self.model = model or os.getenv("GENERATIVE_UI_MODEL", "gemini-3-pro-preview-11-2025")
        self.fallback_model = os.getenv("GENERATIVE_UI_FALLBACK_MODEL", "gemini-2.5-pro")
        self.enable_fallback = enable_fallback
        self.style = GenerationStyle(style) if isinstance(style, str) else style
        self.enable_search = enable_search
        self.enable_image_gen = enable_image_gen
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.base_url = base_url or os.getenv("GENERATIVE_UI_BASE_URL") or os.getenv("GOOGLE_API_BASE_URL")
        
        # 初始化组件
        self.prompt_builder = SystemPromptBuilder(style=self.style.value)
        self.tool_service = ToolEndpointsService(
            enable_search=enable_search,
            enable_image_gen=enable_image_gen,
        )
        self.post_processor = PostProcessorPipeline()
        
        # 初始化 Gemini 客户端
        self.client = self._init_client()
        self._current_model = self.model  # 跟踪当前使用的模型
    
    def _init_client(self):
        """初始化客户端 - 使用 REST API 模式"""
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY not set, using mock mode")
            return None
        
        # 使用 REST API 模式，返回 True 表示已配置
        return True
    
    async def generate(self, user_prompt: str) -> GenerationResult:
        """
        单次生成完整的交互式 HTML 页面
        
        Args:
            user_prompt: 用户需求描述
            
        Returns:
            GenerationResult 包含生成的 HTML 和资源
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        # 1. 构建完整的 system prompt
        system_prompt = self.prompt_builder.build()
        
        # 2. 调用模型生成 HTML
        html_content = ""
        for attempt in range(self.MAX_RETRIES):
            try:
                html_content = await self._call_model(system_prompt, user_prompt)
                if html_content:
                    break
            except Exception as e:
                errors.append(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAYS[attempt])
        
        if not html_content:
            return GenerationResult(
                html="",
                model=self.model,
                prompt=user_prompt,
                generation_time=time.time() - start_time,
                errors=errors or ["Failed to generate HTML after all retries"],
            )
        
        # 3. 提取 HTML 代码
        raw_response = html_content  # 保存原始响应用于调试
        html_content = self._extract_html(html_content)
        
        # 检查提取后的 HTML 是否有实际内容
        if not html_content or len(html_content.strip()) < 100:
            # HTML 内容过短或为空，可能是提取失败
            errors.append(f"HTML extraction failed or content too short (length={len(html_content)})")
            errors.append(f"Raw response preview: {raw_response[:500]}...")
            return GenerationResult(
                html="",
                model=self._current_model,
                prompt=user_prompt,
                generation_time=time.time() - start_time,
                errors=errors,
            )
        
        # 4. 后处理修复
        post_result = await self.post_processor.process(html_content)
        html_content = post_result.html
        if post_result.fixes_applied:
            warnings.extend([f"Fixed: {fix}" for fix in post_result.fixes_applied])
        warnings.extend(post_result.warnings)
        
        # 5. 处理图片资源
        assets = {}
        if self.enable_image_gen:
            try:
                assets = await self.tool_service.resolve_assets(html_content)
            except Exception as e:
                warnings.append(f"Asset resolution warning: {str(e)}")
        
        return GenerationResult(
            html=html_content,
            assets=assets,
            model=self._current_model,  # 使用实际调用的模型
            prompt=user_prompt,
            generation_time=time.time() - start_time,
            errors=errors,
            warnings=warnings,
        )
    
    async def generate_stream(self, user_prompt: str) -> AsyncIterator[str]:
        """
        流式生成，支持渐进式渲染
        
        Args:
            user_prompt: 用户需求描述
            
        Yields:
            HTML 内容片段
        """
        system_prompt = self.prompt_builder.build()
        
        if not self.client:
            yield "<!-- Error: API not configured -->"
            return
        
        # 构建流式 API URL
        base = self.base_url.rstrip("/") if self.base_url else "https://generativelanguage.googleapis.com"
        url = f"{base}/v1beta/models/{self.model}:streamGenerateContent"
        
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        yield f"<!-- Error: API returned {resp.status} -->"
                        return
                    
                    buffer = ""
                    in_html = False
                    
                    async for line in resp.content:
                        try:
                            text = line.decode("utf-8").strip()
                            if not text or text.startswith("data:"):
                                text = text[5:] if text.startswith("data:") else text
                            if not text:
                                continue
                            
                            data = json.loads(text)
                            candidates = data.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                for part in parts:
                                    if "text" in part:
                                        buffer += part["text"]
                                        
                                        if not in_html and "```html" in buffer:
                                            in_html = True
                                            start_idx = buffer.find("```html") + 7
                                            buffer = buffer[start_idx:]
                                        
                                        if in_html and "```" in buffer:
                                            end_idx = buffer.find("```")
                                            yield buffer[:end_idx]
                                            return
                                        
                                        if in_html:
                                            yield buffer
                                            buffer = ""
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            yield f"<!-- Error: {str(e)} -->"
    
    async def _call_model(self, system_prompt: str, user_prompt: str) -> str:
        """调用模型生成内容，使用 REST API"""
        if not self.client:
            return self._get_mock_response(user_prompt)
        
        try:
            return await self._call_rest_api(self.model, system_prompt, user_prompt)
        except Exception as e:
            print(f"❌ 模型调用错误: {str(e)}")
            # 尝试回退到备用模型（如果启用）
            if self.enable_fallback and self._current_model != self.fallback_model:
                print(f"⚠️ 正在回退到备用模型: {self.fallback_model}")
                return await self._call_fallback_model(system_prompt, user_prompt)
            raise RuntimeError(f"Model call failed: {str(e)}")
    
    async def _call_rest_api(self, model: str, system_prompt: str, user_prompt: str) -> str:
        """通过 REST API 调用 Gemini 模型（支持多种代理认证方式）"""
        # 构建 API URL
        base = self.base_url.rstrip("/") if self.base_url else "https://generativelanguage.googleapis.com"
        
        # 认证方式：通过环境变量 GENERATIVE_UI_AUTH_TYPE 指定
        # - "bearer": 使用 Bearer token（Authorization header）
        # - "query" 或其他: 使用 URL 参数 ?key=xxx（Google 官方格式）
        auth_type = os.getenv("GENERATIVE_UI_AUTH_TYPE", "query").lower()
        
        if auth_type == "bearer":
            url = f"{base}/v1beta/models/{model}:generateContent"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        else:
            # 使用 URL 参数传递 API Key（Google 官方格式，默认）
            url = f"{base}/v1beta/models/{model}:generateContent?key={self.api_key}"
            headers = {
                "Content-Type": "application/json",
            }
        
        print(f"📡 请求 URL: {url.split('?')[0]}")
        
        # 构建请求体
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "maxOutputTokens": 65536,
            }
        }
        
        # 检查是否需要禁用 thinking 模式（Gemini 3 Pro 等模型）
        disable_thinking = os.getenv("GENUI_DISABLE_THINKING", "true").lower() == "true"
        if disable_thinking:
            # 通过设置 thinkingConfig 禁用 thinking 模式
            payload["generationConfig"]["thinkingConfig"] = {
                "thinkingBudget": 0  # 设置为 0 禁用 thinking
            }
            print("🧠 Thinking 模式已禁用")
        
        # 配置连接器，增加稳定性
        connector = aiohttp.TCPConnector(
            limit=1,
            force_close=True,  # 每次请求后关闭连接
        )
        timeout = aiohttp.ClientTimeout(
            total=300,      # 总超时 5 分钟
            connect=30,     # 连接超时 30 秒
            sock_read=300,  # 读取超时 5 分钟
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(url, json=payload, headers=headers, timeout=timeout) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"API error {resp.status}: {error_text}")
                
                data = await resp.json()
                
                # 保存原始响应到调试目录
                debug_dir = os.getenv("GENUI_DEBUG_DIR", "genui_debug_output")
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                try:
                    os.makedirs(debug_dir, exist_ok=True)
                    
                    # 保存原始 API 响应 JSON
                    api_response_path = os.path.join(debug_dir, f"{timestamp}_api_response.json")
                    with open(api_response_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"📄 API 响应已保存到: {api_response_path}")
                except Exception as e:
                    print(f"⚠️ 保存调试文件失败: {e}")
                
                # 提取生成的文本
                candidates = data.get("candidates", [])
                if not candidates:
                    raise RuntimeError("No candidates in response")
                
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                
                # 合并所有文本部分（过滤掉 thought=true 的部分，只保留实际输出）
                text_parts = []
                thought_parts = []
                for p in parts:
                    if "text" in p:
                        # 如果有 thought 字段且为 True，单独保存（这是模型的思考过程）
                        if p.get("thought") is True:
                            thought_parts.append(p["text"])
                        else:
                            text_parts.append(p["text"])
                
                result_text = "".join(text_parts)
                
                # 尝试从 JSON 响应中提取 html 字段（使用了 responseSchema）
                if result_text.strip():
                    try:
                        json_response = json.loads(result_text)
                        if isinstance(json_response, dict) and "html" in json_response:
                            print("✅ 从 JSON 响应中提取到 html 字段")
                            result_text = json_response["html"]
                    except json.JSONDecodeError:
                        # 不是 JSON 格式，保持原样
                        pass
                
                # 如果过滤后为空，检查 thought 内容中是否包含 HTML
                if not result_text.strip() and thought_parts:
                    print(f"⚠️ 主输出为空，检查 thought 内容中是否有 HTML...")
                    all_thoughts = "".join(thought_parts)
                    # 检查 thought 中是否有完整的 HTML
                    if "<!DOCTYPE" in all_thoughts or "```html" in all_thoughts:
                        print(f"✅ 在 thought 内容中找到 HTML，使用 thought 内容")
                        result_text = all_thoughts
                    else:
                        print(f"❌ thought 内容中没有 HTML，返回所有文本")
                        result_text = all_thoughts
                
                if not result_text.strip():
                    raise RuntimeError("API returned empty response (no text content)")
                
                # 保存模型输出文本到调试目录
                try:
                    # 保存主输出
                    output_path = os.path.join(debug_dir, f"{timestamp}_model_output.txt")
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(result_text)
                    print(f"📄 模型输出已保存到: {output_path}")
                    
                    # 如果有 thought 内容，单独保存
                    if thought_parts:
                        thought_path = os.path.join(debug_dir, f"{timestamp}_thought_output.txt")
                        with open(thought_path, "w", encoding="utf-8") as f:
                            f.write("".join(thought_parts))
                        print(f"📄 思考过程已保存到: {thought_path}")
                except Exception as e:
                    print(f"⚠️ 保存模型输出失败: {e}")
                
                return result_text
    
    async def _call_fallback_model(self, system_prompt: str, user_prompt: str) -> str:
        """调用备用模型"""
        try:
            self._current_model = self.fallback_model
            return await self._call_rest_api(self.fallback_model, system_prompt, user_prompt)
        except Exception as e:
            raise RuntimeError(f"Fallback model also failed: {str(e)}")
    
    def _extract_html(self, response: str) -> str:
        """从 LLM 响应中提取 HTML 代码"""
        # 方法1：查找 ```html 开始标记，然后找到对应的 ``` 结束标记
        html_start = response.find("```html")
        if html_start != -1:
            content_start = html_start + 7  # len("```html") = 7
            # 跳过开始标记后的空白字符
            while content_start < len(response) and response[content_start] in " \t\n\r":
                content_start += 1
            
            # 从内容开始位置查找结束标记 ```
            # 需要找到独立的 ``` （通常在行首或前面有换行）
            remaining = response[content_start:]
            
            # 查找 </html> 后的 ``` 结束标记
            html_end_tag = remaining.lower().rfind("</html>")
            if html_end_tag != -1:
                # 找到 </html> 后的 ``` 
                after_html = remaining[html_end_tag + 7:]  # len("</html>") = 7
                end_marker = after_html.find("```")
                if end_marker != -1:
                    html_content = remaining[:html_end_tag + 7]
                    return html_content.strip()
            
            # 回退：简单查找最后一个 ```
            end_marker = remaining.rfind("\n```")
            if end_marker != -1:
                return remaining[:end_marker].strip()
            
            # 再回退：查找任意 ```
            end_marker = remaining.find("```")
            if end_marker != -1:
                return remaining[:end_marker].strip()
        
        # 方法2：直接查找 DOCTYPE 到 </html>
        doctype_match = re.search(
            r'(<!DOCTYPE\s+html[\s\S]*?</html>)',
            response,
            re.IGNORECASE
        )
        if doctype_match:
            return doctype_match.group(1).strip()
        
        # 方法3：如果响应本身看起来像 HTML
        if response.strip().startswith('<!DOCTYPE') or response.strip().startswith('<html'):
            return response.strip()
        
        return ""
    
    def _get_mock_response(self, user_prompt: str) -> str:
        """Mock 模式下的示例响应"""
        return f'''```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generative UI Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold text-center text-gray-800 mb-8">
            🚀 Generative UI
        </h1>
        <div class="bg-white rounded-lg shadow-lg p-6">
            <p class="text-gray-600 mb-4">
                用户请求: {user_prompt[:100]}...
            </p>
            <p class="text-sm text-gray-400">
                这是 Mock 模式的示例响应。请设置 GOOGLE_API_KEY 环境变量以启用真实生成。
            </p>
        </div>
    </div>
    <script>
        console.log('Generative UI page loaded');
        window.onerror = function(msg, url, line) {{
            console.error('Error:', msg, 'at', url, ':', line);
        }};
    </script>
</body>
</html>
```'''
