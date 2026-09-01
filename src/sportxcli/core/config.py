"""配置加载:实现 flag > env > config.toml > 默认 的优先级链(clig.dev 惯例)。

只做加载与合并,不含任何学校真实值。真实值来自用户本地 config.toml。
"""
from __future__ import annotations

import os
import pathlib
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # 3.9 / 3.10 回退到 tomli(可选)
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:
        tomllib = None  # 无 TOML 解析器时仍可运行(仅无法读取 config.toml)

ENV_PREFIX = "CSPORTS_"


class Config:
    """扁平化 + 分层访问的配置对象。

    优先级: 显式 override(命令行) > 环境变量 > config.toml > 内置默认。
    """

    def __init__(self, data: dict[str, Any]):
        self._d = data

    # -- 分层读取: cfg.get("modules.booking.stadium_id") --
    def get(self, dotted: str, default: Any = None) -> Any:
        # 环境变量优先: modules.booking.stadium_id -> CSPORTS_MODULES_BOOKING_STADIUM_ID
        env_key = ENV_PREFIX + dotted.upper().replace(".", "_")
        if env_key in os.environ:
            return os.environ[env_key]
        node: Any = self._d
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def module(self, name: str) -> dict[str, Any]:
        return (self._d.get("modules") or {}).get(name, {}) or {}

    @classmethod
    def load(cls, path: str | os.PathLike | None = None) -> "Config":
        p = pathlib.Path(path) if path else pathlib.Path("config.toml")
        data: dict[str, Any] = {}
        if p.exists() and tomllib is not None:
            with open(p, "rb") as f:
                data = tomllib.load(f)
        return cls(data)
