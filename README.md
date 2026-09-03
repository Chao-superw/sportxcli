# sportxcli

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Python" src="https://img.shields.io/badge/python-3.8%2B-3776AB.svg?logo=python&logoColor=white">
  <img alt="Playwright" src="https://img.shields.io/badge/powered%20by-Playwright-2EAD33.svg">
</p>

> 把「步道乐跑系」这类校园 SaaS 从解包做到自动化的一份完整记录：解包微信小程序、复现签名算法、绕过瑞数动态 WAF，最后落成一个人和 AI Agent 都能直接用的多租户 CLI。

多数逆向文章停在“我把某个 App 抓包解开了”。这个仓库想把后面的事也讲清楚：面对一类挂着动态反爬的第三方 SaaS，怎么从零拆开、复现，再工程化成能复用能扩展的框架。方法论在 [`docs/`](#方法论)，可运行的实现就是这个 CLI。

阅读前请先看 [DISCLAIMER.md](DISCLAIMER.md)。本项目只供本人对有权访问的院校实例做合规的日常使用和技术学习，仓库里不含任何学校的真实域名、凭证或密钥。

## 方法论

想学这类系统怎么被吃透，按顺序读这四篇就够，它们和具体学校无关：

| #  | 文档                                       | 内容                            |
| -- | ---------------------------------------- | ----------------------------- |
| 01 | [解包微信小程序](docs/01-decrypt-wxapkg.md)     | Mac 上定位 `.wxapkg`、解密还原源码的通用手法 |
| 02 | [定位并复现签名算法](docs/02-find-sign-algo.md)   | 在混淆代码里找到 `SignMD5` 鉴权、离线复现它   |
| 03 | [绕过瑞数动态 WAF](docs/03-anti-bot-bypass.md) | 为什么不硬逆向动态令牌，而是让请求在真实浏览器上下文里发出 |
| 04 | [扩展新业务模块](docs/04-extending-modules.md)  | 把这套底座复用到第二个业务（以校园乐跑为例）        |

第 03 篇是整个项目的关键。瑞数 WAF 每个 POST 都要一个动态令牌，由页面里 174KB 的混淆 JS 实时算出，纯 `requests` 直连必被拦。本项目不去逆向这个令牌，而是让所有请求都在真实浏览器页面上下文里、用页面自己的 `jQuery.ajax` 发出，令牌由瑞数的 hook 自动注入。这个思路对一大类动态反爬系统都通用。

## 一套框架为什么能覆盖多所学校

不少高校的体育服务都跑在同一类第三方 SaaS（步道乐跑系）上：场馆预约、校园乐跑、体质测试用的是同一套 H5 部署、同一套 `SignMD5` 鉴权、同一套瑞数动态 WAF，只按 `school_id` 区分学校。底座既然同源，把逆向加自动化沉淀成能复用能扩展的框架，就比写一次性脚本划算。sportxcli 因此沿两个正交方向扩展：租户轴对应不同学校，模块轴对应不同业务。

## 架构：平台底座加可插拔模块

```
sportxcli <module> <verb> [--flags]          ① CLI 适配层(argparse,只解析 + 呈现)
        │
        ▼
   core/                                       ② 核心底座(会话复用 / 令牌注入 / 签名 / OCR)
   ├── config      配置优先级链
   ├── module      Module 基类 + ModuleContext(扩展契约)
   └── session     瑞数令牌自动注入的请求通道
        │
        ▼
   modules/                                    ③ 业务模块(名词)
   ├── booking     场馆预约:slots / book / schedule / orders
   └── running     校园乐跑:rank / records / rule(默认只读)
        │
        ▼
   (可选) MCP server                            ④ Agent 接口层,复用 ② 的底座
```

新增一个模块成本很低：写一个 `Module` 子类，在 `registry.py` 登记一行，`core/` 和 `cli.py` 的主干都不用动。细节见 [docs/04-extending-modules.md](docs/04-extending-modules.md)。

## 设计原则（遵循 [clig.dev](https://clig.dev/)）

- 名词-动词子命令：`sportxcli <module> <verb>`，名词是业务模块，动词是动作。

- 人机双用：每个动词都带 `--json`（机器和 Agent 可读）和 `--dry-run`（演练不产生副作用）；数据走 stdout，日志走 stderr，退出码有意义。这样它既能给人用，也能被 Agent 编排。

- 配置优先级链：命令行 flag 高于环境变量 `CSPORTS_*`，再高于 `config.toml`，最后才是内置默认值。

- 零硬编码：所有学校差异（域名、`school_id`、场馆 ID、密钥）只存在于本地 `config.toml`。

## 快速开始

```bash
pip install -e .                 # 或 pip install playwright ddddocr pillow
playwright install chromium
cp config.example.toml config.toml   # 填入你自己(对有权访问的实例)得到的值

sportxcli --help
sportxcli booking slots --date 2026-09-05           # 查场(只读)
sportxcli booking book  --date 2026-09-05 --times 20:00-21:00 21:00-22:00 --same-area
sportxcli booking schedule --at "2026-09-05 12:00:00" --date 2026-09-06 --times 20:00-21:00
```

## 技术栈

Python、Playwright、ddddocr、argparse。Playwright 负责在浏览器上下文里注入请求、绕过动态 WAF 令牌，ddddocr 做验证码识别。

## License

[MIT](LICENSE)。使用即表示你已阅读并同意 [DISCLAIMER.md](DISCLAIMER.md)。
