"""
maque MCP Server - API 文档查询服务

让 AI Agent 能够查询 maque 的可用功能，避免重复造轮子。

启动方式:
    python -m maque.mcp_server

配置 Claude Code (~/.claude.json):
    {
        "mcpServers": {
            "maque": {
                "command": "python",
                "args": ["-m", "maque.mcp_server"]
            }
        }
    }
"""

import ast
import inspect
import pkgutil
import importlib
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# 核心模块列表（按重要性排序）
CORE_MODULES = [
    ("mllm", "多模态 LLM 客户端", ["OpenAIClient", "GeminiClient", "MllmClient", "TableProcessor"]),
    ("embedding", "文本/多模态 Embedding", ["TextEmbedding"]),
    ("async_api", "异步并发执行", ["ConcurrentRequester", "ConcurrentExecutor"]),
    ("retriever", "RAG 检索（ChromaDB）", ["ChromaRetriever", "Document"]),
    ("clustering", "聚类分析", ["ClusterAnalyzer", "ClusteringResult"]),
    ("io", "文件 IO 操作", ["yaml_load", "yaml_dump", "json_load", "json_dump", "jsonl_load", "jsonl_dump"]),
    ("nlp", "NLP 工具", ["parse_to_obj", "parse_to_code"]),
    ("performance", "性能监控", ["MeasureTime"]),
    ("cv", "计算机视觉", ["image", "video"]),
    ("llm", "LLM 推理服务", ["LLMServer"]),
]


@dataclass
class APIInfo:
    """API 信息"""
    name: str
    module: str
    type: str  # 'class' | 'function' | 'module'
    signature: str
    docstring: str
    example: str = ""


def get_maque_root() -> Path:
    """获取 maque 包的根目录"""
    import maque
    return Path(maque.__file__).parent


def extract_docstring_from_source(file_path: Path, target_name: str) -> Optional[str]:
    """从源码中提取指定类或函数的 docstring（不导入模块）"""
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == target_name:
                    return ast.get_docstring(node)
        return None
    except Exception:
        return None


def extract_class_info_from_source(file_path: Path, class_name: str) -> Optional[APIInfo]:
    """从源码提取类信息"""
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                docstring = ast.get_docstring(node) or "无文档"

                # 提取 __init__ 签名
                init_sig = ""
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        args = []
                        for arg in item.args.args[1:]:  # 跳过 self
                            arg_str = arg.arg
                            if arg.annotation:
                                arg_str += f": {ast.unparse(arg.annotation)}"
                            args.append(arg_str)

                        # 处理默认值
                        defaults = item.args.defaults
                        num_defaults = len(defaults)
                        num_args = len(args)
                        for i, default in enumerate(defaults):
                            arg_idx = num_args - num_defaults + i
                            try:
                                default_val = ast.unparse(default)
                                args[arg_idx] += f" = {default_val}"
                            except Exception:
                                pass

                        init_sig = f"({', '.join(args)})"
                        break

                return APIInfo(
                    name=class_name,
                    module=str(file_path.relative_to(get_maque_root().parent)).replace('/', '.').replace('.py', ''),
                    type='class',
                    signature=f"class {class_name}{init_sig}",
                    docstring=docstring[:500] if len(docstring) > 500 else docstring,
                )
        return None
    except Exception as e:
        return None


def search_in_module(module_path: Path, keyword: str) -> list[APIInfo]:
    """在模块中搜索关键词"""
    results = []
    keyword_lower = keyword.lower()

    try:
        source = module_path.read_text(encoding='utf-8')
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node) or ""
                if keyword_lower in node.name.lower() or keyword_lower in docstring.lower():
                    info = extract_class_info_from_source(module_path, node.name)
                    if info:
                        results.append(info)

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 跳过私有函数
                if node.name.startswith('_'):
                    continue
                docstring = ast.get_docstring(node) or ""
                if keyword_lower in node.name.lower() or keyword_lower in docstring.lower():
                    # 构建签名
                    args = []
                    for arg in node.args.args:
                        arg_str = arg.arg
                        if arg.annotation:
                            try:
                                arg_str += f": {ast.unparse(arg.annotation)}"
                            except Exception:
                                pass
                        args.append(arg_str)

                    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                    sig = f"{prefix} {node.name}({', '.join(args)})"

                    results.append(APIInfo(
                        name=node.name,
                        module=str(module_path.relative_to(get_maque_root().parent)).replace('/', '.').replace('.py', ''),
                        type='function',
                        signature=sig,
                        docstring=docstring[:300] if len(docstring) > 300 else docstring,
                    ))
    except Exception:
        pass

    return results


def search_maque(keyword: str) -> list[APIInfo]:
    """搜索 maque 中的 API"""
    results = []
    root = get_maque_root()

    for py_file in root.rglob("*.py"):
        # 跳过测试和私有模块
        if '__pycache__' in str(py_file) or py_file.name.startswith('_'):
            continue
        results.extend(search_in_module(py_file, keyword))

    return results[:20]  # 限制结果数量


def get_module_info(module_name: str) -> str:
    """获取模块的详细使用说明"""

    # 预定义的模块使用示例
    MODULE_EXAMPLES = {
        "mllm": '''
# OpenAI 兼容客户端（vLLM、通义千问、DeepSeek 等）
from maque.mllm import OpenAIClient

client = OpenAIClient(
    base_url="https://api.example.com/v1",
    api_key="your-key",
    model="qwen-vl-plus",
    concurrency_limit=10,  # 并发数
    max_qps=50,            # QPS 限制
    retry_times=3,         # 自动重试
)

# 单条调用
result = await client.chat_completions(messages)

# 批量异步调用
results = await client.chat_completions_batch(messages_list, show_progress=True)

# Gemini 客户端
from maque.mllm import GeminiClient

gemini = GeminiClient(
    api_key="your-google-api-key",
    model="gemini-2.5-flash",
    concurrency_limit=10,
)
results = await gemini.chat_completions(messages_list)
''',
        "embedding": '''
from maque.embedding import TextEmbedding

embedding = TextEmbedding(
    base_url="http://localhost:8001",
    model="BAAI/bge-m3",
    task="retrieval.query",  # 可选：text-matching, retrieval.passage 等
)

# 单条/批量获取向量
vectors = embedding.embed("查询文本")
vectors = embedding.embed(["文本1", "文本2", "文本3"])

# 异步批量
vectors = await embedding.aembed(texts)
''',
        "async_api": '''
from maque.async_api import ConcurrentRequester, ConcurrentExecutor

# 方式1: HTTP 请求管理器
requester = ConcurrentRequester(
    concurrency_limit=5,
    max_qps=10,
    timeout=30,
    retry_times=3,
)

results, tracker = await requester.process_requests(
    request_params=params,
    url='http://api.example.com/endpoint',
    method='POST',
    show_progress=True,
)

# 方式2: 通用并发执行器
executor = ConcurrentExecutor(
    concurrency_limit=5,
    max_qps=10,
    retry_times=3
)

async def my_task(data):
    return f"processed: {data}"

results, _ = await executor.execute_batch(
    async_func=my_task,
    tasks_data=["task1", "task2", "task3"]
)
''',
        "io": '''
from maque.io import load_yaml, save_yaml, load_json, save_json, load_jsonl, save_jsonl

# YAML
data = load_yaml("config.yaml")
save_yaml(data, "output.yaml")

# JSON
data = load_json("data.json")
save_json(data, "output.json")

# JSONL
records = load_jsonl("data.jsonl")
save_jsonl(records, "output.jsonl")
''',
        "retriever": '''
from maque.embedding import TextEmbedding
from maque.retriever import ChromaRetriever, Document

# 初始化
embedding = TextEmbedding(base_url="...", model="...")
retriever = ChromaRetriever(
    embedding=embedding,
    persist_dir="./chroma_db",
    collection_name="my_data"
)

# 批量插入文档
documents = [
    Document(id="1", content="文本内容", metadata={"category": "tech"}),
    Document(id="2", content="另一段文本", metadata={"category": "news"}),
]
retriever.upsert_batch(documents, batch_size=32, skip_existing=True)

# 检索
results = retriever.search("查询文本", top_k=10)
''',
        "clustering": '''
from maque.clustering import ClusterAnalyzer

analyzer = ClusterAnalyzer(algorithm="hdbscan", min_cluster_size=15)

# 从 ChromaDB 直接分析
result = analyzer.analyze_chroma(
    persist_dir="./chroma_db",
    collection_name="my_data",
    output_dir="./results",
    sample_size=10000,  # 可选：采样
    where={"category": "tech"},  # 可选：过滤
)

# 或直接分析向量
result = analyzer.fit(embeddings)  # numpy array
''',
        "performance": '''
from maque.performance import MeasureTime

# 作为上下文管理器
with MeasureTime("my_task"):
    # 你的代码
    pass

# 带 GPU 监控
with MeasureTime("gpu_task", gpu=True):
    # GPU 相关代码
    pass
''',
        "nlp": '''
from maque.nlp.parser import parse_to_obj, parse_to_code

# 从 LLM 输出中提取 JSON 对象
text = 'some text ```json\n{"key": "value"}\n``` more text'
obj = parse_to_obj(text)  # {"key": "value"}

# 提取代码块
code = parse_to_code(text, lang="python")
''',
    }

    if module_name in MODULE_EXAMPLES:
        return MODULE_EXAMPLES[module_name]

    # 尝试从源码提取
    root = get_maque_root()
    module_path = root / module_name

    if module_path.is_dir():
        init_file = module_path / "__init__.py"
        if init_file.exists():
            try:
                source = init_file.read_text(encoding='utf-8')
                tree = ast.parse(source)
                docstring = ast.get_docstring(tree)
                if docstring:
                    return docstring
            except Exception:
                pass

    return f"模块 {module_name} 暂无详细使用示例。请使用 search_maque_api 搜索具体功能。"


def list_all_modules() -> str:
    """列出所有核心模块"""
    lines = ["# maque 核心模块\n"]

    for module, desc, exports in CORE_MODULES:
        lines.append(f"## {module}")
        lines.append(f"  {desc}")
        lines.append(f"  主要导出: {', '.join(exports)}")
        lines.append("")

    lines.append("\n使用 `get_module_usage(module_name)` 获取详细用法")
    return "\n".join(lines)


# CLI 命令组映射
CLI_GROUPS = {
    "config": "配置管理",
    "mllm": "多模态 LLM 操作",
    "llm": "LLM 推理服务",
    "data": "数据处理工具",
    "embedding": "Embedding 服务",
    "system": "系统工具",
    "git": "Git 辅助命令",
    "service": "服务管理",
    "doctor": "诊断工具",
    "mcp": "MCP 服务",
}


@dataclass
class CLICommand:
    """CLI 命令信息"""
    name: str
    group: str  # 空字符串表示顶级命令
    description: str
    signature: str


def extract_cli_commands() -> list[CLICommand]:
    """提取所有 CLI 命令"""
    commands = []
    root = get_maque_root()

    # 1. 提取顶级命令（从 __main__.py 的 NewCli 类）
    main_file = root / "__main__.py"
    if main_file.exists():
        commands.extend(_extract_commands_from_class(main_file, "NewCli", ""))

    # 2. 提取分组命令（从 cli/groups/*.py）
    groups_dir = root / "cli" / "groups"
    if groups_dir.exists():
        for py_file in groups_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            # 从文件名推断 group 名称
            group_name = py_file.stem
            if group_name == "mllm_simple":
                continue  # 跳过简化版
            commands.extend(_extract_commands_from_file(py_file, group_name))

    return commands


def _extract_commands_from_class(file_path: Path, class_name: str, group: str) -> list[CLICommand]:
    """从指定类中提取命令"""
    commands = []
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # 跳过私有方法和特殊方法
                        if item.name.startswith('_'):
                            continue
                        # 跳过属性方法（没有实际功能）
                        if any(isinstance(d, ast.Name) and d.id == 'property' for d in item.decorator_list):
                            continue

                        docstring = ast.get_docstring(item) or "无描述"
                        # 只取 docstring 第一行
                        desc = docstring.split('\n')[0].strip()

                        # 构建签名
                        args = []
                        for arg in item.args.args:
                            if arg.arg in ('self', 'cls'):
                                continue
                            args.append(arg.arg)
                        sig = f"({', '.join(args)})" if args else "()"

                        commands.append(CLICommand(
                            name=item.name,
                            group=group,
                            description=desc,
                            signature=sig,
                        ))
    except Exception:
        pass
    return commands


def _extract_commands_from_file(file_path: Path, group_name: str) -> list[CLICommand]:
    """从文件中提取 Group 类的命令"""
    commands = []
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith('Group'):
                commands.extend(_extract_commands_from_class(file_path, node.name, group_name))
                break  # 每个文件只处理一个 Group 类
    except Exception:
        pass
    return commands


def list_cli_commands() -> str:
    """列出所有 CLI 命令"""
    commands = extract_cli_commands()

    # 分组显示
    top_level = [c for c in commands if not c.group]
    grouped = {}
    for c in commands:
        if c.group:
            if c.group not in grouped:
                grouped[c.group] = []
            grouped[c.group].append(c)

    lines = ["# maque CLI 命令\n"]

    # 顶级命令
    if top_level:
        lines.append("## 顶级命令")
        lines.append("用法: `maque <command> [args]`\n")
        for cmd in sorted(top_level, key=lambda x: x.name):
            lines.append(f"- **{cmd.name}**{cmd.signature}: {cmd.description}")
        lines.append("")

    # 分组命令
    lines.append("## 分组命令")
    lines.append("用法: `maque <group> <command> [args]`\n")

    for group_name in sorted(grouped.keys()):
        group_desc = CLI_GROUPS.get(group_name, "")
        lines.append(f"### {group_name}" + (f" - {group_desc}" if group_desc else ""))
        for cmd in sorted(grouped[group_name], key=lambda x: x.name):
            lines.append(f"- **{cmd.name}**{cmd.signature}: {cmd.description}")
        lines.append("")

    return "\n".join(lines)


# 创建 MCP Server
server = Server("maque-docs")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="search_maque_api",
            description="搜索 maque 库中的 API（类、函数、模块）。用于查找可复用的功能，避免重复造轮子。",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词，如 'embedding', 'llm', 'async', 'retry' 等"
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="get_module_usage",
            description="获取 maque 指定模块的详细使用示例。",
            inputSchema={
                "type": "object",
                "properties": {
                    "module": {
                        "type": "string",
                        "description": "模块名称，如 'mllm', 'embedding', 'async_api', 'io', 'retriever', 'clustering'"
                    }
                },
                "required": ["module"]
            }
        ),
        Tool(
            name="list_maque_modules",
            description="列出 maque 所有核心模块及其功能概述。",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_cli_commands",
            description="列出 maque 所有可用的 CLI 命令，包括顶级命令和分组命令。",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""

    if name == "search_maque_api":
        keyword = arguments.get("keyword", "")
        results = search_maque(keyword)

        if not results:
            return [TextContent(type="text", text=f"未找到与 '{keyword}' 相关的 API")]

        lines = [f"# 搜索结果: '{keyword}'\n"]
        for api in results:
            lines.append(f"## {api.name}")
            lines.append(f"  模块: `{api.module}`")
            lines.append(f"  类型: {api.type}")
            lines.append(f"  签名: `{api.signature}`")
            if api.docstring:
                lines.append(f"  说明: {api.docstring}")
            lines.append("")

        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "get_module_usage":
        module = arguments.get("module", "")
        usage = get_module_info(module)
        return [TextContent(type="text", text=f"# {module} 模块使用示例\n\n```python{usage}\n```")]

    elif name == "list_maque_modules":
        return [TextContent(type="text", text=list_all_modules())]

    elif name == "list_cli_commands":
        return [TextContent(type="text", text=list_cli_commands())]

    return [TextContent(type="text", text=f"未知工具: {name}")]


async def main_stdio():
    """以 stdio 模式启动 MCP Server（Claude Code 自动管理）"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main_sse(host: str = "0.0.0.0", port: int = 8765):
    """
    以 SSE 模式启动 MCP Server（独立 HTTP 服务）

    启动: python -m maque.mcp_server --sse --port 8765
    配置: claude mcp add maque-remote --transport sse --url http://localhost:8765/sse
    """
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route
    import uvicorn

    sse = SseServerTransport("/messages")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )

    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)

    app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ]
    )

    print(f"🚀 MCP Server (SSE) running at http://{host}:{port}")
    print(f"   配置命令: claude mcp add maque --transport sse --url http://localhost:{port}/sse")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import sys
    import asyncio

    if "--sse" in sys.argv:
        # SSE 模式：独立 HTTP 服务
        port = 8765
        for i, arg in enumerate(sys.argv):
            if arg == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        main_sse(port=port)
    else:
        # stdio 模式：Claude Code 自动管理
        asyncio.run(main_stdio())
