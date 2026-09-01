# 03 · 应对动态反爬(瑞数 WAF):为什么用浏览器上下文而非硬逆向

## 问题

即使签名算好了,直连接口仍会被拦。观察发现,每个 POST 的 URL 上都带一个动态令牌,例如 `?chBKhbg9=<一长串>`。这是瑞数信息(RiverSafe)动态防护的典型特征:

- 页面加载一段 100KB 以上的混淆 JS;
- 它 hook 了 `XMLHttpRequest` / `fetch`,在每次请求发出的瞬间现算一个令牌拼到 URL 上;
- 令牌与 cookie、时间、环境强绑定,而且脚本高度混淆、频繁更新。

## 两条路

| 方案 | 做法 | 代价 |
|---|---|---|
| A. 硬逆向令牌 | 逆向那段混淆 JS,用 Python 复现令牌算法 | 极高:混淆重、易变,维护成本巨大 |
| B. 借用页面上下文(本项目选择) | 用 Playwright 打开真实页面,让页面自己的 JS 发请求 | 低:令牌由瑞数 hook 自动注入,完全绕开逆向 |

## 方案 B 的关键点

1. 会话复用:首次人工登录后用 `storage_state` 保存 cookie(含 PHPSESSID 与瑞数 cookie),后续自动化直接复用,不必重复登录。
2. 在页面上下文里发请求:所有业务请求通过 `page.evaluate(...)` 调用页面自带的 `jQuery.ajax` / `fetch` 发出,这样瑞数的 hook 会自动给 URL 拼上合法令牌。

```js
// 在页面上下文执行:令牌由瑞数自动注入,我们不碰它
(method, path, data) => new Promise((resolve) => {
  window.$.ajax({
    url: location.origin + '/.../index.php/' + path,
    type: method, data, dataType: 'json',
    success: r => resolve({ok: true, data: r}),
    error:   x => resolve({ok: false, status: x.status}),
  });
})
```

3. 验证码:剩下的图形验证码用 `ddddocr` 识别;识别前按亮度做前景提取预处理,失败自动刷新重试。

## 结论

对抗动态 WAF 不一定要硬刚混淆 JS。把请求放回它本来该在的执行环境里,是更省力也更稳健的思路,这也是本项目 `core/session` 层的设计核心。
