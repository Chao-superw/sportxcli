# 扩展一个新模块(以「校园乐跑」为例)

这篇文档回答一个具体问题:当前架构能不能优雅地容纳未来的新板块(校园乐跑、体质测试、教学视频等)?答案是能,而且新增一个模块不需要改动 `core/` 或 `cli.py` 主干。

## 为什么能

步道乐跑系首页是一个功能矩阵:

```
我的课程 | 校园乐跑 | 体质测试 | 教学视频 | 场馆预约 | 竞训管理 | 课外锻炼
```

这些板块共享同一套底座:同一部署域名、同一 `SignMD5` 鉴权、同一瑞数 WAF 动态令牌、同一 `school_id` 多租户。区别只在业务动作上。所以架构沿两个正交的轴扩展:

- 模块轴:`booking` / `running` / `fitness` 等,对应不同业务能力。
- 租户轴:`school_id`,让同一模块适配不同学校。

CLI 把这两个轴映射成 `sportctl <module> <verb>`,名词是模块,动词是动作。

## 三步加一个模块

以校园乐跑 `running` 为例(见 [`modules/running.py`](../src/campus_sports/modules/running.py)):

1. 写一个 `Module` 子类,声明 `name` / `help`,在 `register()` 里挂动词:

```python
from ..core.module import Module, ModuleContext

class RunningModule(Module):
    name = "running"
    help = "校园乐跑:排行 / 记录 / 规则(默认只读)"

    def register(self, subparsers):
        self.add_verb(subparsers, "rank", "查看乐跑排行榜(只读)", self._rank)
        self.add_verb(subparsers, "records", "查看我的乐跑记录(只读)", self._records)

    def _rank(self, args, ctx: ModuleContext):
        data = ctx.api("POST", "running/rank", {...})   # 复用底座:令牌注入/签名/会话全自动
        print(data); return 0
```

2. 在 [`registry.py`](../src/campus_sports/modules/registry.py) 加一行:`REGISTRY = [BookingModule, RunningModule]`
3. 在 config 里加一段 `[modules.running]`(见 `config.example.toml`)。

完成后,`sportctl running --help` 会自动出现,`core` 与 `cli` 主干一行未改。

## 合规边界(校园乐跑尤其要注意)

校园乐跑是 GPS 轨迹型业务,它天然分成两类能力:

| 能力 | 性质 | 本项目态度 |
|---|---|---|
| 乐跑排行 / 记录 / 规则 | 只读查询 | 可实现(与"看自己的成绩"无异) |
| 开始乐跑 → 提交轨迹 | 写入运动数据 | 默认不实现;`enabled=false` |

"开始乐跑"若由脚本自动生成并提交轨迹,等于伪造体育成绩,可能违反学校学籍或体测规定,性质和"本人正常约场"完全不同。所以本骨架默认只规划只读能力,把"是否落地写入类能力"留给使用者按其院校规定自行判断,并自负后果。这与本项目的整体定位一致(见 `DISCLAIMER.md`)。
