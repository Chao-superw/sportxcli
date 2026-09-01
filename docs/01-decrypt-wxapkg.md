# 01 · Mac 微信小程序解包

目标是拿到小程序前端 JS,好分析它的鉴权和签名逻辑。这里只讲通用方法,不含任何具体系统的密钥。

## 1. 定位缓存

Mac 微信会把用过的小程序包缓存到本地:

```
~/Library/Containers/com.tencent.xinWeChat/Data/.../applet/packages/<appid>/
```

每个 `<appid>` 目录下是加密后的 `.wxapkg` 包。先在小程序里正常访问一遍目标页面,确保包已落盘。

## 2. 解密(V1MMWX 格式)

Mac 端的包不是标准 wxapkg,而是加了一层加密的 `V1MMWX` 格式。解密分几步:

1. 头部 6 字节是魔数 `V1MMWX`,跳过。
2. 用 `PBKDF2(salt=<appid>, ...)` 派生 AES key,对前 1024 字节做 `AES-128-CBC` 解密,取前 1023 字节为头部。
3. 剩余部分用一个单字节 XOR(key 与 appid 相关)还原。
4. 拼接后得到标准 wxapkg,魔数应为 `0xBE`。

实现细节见仓库历史里的 `wxapkg_decrypt.py`,它是社区通用算法的一个实现。

## 3. 拆包

标准 wxapkg 的结构是 `[header][index][data]`。按 index 里记录的 (name, offset, size) 把每个文件切出来写盘,就能还原出 `app-service.js`、`*.html`、`static/*` 等前端源码。

## 4. 下一步

拿到源码后,进入 [02-find-sign-algo.md](02-find-sign-algo.md),在还原出的 JS 里定位签名函数。
