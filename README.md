# sportxcli

> 校园体育(步道乐跑系)自动化 CLI,人机双用,配置化的多租户、多模块框架。

这个项目记录了一条完整的路子:解包微信小程序,逆向它的签名算法,应对动态反爬(瑞数 WAF),最后落到一个人和 AI Agent 都能直接用的自动化 CLI。

阅读前请先看 [DISCLAIMER.md](DISCLAIMER.md)。本项目只供本人对有权访问的院校实例做合规的日常使用和技术学习,仓库里不含任何学校的真实域名、凭证或密钥。

## 为什么会有这个项目

不少高校的体育服务都跑在同一类第三方 SaaS(步道乐跑系)上,场馆预约、校园乐跑、体质测试用的是同一套 H5 部署、同一套 `SignMD5` 鉴权、同一套瑞数动态 WAF,再按 `school_id` 区分学校。既然底座是同一套,那么"对这类系统做逆向加自动化"的过程就值得沉淀成一个能复用、能扩展的框架,这就是本项目做的事。

## 设计原则(遵循 [clig.dev](https://clig.dev/))

- 名词-动词子命令:`sportxcli <module> <verb>`,名词是业务模块,动词是动作。
- 人机双用:每个动词都带 `--json`(机器和 Agent 可读)和 `--dry-run`(演练不产生副作用);数据走 stdout,日志走 stderr,退出码有意义。这样它既能给人用,也能被 Agent 编排。
- 配置优先级链:命令行 flag 高于环境变量 `CSPORTS_*`,再高于 `config.toml`,最后才是内置默认值。
- 零硬编码:所有学校差异(域名、`school_id`、场馆 ID、密钥)只存在于本地 `config.toml`。

## 架构:平台底座加可插拔模块

架构沿两个正交的轴扩展,模块轴对应不同业务,租户轴对应不同学校:

```
sportxcli <module> <verb> [--flags]          ① CLI 适配层(argparse,只解析+呈现)
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

新增一个模块的成本很低:写一个 `Module` 子类,再在 `registry.py` 登记一行,`core/` 和 `cli.py` 的主干都不用动。细节见 [docs/04-extending-modules.md](docs/04-extending-modules.md)。

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

## 文档

- [docs/01-decrypt-wxapkg.md](docs/01-decrypt-wxapkg.md):Mac 微信小程序解包(通用方法)
- [docs/02-find-sign-algo.md](docs/02-find-sign-algo.md):定位并复现签名/加密算法
- [docs/03-anti-bot-bypass.md](docs/03-anti-bot-bypass.md):瑞数动态令牌,为何用浏览器上下文而非硬逆向
- [docs/04-extending-modules.md](docs/04-extending-modules.md):如何扩展新模块(以校园乐跑为例)

## 技术栈

Python、Playwright(浏览器上下文注入,绕过动态 WAF 令牌)、ddddocr(验证码 OCR)、argparse。

## License

[MIT](LICENSE)。使用即表示你已阅读并同意 [DISCLAIMER.md](DISCLAIMER.md)。
