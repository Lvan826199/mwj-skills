# 各技术栈起服务与喂数据

## Vue 3 + Vite（AiTestProject / game-auto / MSCA 前端）

- 前端单独开一个端口：`npx vite --port 5391`。本机跑 Vite 必须加 `CHOKIDAR_USEPOLLING=true`，否则 inotify 额度用完会报 ENOSPC 退出。
- **先确认协议**：开了 `basicSsl` 的项目是 https，用 http 探测会一直返回 000。探活命令：`curl -sk https://127.0.0.1:<port>`。`shot.py` 已经默认忽略自签证书。
- 喂数据有两种方式：
  - 起真实后端，后端指向临时库，例如 `uv run python __main__.py --port 18000`；
  - 不起后端，用 `mock` 拦截接口。WebSocket 需要另写 Playwright 脚本调用 `page.route_web_socket`。
- 登录态：
  - 需要真实 token 时，参照 AiTestProject `scripts/lib/auth_session.cjs`：先取 captcha，再 login，然后往 localStorage 写 `user` 和 `workspace`；
  - 只截静态 UI 时，直接在 `local_storage` 里塞一个假的用户对象。
- 安全上下文：剪贴板、摄像头这类 API 只在 https 或 localhost 下可用。从内网 IP 访问时行为会不一样，涉及这类 API 的改动要用内网 IP 验一次。
- 组件库主题：MSCA 是 Element 暗色主题（`class="dark"`），截图时要确认暗色主题已经生效。

## Electron（Sujian / MSCA 外壳）

本机没有显示器，也没有 Xvfb：

- 先 `unset ELECTRON_RUN_AS_NODE`。
- 普通窗口在 headless 下会段错误。用一个包装 app 把 `BrowserWindow` 强制设成 `webPreferences.offscreen: true`。
- 启动参数：`--ozone-platform=headless --disable-gpu --no-sandbox --no-zygote --remote-debugging-port=9333`，然后用 CDP 驱动（Node 22 自带 WebSocket）。
- 启动和驱动要写在**同一条命令**里；必要时需要关掉沙箱。
- 截图如果返回空白（约 87 字节），改用 `Runtime.evaluate` 读 DOM 来判断；canvas 导出成 JPEG 再看。
- 用 `XDG_CONFIG_HOME` 指向临时目录来预置配置，不要动用户的真实配置。
- 只改了渲染层的话，更省事的做法是只起 renderer 的 Vite 开发服务，用 `shot.py` 截；preload 暴露的 API 用 `mock`，或者在页面里注入一个假对象代替。

## pywebview / 内嵌 HTTP 后端（MoneyFree 桌面端）

- 参照 `MoneyFree/scripts/shot_pages.py`：
  - 用 `tempfile.mkdtemp` 建临时数据目录，并设置数据根目录环境变量；
  - 用 seed 造数据，**故意造超长文本和大数字**；
  - 进程内启动 server，用随机端口。
- 要用真实数据时，**只拷贝副本**（db + meta），不拷同步配置，避免把截图过程中的写入同步到云端。
- 手机端页面（Android WebView 里打开的）用 390 宽截图；桌面端用 1280。

## 纯 HTML（MwjAppPrefTrace / MwjZhiWen 的 web 目录）

- 页面引用了绝对路径的资源（例如 MwjZhiWen 的 `/assets/common.css`），或者要请求后端接口：**必须起项目自己的服务**（端口要隔离）。用 http.server 直接托管 web 目录，资源全部 404，截出来的是没有样式的页面。
- 只有自包含的纯静态页（例如生成的报告 html）才用 `python3 -m http.server <port> -d <目录>`。
- 页面里要声明 `<meta charset="utf-8">`，否则中文会乱码。截图里看到乱码时，先查这一项。
