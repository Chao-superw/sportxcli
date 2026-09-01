"""模块注册表:新增模块的唯一改动点。

想加一个新业务模块(体质测试 / 教学视频 / 竞训管理 ...):
  1. 在 modules/ 下新建一个 Module 子类
  2. 在这里 import 并加进 REGISTRY
就这两步,cli.py 会自动把它挂上去。
"""
from .booking import BookingModule
from .running import RunningModule

# enabled 与否最终由 config.toml 的 [modules.xxx].enabled 决定;
# 这里登记的是"代码里可用的模块全集"。
REGISTRY = [
    BookingModule,
    RunningModule,
    # FitnessTestModule,   # 体质测试(未来)
    # CoursesModule,       # 我的课程(未来)
]
