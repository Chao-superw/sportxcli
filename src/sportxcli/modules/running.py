"""校园乐跑模块(未来扩展的骨架,用来证明架构可扩展)。

这个文件存在的意义:展示"新增一个业务模块"到底要写多少东西。答案是:
  1) 继承 Module;2) 声明 name/help;3) 在 register() 里挂动词;
  4) 在 registry.py 里加一行登记。
  完全不需要改动 core 或 cli 主干。

合规边界(重要):
  校园乐跑是 GPS 轨迹型业务。本骨架默认只规划【只读查询】能力
  (排行 rank / 记录 records / 规则 rule),对应界面上的"乐跑排行/记录/规则"。
  "开始乐跑"(提交轨迹)涉及伪造运动数据,默认不实现、config 里默认 enabled=false。
  是否落地由使用者按其院校规定自行判断。详见 docs/04-extending-modules.md。
"""
from __future__ import annotations

from ..core.module import Module, ModuleContext


class RunningModule(Module):
    name = "running"
    help = "校园乐跑:排行 / 记录 / 规则(默认只读)"

    def register(self, subparsers) -> None:
        self.add_verb(subparsers, "rank", "查看乐跑排行榜(只读)", self._rank)
        self.add_verb(subparsers, "records", "查看我的乐跑记录(只读)", self._records)
        self.add_verb(subparsers, "rule", "查看乐跑规则(只读)", self._rule)

    def _rank(self, args, ctx: ModuleContext) -> int:
        print("[running.rank] 只读:排行榜 (接入乐跑排行接口)")
        return 0

    def _records(self, args, ctx: ModuleContext) -> int:
        print("[running.records] 只读:我的乐跑记录")
        return 0

    def _rule(self, args, ctx: ModuleContext) -> int:
        print("[running.rule] 只读:乐跑规则")
        return 0
