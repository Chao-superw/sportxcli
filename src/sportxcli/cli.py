"""sportxcli 入口:sportxcli <module> <verb> [--flags]

设计遵循 clig.dev:
  - 名词-动词子命令(名词=业务模块,动词=模块内动作)
  - 每个动词自带 --json(机器/Agent 可读)与 --dry-run(演练不产生副作用)
  - 有意义的退出码;错误走 stderr,数据走 stdout

扩展方式:模块从 modules/registry.py 的 REGISTRY 自动装配,主干无需改动。
"""
from __future__ import annotations

import argparse
import sys

from .core.config import Config
from .core.module import ModuleContext
from .modules.registry import REGISTRY


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sportxcli",
        description="校园体育(步道乐跑系)自动化 CLI,人机双用,配置化多租户/多模块。",
    )
    parser.add_argument("-c", "--config", default="config.toml", help="配置文件路径")
    parser.add_argument("--version", action="version", version="sportxcli 0.1.0")

    module_sub = parser.add_subparsers(dest="module", metavar="<module>")
    # 从注册表自动挂载每个模块及其动词
    for cls in REGISTRY:
        mod = cls()
        mp = module_sub.add_parser(mod.name, help=mod.help)
        verbs = mp.add_subparsers(dest="verb", metavar="<verb>")
        mod.register(verbs)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "module", None) or not getattr(args, "_handler", None):
        parser.print_help()
        return 2

    config = Config.load(args.config)
    ctx = ModuleContext(config)
    try:
        return int(args._handler(args, ctx) or 0)
    except KeyboardInterrupt:
        print("已中断", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
