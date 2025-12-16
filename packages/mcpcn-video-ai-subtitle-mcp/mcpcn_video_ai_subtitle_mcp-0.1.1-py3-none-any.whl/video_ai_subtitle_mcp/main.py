#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频AI字幕生成 MCP 服务
工具：
1. generate_subtitle - 从视频生成 SRT 字幕
2. merge_subtitle - 将字幕合并到视频

通过 Roots 协议获取用户 token，调用 mcpcn.cc 后端 API
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time
import logging
from logging.handlers import RotatingFileHandler
import tempfile
import threading
from pathlib import Path
from urllib.request import urlretrieve
from urllib.parse import unquote
import platform
import urllib.parse
from typing import Any

import ffmpeg
import requests
from mcp import types
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from pydantic import BaseModel

# 配置日志
logger = logging.getLogger("video_ai_subtitle_mcp")

package = "video-ai-subtitle-mcp"


def get_desktop_path() -> Path:
    """获取桌面路径，支持 Windows 和 macOS"""
    system = platform.system()
    if system == "Windows":
        # Windows: 使用 USERPROFILE 环境变量
        desktop = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
        if not desktop.exists():
            # 尝试中文路径
            desktop = Path(os.environ.get("USERPROFILE", "")) / "桌面"
    else:
        # macOS / Linux: 使用 HOME 环境变量
        desktop = Path.home() / "Desktop"
        if not desktop.exists():
            desktop = Path.home() / "桌面"
    
    # 如果桌面路径不存在，回退到临时目录
    if not desktop.exists():
        desktop = Path(tempfile.gettempdir()) / package
    
    return desktop


# 日志文件输出到桌面
log_dir = get_desktop_path()
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"{package}_debug.log"


def setup_logging() -> str:
    """配置日志处理器"""
    if getattr(logger, "_configured", False):
        return str(log_file)

    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    file_handler = RotatingFileHandler(
        str(log_file), maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    setattr(logger, "_configured", True)
    return str(log_file)


# ffmpeg 配置
FFMPEG_BINARY = os.environ.get("FFMPEG_BINARY")
FFPROBE_BINARY = os.environ.get("FFPROBE_BINARY")

# mcpcn.cc API 配置
MCPCN_API_BASE = "https://www.mcpcn.cc"

# 全局状态
_mcpcn_token: str = os.environ.get("MCPCN_TOKEN", "")
SERVER_SESSION = None


class RawRootsResult(BaseModel):
    """原始 roots 结果，不验证 URI 格式"""
    roots: list[dict[str, Any]] = []

    class Config:
        extra = "allow"


def get_token() -> str:
    """获取当前 token"""
    global _mcpcn_token
    return _mcpcn_token


def set_token(token: str) -> None:
    """设置 token"""
    global _mcpcn_token
    _mcpcn_token = token


async def safe_list_roots(session: Any) -> list[dict[str, Any]]:
    """安全地获取 roots 列表"""
    try:
        logger.info("[Roots] 开始请求 roots 列表...")
        response = await session.send_request(
            types.ServerRequest(types.ListRootsRequest()),
            RawRootsResult,
        )
        logger.info("[Roots] 收到响应: %s", response)
        
        if response and response.roots:
            logger.info("[Roots] 获取到 %d 个 root 项", len(response.roots))
            for idx, root in enumerate(response.roots):
                logger.info("[Roots] root[%d]: %s", idx, json.dumps(root, ensure_ascii=False, default=str))
            return response.roots
        
        logger.warning("[Roots] 响应为空或无 roots 数据")
        return []
    except Exception as e:
        logger.error("[Roots] 获取 roots 失败: %s", e, exc_info=True)
        return []


def load_token_from_roots(raw_roots: list[dict[str, Any]]) -> None:
    """从 roots 中提取 token"""
    global _mcpcn_token
    
    logger.info("[LoadToken] 开始从 roots 中提取 token，共 %d 个 root", len(raw_roots))
    logger.info("[LoadToken] 原始 roots 数据: %s", json.dumps(raw_roots, ensure_ascii=False, default=str))
    
    for idx, root in enumerate(raw_roots):
        try:
            uri = str(root.get("uri", ""))
            name = root.get("name", "")
            logger.info("[LoadToken] 检查 root[%d]: name=%s, uri=%s", idx, name, uri)
            
            # 解析 mcpcn://token/<token> 格式
            if uri.startswith("mcpcn://token/"):
                token = unquote(uri[14:])  # 去掉 "mcpcn://token/" 前缀
                if token:
                    _mcpcn_token = token
                    logger.info("[LoadToken] ✓ 从 Roots 协议成功获取到 token (长度: %d)", len(token))
                    return
            else:
                logger.debug("[LoadToken] root[%d] 不是 token URI，跳过", idx)
        except Exception as e:
            logger.warning("[LoadToken] 处理 root[%d] 时出错: %s, 错误: %s", idx, root, e)
    
    # 回退到环境变量
    logger.info("[LoadToken] 未从 roots 中找到 token，尝试环境变量...")
    if not _mcpcn_token:
        _mcpcn_token = os.environ.get("MCPCN_TOKEN", "")
        if _mcpcn_token:
            logger.info("[LoadToken] ✓ 从环境变量 MCPCN_TOKEN 获取到 token (长度: %d)", len(_mcpcn_token))
        else:
            logger.warning("[LoadToken] ✗ 未找到 token，API 调用可能失败")


# ============== ffmpeg 相关函数 ==============

def _ffmpeg_run(stream_spec, **kwargs):
    """Run ffmpeg with an explicit binary path."""
    if "overwrite_output" not in kwargs:
        kwargs["overwrite_output"] = True
    return ffmpeg.run(stream_spec, cmd=FFMPEG_BINARY, **kwargs)


def _ffmpeg_run_async(stream_spec, **kwargs):
    """Run ffmpeg asynchronously with explicit binary path."""
    return ffmpeg.run_async(stream_spec, cmd=FFMPEG_BINARY, **kwargs)


def _ffmpeg_run_with_progress(stream_spec, operation_name: str = "Processing", **kwargs):
    """Run ffmpeg with progress logging."""
    if 'overwrite_output' not in kwargs:
        kwargs['overwrite_output'] = True

    process = _ffmpeg_run_async(stream_spec, pipe_stderr=True, **kwargs)
    logger.info(f"{operation_name} 开始...")
    
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        error_message = stderr.decode("utf8") if stderr else "Unknown error"
        logger.error(f"{operation_name} 失败: {error_message}")
        raise ffmpeg.Error("ffmpeg", stdout, stderr)
    
    logger.info(f"{operation_name} 完成")
    return process


def _prepare_path(input_path: str, output_path: str, overwrite: bool = False) -> None:
    """Prepare and validate input/output paths."""
    if not os.path.exists(input_path):
        raise RuntimeError(f"Error: Input file not found at {input_path}")
    try:
        parent_dir = os.path.dirname(output_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Error creating output directory for {output_path}: {str(e)}")
    if os.path.exists(output_path) and not overwrite:
        raise RuntimeError(f"Error: Output file already exists at {output_path}.")


def extract_audio(video_path: Path, wav_path: Path):
    """使用 ffmpeg-python 提取音频"""
    input_stream = ffmpeg.input(str(video_path))
    output_stream = input_stream.output(
        str(wav_path),
        vn=None,
        ac=1,
        ar=16000,
        f="wav"
    )
    _ffmpeg_run_with_progress(output_stream, operation_name="提取音频")


# ============== mcpcn.cc API 函数 ==============

def upload_to_mcpcn(file_path: Path, token: str = None) -> str:
    """上传文件到 mcpcn.cc"""
    headers = {}
    if token:
        headers["x-token"] = token
    
    with open(file_path, 'rb') as f:
        resp = requests.post(
            f'{MCPCN_API_BASE}/api/fileUploadAndDownload/uploadMcpFile',
            files={'file': f},
            headers=headers
        )
    if resp.status_code == 200 and resp.json().get('code') == 0:
        return resp.json()['data']['url']
    raise RuntimeError(f"上传失败: {resp.text}")


def submit_caption_task(
    url: str,
    token: str,
    language: str = "zh-CN",
    words_per_line: int = 46,
    max_lines: int = 1,
    caption_type: str = "auto"
) -> str:
    """提交字幕生成任务到 mcpcn.cc API"""
    resp = requests.post(
        f'{MCPCN_API_BASE}/api/translate/videoCaption/submit',
        headers={
            'Content-Type': 'application/json',
            'x-token': token
        },
        json={
            'url': url,
            'language': language,
            'words_per_line': words_per_line,
            'max_lines': max_lines,
            'caption_type': caption_type
        }
    )
    data = resp.json()
    if data.get('code') != 0:
        raise RuntimeError(f"提交失败: {data.get('msg', resp.text)}")
    return data['data']['id']


def query_caption_result(task_id: str, token: str, blocking: bool = True) -> dict:
    """查询字幕生成结果（会触发扣费）"""
    params = {'id': task_id}
    if blocking:
        params['blocking'] = 1
    
    resp = requests.get(
        f'{MCPCN_API_BASE}/api/translate/videoCaption/query',
        params=params,
        headers={'x-token': token}
    )
    data = resp.json()
    
    if data.get('code') != 0:
        raise RuntimeError(f"查询失败: {data.get('msg', resp.text)}")
    
    return data.get('data', data)


def ms_to_timestamp(ms: int) -> str:
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def result_to_srt(data: dict, srt_path: Path):
    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, u in enumerate(data.get('utterances', []), 1):
            f.write(f"{i}\n{ms_to_timestamp(u['start_time'])} --> {ms_to_timestamp(u['end_time'])}\n{u['text'].strip()}\n\n")


# ============== 字幕烧录相关函数 ==============

def _color_to_ass(color: str) -> str:
    """将颜色转换为 ASS 格式 (&HAABBGGRR)"""
    color_map = {
        "white": "FFFFFF", "black": "000000", "red": "FF0000",
        "green": "00FF00", "blue": "0000FF", "yellow": "FFFF00",
        "cyan": "00FFFF", "magenta": "FF00FF", "orange": "FFA500", "pink": "FFC0CB",
    }
    
    color_lower = color.lower().strip()
    if color_lower in color_map:
        hex_color = color_map[color_lower]
    else:
        hex_color = color.lstrip('#').upper()
        if len(hex_color) != 6:
            hex_color = "FFFFFF"
    
    r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
    return f"&H00{b}{g}{r}"


def burn_subtitle(
    video_path: Path,
    srt_path: Path,
    output_path: Path,
    font_color: str = "white",
    outline_color: str = "black",
    font_size: int = 24,
    position: str = "bottom",
    margin_v: int = 50,
):
    """使用 ffmpeg-python 烧录字幕"""
    font_name, font_file = "Arial", None
    for name, path in [
        ("Arial Unicode MS", "/Library/Fonts/Arial Unicode.ttf"),
        ("STHeiti", "/System/Library/Fonts/STHeiti Medium.ttc"),
        ("PingFang SC", "/System/Library/Fonts/PingFang.ttc"),
    ]:
        if os.path.exists(path):
            font_name, font_file = name, path
            break
    
    primary_colour = _color_to_ass(font_color)
    outline_colour = _color_to_ass(outline_color)
    
    alignment_map = {"top": 8, "center": 5, "bottom": 2}
    alignment = alignment_map.get(position.lower(), 2)
    
    safe_srt = str(srt_path.absolute()).replace("'", "\\'").replace(":", "\\:")
    style = f"FontName={font_name},FontSize={font_size},PrimaryColour={primary_colour},OutlineColour={outline_colour},Outline=2,Alignment={alignment},MarginV={margin_v}"
    vf = f"subtitles='{safe_srt}':force_style='{style}'"
    if font_file:
        vf += f":fontsdir='{str(Path(font_file).parent).replace(':', '\\:')}'"
    
    input_stream = ffmpeg.input(str(video_path))
    output_stream = input_stream.output(
        str(output_path),
        vf=vf,
        **{'c:v': 'libx264', 'c:a': 'copy'}
    )
    _ffmpeg_run_with_progress(output_stream, operation_name="烧录字幕")


# ============== 工具实现函数 ==============

def do_generate_subtitle(
    video_url: str,
    output_dir: str = "outputs",
    output_name: str = "output",
    language: str = "zh-CN",
    words_per_line: int = 46,
    max_lines: int = 1,
) -> dict:
    """生成字幕的核心逻辑"""
    execution_start_time = time.time()
    
    token = get_token()
    if not token:
        return {
            "success": False,
            "error": "未配置 token\n请通过以下方式之一配置:\n1. Roots 协议: 添加 mcpcn://token/<your-token>\n2. 环境变量: MCPCN_TOKEN=<your-token>"
        }
    
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    video_path = out_dir / f"{output_name}_original_{timestamp}.mp4"
    wav_path = out_dir / f"{output_name}_{timestamp}.wav"
    srt_path = out_dir / f"{output_name}_{timestamp}.srt"
    
    logger.info("下载视频...")
    urlretrieve(video_url, str(video_path))
    
    logger.info("提取音频...")
    extract_audio(video_path, wav_path)
    
    logger.info("上传音频...")
    audio_url = upload_to_mcpcn(wav_path, token)
    
    logger.info("提交字幕任务...")
    task_id = submit_caption_task(
        url=audio_url,
        token=token,
        language=language,
        words_per_line=words_per_line,
        max_lines=max_lines
    )
    
    logger.info("等待识别结果...")
    result = query_caption_result(task_id, token, blocking=True)
    
    logger.info("生成字幕文件...")
    result_to_srt(result, srt_path)
    
    execution_time = time.time() - execution_start_time
    duration = result.get('duration', 0)
    
    return {
        "success": True,
        "srt_path": str(srt_path.absolute()),
        "video_path": str(video_path.absolute()),
        "utterance_count": len(result.get('utterances', [])),
        "duration": duration,
        "execution_time": execution_time
    }


def do_merge_subtitle(
    video_path: str,
    srt_path: str,
    output_path: str = "",
    font_color: str = "white",
    outline_color: str = "black",
    font_size: int = 24,
    position: str = "bottom",
    margin_v: int = 50,
) -> dict:
    """合并字幕的核心逻辑"""
    execution_start_time = time.time()
    
    video = Path(video_path)
    srt = Path(srt_path)
    if output_path:
        output = Path(output_path)
    else:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output = video.parent / f"{video.stem}_with_sub_{timestamp}.mp4"
    
    _prepare_path(str(video), str(output), overwrite=True)
    
    burn_subtitle(
        video, srt, output,
        font_color=font_color,
        outline_color=outline_color,
        font_size=font_size,
        position=position,
        margin_v=margin_v,
    )
    
    execution_time = time.time() - execution_start_time
    
    return {
        "success": True,
        "output_path": str(output.absolute()),
        "execution_time": execution_time
    }


# ============== MCP 服务器定义 ==============

TOOL_DEFINITIONS = [
    types.Tool(
        name="generate_subtitle",
        description="从视频 URL 生成 SRT 字幕文件（使用 mcpcn.cc 字幕 API）",
        inputSchema={
            "type": "object",
            "properties": {
                "video_url": {
                    "type": "string",
                    "description": "视频的公网 URL",
                },
                "output_dir": {
                    "type": "string",
                    "description": "输出目录，默认 outputs",
                    "default": "outputs",
                },
                "output_name": {
                    "type": "string",
                    "description": "输出文件名前缀，默认 output",
                    "default": "output",
                },
                "language": {
                    "type": "string",
                    "description": "语言代码，默认 zh-CN",
                    "default": "zh-CN",
                },
                "words_per_line": {
                    "type": "integer",
                    "description": "每行字数，默认 46",
                    "default": 46,
                },
                "max_lines": {
                    "type": "integer",
                    "description": "最大行数，默认 1",
                    "default": 1,
                },
            },
            "required": ["video_url"],
        },
    ),
    types.Tool(
        name="merge_subtitle",
        description="将 SRT 字幕文件合并（烧录）到视频中",
        inputSchema={
            "type": "object",
            "properties": {
                "video_path": {
                    "type": "string",
                    "description": "视频文件路径",
                },
                "srt_path": {
                    "type": "string",
                    "description": "SRT 字幕文件路径",
                },
                "output_path": {
                    "type": "string",
                    "description": "输出视频路径，默认在原视频目录生成",
                    "default": "",
                },
                "font_color": {
                    "type": "string",
                    "description": "字幕颜色，支持颜色名称或十六进制(#RRGGBB)，默认 white",
                    "default": "white",
                },
                "outline_color": {
                    "type": "string",
                    "description": "描边颜色，默认 black",
                    "default": "black",
                },
                "font_size": {
                    "type": "integer",
                    "description": "字体大小，默认 24",
                    "default": 24,
                },
                "position": {
                    "type": "string",
                    "description": "字幕位置，可选 top/center/bottom，默认 bottom",
                    "default": "bottom",
                },
                "margin_v": {
                    "type": "integer",
                    "description": "垂直边距(像素)，默认 50",
                    "default": 50,
                },
            },
            "required": ["video_path", "srt_path"],
        },
    ),
]

# 创建 MCP 服务器
mcp = Server("video-ai-subtitle-mcp")


@mcp.list_tools()
async def list_tools() -> list[types.Tool]:
    """列出可用工具"""
    return TOOL_DEFINITIONS


@mcp.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> types.CallToolResult:
    """处理工具调用"""
    payload = arguments or {}
    
    try:
        if name == "generate_subtitle":
            result = do_generate_subtitle(
                video_url=payload.get("video_url", ""),
                output_dir=payload.get("output_dir", "outputs"),
                output_name=payload.get("output_name", "output"),
                language=payload.get("language", "zh-CN"),
                words_per_line=payload.get("words_per_line", 46),
                max_lines=payload.get("max_lines", 1),
            )
            
            if result["success"]:
                text = f"✓ 字幕生成完成\n字幕文件: {result['srt_path']}\n视频文件: {result['video_path']}\n识别句数: {result['utterance_count']}\n音频时长: {result['duration']:.2f} 秒\n执行时间: {result['execution_time']:.2f} 秒"
            else:
                text = f"❌ 错误: {result['error']}"
                return types.CallToolResult(
                    content=[types.TextContent(type="text", text=text)],
                    isError=True,
                )
            
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=text)],
                structuredContent=result,
                isError=False,
            )
        
        elif name == "merge_subtitle":
            result = do_merge_subtitle(
                video_path=payload.get("video_path", ""),
                srt_path=payload.get("srt_path", ""),
                output_path=payload.get("output_path", ""),
                font_color=payload.get("font_color", "white"),
                outline_color=payload.get("outline_color", "black"),
                font_size=payload.get("font_size", 24),
                position=payload.get("position", "bottom"),
                margin_v=payload.get("margin_v", 50),
            )
            
            text = f"✓ 字幕合并完成\n输出文件: {result['output_path']}\n执行时间: {result['execution_time']:.2f} 秒"
            
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=text)],
                structuredContent=result,
                isError=False,
            )
        
        else:
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=f"未知工具: {name}")],
                isError=True,
            )
    
    except Exception as e:
        logger.error("工具执行失败: %s", e, exc_info=True)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"❌ 执行失败: {str(e)}")],
            isError=True,
        )


# ============== Roots 协议处理 ==============

async def handle_roots_changed(notification: types.RootsListChangedNotification) -> None:
    """处理 roots 变化通知"""
    global SERVER_SESSION
    logger.info("[MCP] 收到 roots 变化通知")
    try:
        if SERVER_SESSION:
            raw_roots = await safe_list_roots(SERVER_SESSION)
            load_token_from_roots(raw_roots)
    except Exception as e:
        logger.error("获取更新的 roots 失败: %s", e)


mcp.notification_handlers[types.RootsListChangedNotification] = handle_roots_changed


async def run_server() -> None:
    """运行服务器"""
    global SERVER_SESSION

    log_path = setup_logging()
    logger.info("=" * 60)
    logger.info("视频AI字幕 MCP 服务器启动")
    logger.info("操作系统: %s", platform.system())
    logger.info("平台: %s", platform.platform())
    logger.info("日志文件: %s", log_path)
    logger.info("=" * 60)

    async with stdio_server() as (read_stream, write_stream):
        init_options = mcp.create_initialization_options(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        )

        # Monkey-patch ServerSession 来在初始化完成后获取 roots
        from mcp.server.session import ServerSession
        original_received_notification = ServerSession._received_notification

        async def patched_received_notification(self, notification: types.ClientNotification) -> None:
            global SERVER_SESSION
            await original_received_notification(self, notification)

            if isinstance(notification.root, types.InitializedNotification):
                logger.info("[MCP] 收到初始化完成通知，准备获取 roots")
                SERVER_SESSION = self

                async def fetch_roots_background():
                    try:
                        client_params = self._client_params
                        logger.info("[MCP] 客户端参数: %s", client_params)
                        
                        if client_params:
                            logger.info("[MCP] 客户端能力: %s", client_params.capabilities)
                        
                        if client_params and client_params.capabilities and client_params.capabilities.roots:
                            logger.info("[MCP] ✓ 客户端支持 roots 协议，开始获取 roots")
                            raw_roots = await asyncio.wait_for(
                                safe_list_roots(self), timeout=10.0
                            )
                            logger.info("[MCP] 获取到的 raw_roots: %s", json.dumps(raw_roots, ensure_ascii=False, default=str))
                            load_token_from_roots(raw_roots)
                        else:
                            logger.warning("[MCP] ✗ 客户端不支持 MCP roots 协议")
                            if client_params and client_params.capabilities:
                                logger.warning("[MCP] 客户端能力详情: roots=%s", 
                                    getattr(client_params.capabilities, 'roots', None))
                            load_token_from_roots([])
                    except asyncio.TimeoutError:
                        logger.warning("[MCP] 获取 roots 超时 (10秒)，尝试从环境变量获取 token")
                        load_token_from_roots([])
                    except Exception as e:
                        logger.error("[MCP] 获取初始 roots 失败: %s", e, exc_info=True)
                        load_token_from_roots([])

                asyncio.create_task(fetch_roots_background())

        ServerSession._received_notification = patched_received_notification

        try:
            await mcp.run(
                read_stream,
                write_stream,
                init_options,
            )
        finally:
            ServerSession._received_notification = original_received_notification


def main() -> None:
    """主入口"""
    print("启动视频AI字幕 MCP 服务器 (Roots 协议)")
    print("可用工具: generate_subtitle, merge_subtitle")
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
