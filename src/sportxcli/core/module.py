"""模块基类:整个项目"可扩展"的核心契约。

设计意图:
  平台(步道乐跑系)首页是一个功能矩阵:场馆预约 / 校园乐跑 / 体质测试 ...
  它们共享同一套底座(同域名、同 SignMD5 鉴权、同瑞数 WAF、同 school_id 多租户),
  只是业务动作不同。所以把"业务模块"抽象成一等公民:

    - 每个模块实现 Module 接口,声明自己叫什么(name)、提供哪些子命令(register)。
    - 模块通过传入的 ctx 拿到共享底座(会话、签名、ajax 通道、配置),
      自身不关心底座怎么实现。

  新增一个模块(如 running 校园乐跑)就是新写一个 Module 子类丢进 modules/,
  在 REGISTRY 里登记一行,不改动 core、不改动 cli 主干。
  这就是"对扩展开放、对修改封闭"。

CLI 映射:  sportctl <module_name> <verb> [--flags]
           名词是模块, 动词是模块内的动作(clig.dev 的 noun-verb 范式)。
"""
from __future__ import annotations

import abc
import argparse
from typing import Callable


class ModuleContext:
    """底座能力的统一入口,注入给每个模块。

    这里只声明契约;真实实现(会话复用、瑞数令牌注入、页面上下文 ajax、
    验证码 OCR)由 core 提供。模块只管调用,不关心实现细节。这样
    booking 和未来的 running 能共享同一套鉴权/反爬底座。
    """

    def __init__(self, config, session=None):
        self.config = config
        self.session = session  # 浏览器/会话句柄,由 core.session 提供

    # 模块统一通过它发请求:令牌注入、签名、会话复用都在底座内完成。
    def api(self, method: str, path: str, data: dict | None = None):
        raise NotImplementedError("由 core.session 在运行期实现")


class Module(abc.ABC):
    """所有业务模块的基类。"""

    #: CLI 里的名词,如 "booking" / "running"
    name: str = ""
    #: 一句话描述,用于 --help
    help: str = ""

    @abc.abstractmethod
    def register(self, subparsers: "argparse._SubParsersAction") -> None:
        """把本模块的子命令(动词)挂到 CLI 上。

        约定:每个动词 parser 用 set_defaults(_handler=fn) 绑定处理函数,
        fn 签名为 fn(args, ctx: ModuleContext) -> int(返回退出码)。
        """
        raise NotImplementedError

    # 便捷方法:统一动词注册,顺带保证 --json 等公共 flag 一致
    @staticmethod
    def add_verb(
        subparsers: "argparse._SubParsersAction",
        name: str,
        help_text: str,
        handler: Callable,
    ) -> argparse.ArgumentParser:
        p = subparsers.add_parser(name, help=help_text)
        p.add_argument("--json", action="store_true", help="以 JSON 输出(机器/Agent 可读)")
        p.add_argument("--dry-run", action="store_true", help="只演练不产生副作用")
        p.set_defaults(_handler=handler)
        return p
