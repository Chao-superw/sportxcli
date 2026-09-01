"""场馆预约模块(现有能力的模块化封装)。

真实抢场逻辑在本地私有目录中(经过实跑验证),不随仓库发布。这里作为
CLI 模块的适配层:声明子命令、解析参数、调用底座 api()。把成熟逻辑接进来时
只需在各 handler 内转调,core 与 cli 主干无需改动。
"""
from __future__ import annotations

import json as _json

from ..core.module import Module, ModuleContext


class BookingModule(Module):
    name = "booking"
    help = "场馆预约:查场 / 抢场 / 定时 / 我的订单"

    def register(self, subparsers) -> None:
        # slots:只读查询,最安全,适合先验证连通性
        p = self.add_verb(subparsers, "slots", "列出某天可约场次(只读)", self._slots)
        p.add_argument("--date", required=True, help="YYYY-MM-DD")

        # book:立即抢
        p = self.add_verb(subparsers, "book", "立即抢场并产生未支付订单", self._book)
        p.add_argument("--date", required=True)
        p.add_argument("--time", dest="time_range", help="单时段,如 17:00-18:00")
        p.add_argument("--times", nargs="+", help="多时段连打,如 20:00-21:00 21:00-22:00")
        p.add_argument("--same-area", action="store_true", help="多时段要求同一片场地")
        p.add_argument("--area", dest="area_name", default="", help="指定场地名;留空=任意可约")

        # schedule:定时抢(放场时刻卡点开抢)
        p = self.add_verb(subparsers, "schedule", "定时抢场(到放场时刻自动开抢)", self._schedule)
        p.add_argument("--at", required=True, help='放场时刻,如 "2026-09-05 12:00:00"')
        p.add_argument("--date", required=True)
        p.add_argument("--times", nargs="+", required=True)
        p.add_argument("--same-area", action="store_true")

        # orders:查/取消我的订单(复用抓到的 orderDetails / cancelOrder)
        p = self.add_verb(subparsers, "orders", "查看我的订单;--cancel 取消", self._orders)
        p.add_argument("--cancel", metavar="ORDER_ID", help="取消指定订单")

    # ---- handlers:签名 fn(args, ctx) -> int ----
    # 下面为接入点占位:实盘逻辑从本地私有实现转调即可。
    def _slots(self, args, ctx: ModuleContext) -> int:
        print(f"[booking.slots] date={args.date} (接入 get_interval)")
        return 0

    def _book(self, args, ctx: ModuleContext) -> int:
        if args.dry_run:
            print("[booking.book] dry-run:仅演练,不产生订单")
        print(f"[booking.book] date={args.date} times={args.times or [args.time_range]} "
              f"same_area={args.same_area}")
        return 0

    def _schedule(self, args, ctx: ModuleContext) -> int:
        print(f"[booking.schedule] at={args.at} date={args.date} times={args.times}")
        return 0

    def _orders(self, args, ctx: ModuleContext) -> int:
        if args.cancel:
            print(f"[booking.orders] cancel order {args.cancel}")
        else:
            print("[booking.orders] 列出我的订单 (接入 mySubscribe/orderDetails)")
        return 0
