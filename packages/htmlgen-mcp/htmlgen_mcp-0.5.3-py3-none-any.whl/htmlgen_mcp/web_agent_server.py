#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generative UI MCP 服务

基于 Google Research Generative UI 论文，通过 Gemini 模型生成交互式网页。
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import traceback
import zipfile
import tempfile
import aiohttp
from typing import Any, Dict, Optional

import uuid
from pathlib import Path

from fastmcp import FastMCP

# 确保项目根目录在模块搜索路径中
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ============================================================================
# 配置
# ============================================================================

NAS_PATH = os.environ.get("NAS_STORAGE_PATH", "/app/mcp-servers/mcp-servers/html_agent")
DEFAULT_PROJECT_ROOT = os.path.abspath(
    os.environ.get("WEB_AGENT_PROJECT_ROOT", f"{NAS_PATH}/projects")
)
AUTO_CREATE_PROJECT_DIR = os.environ.get("AUTO_CREATE_PROJECT_DIR", "true").lower() == "true"
DEFAULT_UPLOAD_URL = os.environ.get(
    "UPLOAD_URL", "https://www.mcpcn.cc/api/fileUploadAndDownload/uploadMcpFile"
)

# 任务持久化目录（延迟创建）
JOBS_STORAGE_DIR = os.path.join(NAS_PATH, "jobs")

mcp = FastMCP("generative-ui")

# Generative UI 任务注册表（内存缓存）
_GENUI_JOBS: dict[str, Dict[str, Any]] = {}

# 标记是否已初始化存储目录
_JOBS_DIR_INITIALIZED = False


# ============================================================================
# 任务持久化函数
# ============================================================================

def _ensure_jobs_dir() -> bool:
    """确保任务存储目录存在，返回是否可用"""
    global _JOBS_DIR_INITIALIZED
    if _JOBS_DIR_INITIALIZED:
        return True
    try:
        os.makedirs(JOBS_STORAGE_DIR, exist_ok=True)
        _JOBS_DIR_INITIALIZED = True
        return True
    except Exception as e:
        print(f"⚠️ 无法创建任务存储目录: {e}，将仅使用内存存储")
        return False


def _get_job_file_path(job_id: str) -> str:
    """获取任务文件路径"""
    return os.path.join(JOBS_STORAGE_DIR, f"{job_id}.json")


def _save_job(job_id: str, job_data: Dict[str, Any]) -> None:
    """保存任务到文件"""
    if not _ensure_jobs_dir():
        return  # 目录不可用，跳过文件保存
    try:
        file_path = _get_job_file_path(job_id)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(job_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存任务失败: {job_id}, 错误: {e}")


def _load_job(job_id: str) -> Optional[Dict[str, Any]]:
    """从文件加载任务"""
    try:
        file_path = _get_job_file_path(job_id)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"加载任务失败: {job_id}, 错误: {e}")
    return None


def _update_job(job_id: str, updates: Dict[str, Any]) -> None:
    """更新任务状态（内存 + 文件）"""
    if job_id in _GENUI_JOBS:
        _GENUI_JOBS[job_id].update(updates)
        _save_job(job_id, _GENUI_JOBS[job_id])
    else:
        # 从文件加载后更新
        job_data = _load_job(job_id)
        if job_data:
            job_data.update(updates)
            _GENUI_JOBS[job_id] = job_data
            _save_job(job_id, job_data)


# ============================================================================
# 辅助函数
# ============================================================================

def _resolve_edgeone_deploy_env() -> str:
    """解析 EdgeOne 自动部署环境，默认 Production。"""
    env_value = (
        os.environ.get("EDGEONE_AUTO_DEPLOY_ENV")
        or os.environ.get("EDGEONE_PAGES_DEPLOY_ENV")
        or "Production"
    )
    return env_value if env_value in {"Production", "Preview"} else "Production"


def _should_upload_zip_to_oss() -> bool:
    """是否在 EdgeOne 部署前上传 ZIP 到 OSS。"""
    flag = os.environ.get("KEEP_OSS_UPLOAD", "true").strip().lower()
    return flag not in {"0", "false", "no", "off"}


def _resolve_project_directory(project_root: Optional[str], project_name: Optional[str] = None) -> str:
    """解析项目目录路径"""
    if project_root:
        if os.path.isabs(project_root):
            abs_path = project_root
        else:
            if '/' not in project_root and '\\' not in project_root:
                abs_path = os.path.join(DEFAULT_PROJECT_ROOT, project_root)
            else:
                abs_path = os.path.abspath(os.path.join(DEFAULT_PROJECT_ROOT, project_root))
    else:
        base = DEFAULT_PROJECT_ROOT
        if project_name and AUTO_CREATE_PROJECT_DIR:
            safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_', '.'))
            safe_name = safe_name.strip().replace(' ', '_')
            if safe_name:
                abs_path = os.path.join(base, safe_name)
            else:
                abs_path = base
        else:
            abs_path = base
    
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


# ============================================================================
# MCP 工具 - Generative UI
# ============================================================================

@mcp.tool()
async def generate_interactive_page(prompt: str) -> Dict[str, Any]:
    """🚀 生成交互式网页应用 - 主要的网页生成工具

    基于 Google Research Generative UI 论文，通过 Gemini 模型一次性生成完整的交互式 HTML 应用。
    任务会在后台异步执行，立即返回 job_id，使用 get_generation_progress 查询进度。

    参数说明：
    - prompt: 用户需求描述，支持多种类型：
      * 简单工具："创建一个计数器" → 生成计数器应用
      * 时间显示："现在几点了" → 生成精美时钟
      * 游戏请求："俄罗斯方块游戏" → 生成可玩的游戏
      * 数据展示：传入 JSON 数据 + 描述 → 生成数据展示页面

    返回值：
    - status: "pending" 表示任务已提交
    - job_id: 任务ID，用于查询进度
    
    使用 get_generation_progress(job_id) 查询任务状态，完成后返回：
    - status: "completed"
    - html: 生成的完整 HTML 页面代码
    - output_path: 本地保存路径
    - generation_time: 生成耗时（秒）
    """
    job_id = uuid.uuid4().hex
    
    job_data = {
        "status": "pending",
        "prompt": prompt,
        "created_at": time.time(),
        "progress": "正在初始化...",
    }
    _GENUI_JOBS[job_id] = job_data
    _save_job(job_id, job_data)
    
    asyncio.create_task(_run_genui_job(job_id, prompt))
    
    return {
        "status": "pending",
        "job_id": job_id,
        "message": "任务已提交，请使用 get_generation_progress 查询进度",
    }


async def _run_genui_job(job_id: str, prompt: str) -> None:
    """后台执行 Generative UI 生成任务"""
    try:
        _update_job(job_id, {
            "status": "running",
            "progress": "正在调用 Gemini 模型生成页面...",
            "started_at": time.time(),
        })
        
        from htmlgen_mcp.generative_ui import GenerativeUIAgent
        
        agent = GenerativeUIAgent()
        result = await agent.generate(prompt)
        
        if not result.success:
            _update_job(job_id, {
                "status": "failed",
                "progress": "生成失败",
                "errors": result.errors,
            })
            return
        
        _update_job(job_id, {"progress": "正在保存文件..."})
        
        # 保存文件
        page_id = uuid.uuid4().hex
        resolved_output_dir = _resolve_project_directory(None, f"genui_{page_id[:8]}")
        output_path = os.path.join(resolved_output_dir, "index.html")
        
        from htmlgen_mcp.generative_ui.tools.endpoints_service import ToolEndpointsService
        endpoint_service = ToolEndpointsService()
        final_html = endpoint_service.resolve_html(result.html)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)
        
        _update_job(job_id, {
            "page_id": page_id,
            "output_path": output_path,
            "model": result.model,
            "generation_time": result.generation_time,
            "html_length": len(final_html),
        })
        
        # 1. 上传到 OSS
        _update_job(job_id, {"progress": "正在上传到 OSS..."})
        try:
            # 打包为 ZIP
            zip_filename = f"genui_{page_id[:8]}_{int(time.time())}.zip"
            zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
            
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(resolved_output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, resolved_output_dir)
                        zipf.write(file_path, arcname)
            
            # 上传到 OSS
            async with aiohttp.ClientSession() as session:
                with open(zip_path, "rb") as f:
                    data = aiohttp.FormData()
                    data.add_field("file", f, filename=zip_filename, content_type="application/zip")
                    
                    async with session.post(DEFAULT_UPLOAD_URL, data=data) as response:
                        if response.status == 200:
                            oss_result = await response.json()
                            oss_data = oss_result.get("data") or {}
                            _update_job(job_id, {
                                "oss_url": oss_data.get("url") or oss_data.get("file", {}).get("url"),
                                "oss_status": "success",
                            })
                        else:
                            _update_job(job_id, {
                                "oss_status": "failed",
                                "oss_error": f"HTTP {response.status}",
                            })
            
            # 清理临时 ZIP
            if os.path.exists(zip_path):
                os.remove(zip_path)
                
        except Exception as oss_err:
            _update_job(job_id, {
                "oss_status": "failed",
                "oss_error": str(oss_err),
            })
        
        # 2. 部署到 EdgeOne Pages
        _update_job(job_id, {"progress": "正在部署到 EdgeOne Pages..."})
        try:
            deploy_result = await deploy_to_edgeone_pages(
                folder_path=resolved_output_dir,
                env=_resolve_edgeone_deploy_env(),
            )
            if deploy_result.get("status") == "success":
                _update_job(job_id, {
                    "web_url": deploy_result.get("result", {}).get("url"),
                    "deployment_status": "success",
                })
            else:
                _update_job(job_id, {
                    "deployment_status": "failed",
                    "deployment_error": deploy_result.get("message"),
                })
        except Exception as deploy_err:
            _update_job(job_id, {
                "deployment_status": "failed",
                "deployment_error": str(deploy_err),
            })
        
        _update_job(job_id, {
            "status": "completed",
            "progress": "生成完成",
            "completed_at": time.time(),
        })
        
    except Exception as e:
        _update_job(job_id, {
            "status": "failed",
            "progress": f"错误: {str(e)}",
            "error": str(e),
        })


@mcp.tool()
async def get_generation_progress(job_id: str) -> Dict[str, Any]:
    """查询网页生成任务的进度

    参数：
    - job_id: 任务ID，由 generate_interactive_page 返回

    返回值：
    - status: 任务状态 (pending/running/completed/failed)
    - job: 任务详情对象，包含 progress, output_path, upload_url, web_url, generation_time 等
    """
    # 优先从内存获取，否则从文件加载
    if job_id in _GENUI_JOBS:
        job_data = _GENUI_JOBS[job_id].copy()
    else:
        job_data = _load_job(job_id)
        if job_data:
            _GENUI_JOBS[job_id] = job_data  # 缓存到内存
            job_data = job_data.copy()
    
    if not job_data:
        return {
            "status": "not_found",
            "message": f"未找到任务: {job_id}",
        }
    
    # 不返回完整 HTML（太长），只返回长度
    if "html" in job_data:
        del job_data["html"]
    
    # 计算已用时间
    if job_data.get("started_at"):
        if job_data.get("completed_at"):
            job_data["elapsed_time"] = round(job_data["completed_at"] - job_data["started_at"], 2)
        else:
            job_data["elapsed_time"] = round(time.time() - job_data["started_at"], 2)
    
    # 将 oss_url 重命名为 upload_url
    if "oss_url" in job_data:
        job_data["upload_url"] = job_data.pop("oss_url")
    
    # 返回嵌套的 job 结构
    return {
        "status": job_data.get("status", "unknown"),
        "job": job_data,
    }


@mcp.tool()
async def get_generative_ui_status() -> Dict[str, Any]:
    """获取 Generative UI 模块状态和配置信息"""
    try:
        from htmlgen_mcp.generative_ui.config import get_config, SUPPORTED_MODELS
        
        config = get_config()
        
        return {
            "status": "available",
            "configured": config.is_configured,
            "primary_model": config.primary_model,
            "fallback_model": config.fallback_model,
            "supported_models": SUPPORTED_MODELS,
            "api_key_set": bool(config.api_key),
            "base_url": config.base_url,
            "hint": "设置 GOOGLE_API_KEY 环境变量以启用 Gemini 模型" if not config.api_key else None,
        }
    except ImportError:
        return {
            "status": "unavailable",
            "message": "Generative UI 模块未安装",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


# ============================================================================
# 内部辅助函数 - EdgeOne 部署
# ============================================================================

async def deploy_to_edgeone_pages(folder_path: str, env: str = "Production") -> Dict[str, Any]:
    """内部函数：将文件夹部署到 EdgeOne Pages"""
    try:
        from htmlgen_mcp.agents.web_tools.edgeone_deploy import deploy_folder_or_zip_to_edgeone

        api_token = os.getenv("EDGEONE_PAGES_API_TOKEN")
        if not api_token:
            return {
                "status": "error",
                "message": "Missing EDGEONE_PAGES_API_TOKEN environment variable.",
            }

        result_json = await asyncio.to_thread(deploy_folder_or_zip_to_edgeone, folder_path, env)
        result = json.loads(result_json)

        return {
            "status": "success",
            "result": result.get("result", {}),
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
        }


# ============================================================================
# 入口
# ============================================================================

def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    print("🚀 Generative UI MCP 服务器已启动")
    print(f"📁 默认项目根目录: {DEFAULT_PROJECT_ROOT}")
    print("=" * 50)
    print("📦 可用工具:")
    print("  • generate_interactive_page - 🚀 主要工具：生成交互式网页")
    print("  • get_generation_progress - 📊 查询生成任务进度")
    print("  • get_generative_ui_status - ℹ️ 查看模块状态")
    print("=" * 50)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
