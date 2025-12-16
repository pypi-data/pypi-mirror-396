"""
InnerLoop Tooling Subpackage

Provides curryable, stateful, and specialized tools for the agent loop.

Bash (curryable):
    from innerloop.tooling import bash

    # Full reign
    loop = Loop(model="...", tools=[bash])

    # Constrained
    safe_bash = bash(
        allow={"make": "Run make targets"},
        deny=["rm -rf", "sudo"],
        usage="Use make for builds"
    )
    loop = Loop(model="...", tools=[safe_bash])

Todo (stateful, auto-managed):
    from innerloop import Loop, TODO_TOOLS

    loop = Loop(model="...", tools=TODO_TOOLS)
    response = loop.run("Add 3 todos and complete them")
    print(len(loop.todos))  # Access state via loop.todos

Filesystem:
    from innerloop.tooling import read, write, edit, glob, ls, grep
    from innerloop.tooling import FS_TOOLS, SAFE_FS_TOOLS

    loop = Loop(model="...", tools=SAFE_FS_TOOLS)  # read-only tools

Web:
    from innerloop.tooling import fetch, download, search, WEB_TOOLS

    loop = Loop(model="...", tools=WEB_TOOLS)
"""

# Base infrastructure (re-exported)
from .base import LocalTool, ToolContext, tool

# Curryable bash
from .bash import BashConfig, BashTool, bash

# Filesystem tools
from .filesystem import (
    FS_TOOLS,
    SAFE_FS_TOOLS,
    SecurityError,
    chunk,
    edit,
    glob,
    grep,
    ls,
    read,
    stat,
    write,
)

# Todo tools (state is auto-managed via ToolContext)
from .todo import (
    TODO_TOOLS,
    Status,
    Todo,
    TodoState,
    add_todo,
    list_todos,
    mark_done,
    mark_skip,
    rehydrate_from_session,
)

# Web tools - optional, requires [web] extra
try:
    from .web import WEB_TOOLS, download, fetch, search

    _WEB_AVAILABLE = True
except ImportError:
    # Web extra not installed - provide placeholder that raises helpful error
    _WEB_AVAILABLE = False
    WEB_TOOLS: list[object] = []  # type: ignore[no-redef]

    def _web_not_installed(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise ImportError(
            "Web tools require the 'web' extra. "
            "Install with: pip install innerloop[web]"
        )

    fetch = download = search = _web_not_installed  # type: ignore[assignment]

# Combined bundles
ALL_TOOLS = [*FS_TOOLS, bash, *WEB_TOOLS]

__all__ = [
    # Base
    "tool",
    "LocalTool",
    "ToolContext",
    # Bash
    "bash",
    "BashTool",
    "BashConfig",
    # Filesystem
    "read",
    "write",
    "edit",
    "glob",
    "ls",
    "grep",
    "stat",
    "chunk",
    "FS_TOOLS",
    "SAFE_FS_TOOLS",
    "SecurityError",
    # Todo
    "TodoState",
    "Todo",
    "Status",
    "rehydrate_from_session",
    "add_todo",
    "list_todos",
    "mark_done",
    "mark_skip",
    "TODO_TOOLS",
    # Web (available if [web] extra installed)
    "fetch",
    "download",
    "search",
    "WEB_TOOLS",
    # Bundles
    "ALL_TOOLS",
]
