#!/usr/bin/env python3
"""
MCP Docs Server
读取项目 docs/ 目录下的所有 *.md 文件，供 Cursor 检索/引用。
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

from mcp.server.fastmcp import FastMCP # type: ignore

# ----------- 配置区 -----------
DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "docs"   # 与脚本同级的 docs/
DOC_SUFFIX = ".md"
# ----------------------------

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("docs-mcp")

# 全局缓存：filename -> content
docs_cache: Dict[str, str] = {}


# ---------- 工具函数 ----------
def scan_docs() -> None:
    """扫描 docs/ 目录，刷新缓存。"""
    global docs_cache
    docs_cache.clear()
    if not DOCS_DIR.is_dir():
        log.warning("目录 %s 不存在，跳过扫描", DOCS_DIR)
        return

    for md in DOCS_DIR.rglob(f"*{DOC_SUFFIX}"):
        key = md.relative_to(DOCS_DIR).with_suffix("").as_posix()
        docs_cache[key] = md.read_text(encoding="utf-8")
    log.info("扫描完成，共加载 %d 个文档", len(docs_cache))


# ---------- MCP 定义 ----------
mcp = FastMCP("DocsHelper", json_response=True)


@mcp.tool()
def list_docs() -> List[str]:
    """返回所有可用文档的相对路径（不含 .md 后缀）。"""
    return sorted(docs_cache.keys())


@mcp.tool()
def read_doc(name: str) -> str:
    """
    读取指定文档的完整内容。
    参数:
        name: 文档相对路径（不含 .md 后缀），例如 'api/auth'
    """
    if name not in docs_cache:
        raise ValueError(f"文档 '{name}' 不存在，可用文档：{list_docs()}")
    return docs_cache[name]


@mcp.tool()
def search_docs(keyword: str) -> List[str]:
    """
    全文关键字检索，返回匹配的文件名列表（不区分大小写）。
    """
    kw = keyword.lower()
    hits = [k for k, v in docs_cache.items() if kw in v.lower()]
    return sorted(hits)


@mcp.resource("doc://{name}")
def doc_resource(name: str) -> str:
    """Resource 形式暴露单个文档，方便在 prompt 中直接 @doc/name 引用。"""
    return read_doc(name)


@mcp.resource("config://reload")
def reload_docs() -> str:
    """手动触发重新扫描 docs/ 目录（热重载）。"""
    scan_docs()
    return f"Reloaded {len(docs_cache)} docs."


# ---------- 启动 ----------
def main() -> None:
    scan_docs()          # 启动时先扫一遍
    mcp.run(transport="stdio")

# ---------- 启动 ----------
# if __name__ == "__main__":
#     scan_docs()          # 启动时先扫一遍
#     mcp.run(transport="sse") stdio
