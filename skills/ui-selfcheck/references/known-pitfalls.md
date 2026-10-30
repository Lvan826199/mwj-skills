# 已知坑

| 坑 | 现象 | 对策 | 出处 |
|---|---|---|---|
| Vite 开了 HTTPS | 用 http 探测一直返回 000，误以为服务卡死 | 先看 vite.config 里有没有 `basicSsl`；用 `curl -sk https://...` 探测 | AiTestProject |
| inotify 额度不够 | Vite 启动后报 ENOSPC 退出 | 启动时加 `CHOKIDAR_USEPOLLING=true` | AiTestProject |
| ECharts 按需注册漏了组件 | 配置写了却静默不生效，例如 dataZoom 不出现 | 改图表前先查统一注册文件（`utils/echarts.ts`）；MoneyFree 各页面分散注册，要逐页查 | AiTestProject、MoneyFree |
| Vue 模板里写了字面量 `{{ }}` | 编译报 Unterminated string，路由跳转静默中止 | 加 `v-pre`，或在 script 里拼好字符串再输出 | AiTestProject |
| 新页面只注册了路由 | 只能通过 URL 直达，从导航点不进去 | 路由、导航配置、侧栏分组、权限四处都要注册；用真实点击验证 | AiTestProject |
| `full_page=True` 截图 | ECharts 画出界、布局变形 | 把视口拉到页面全高再截（`--full-height`） | MoneyFree |
| SPA 不触发 load | 截到的是空壳页面 | 等 networkidle，或用 `wait_for` 等关键元素出现 | AiTestProject |
| 安全上下文 API | localhost 上正常，从内网 IP 访问就失效 | 涉及剪贴板、摄像头等 API 时，从内网 IP 再验一次 | AiTestProject |
| Electron headless | 窗口段错误，或截图空白 | 用 offscreen 包装 + CDP；截图空白时改为读 DOM | Sujian |
| `pkill -f <关键字>` | 匹配到自己的命令行，把当前 shell 也杀了 | 记下 pid，按 pid 停；或用 `ps` + `grep` 精确过滤 | Sujian、AiTestProject |
| 端口被别人占用 | 截到的是别的服务或旧实例 | 先查端口属于哪个进程；本机有同事和别的项目的服务 | AiTestProject |
| 截图时动了真实数据 | 截图过程中的写入被同步到云端 | 只用临时目录或副本；不拷同步配置 | MoneyFree |
| 前端测试全是纯函数测试 | 模板写错、prop 名对不上，要到真机才发现 | 补一个用 SSR 真正渲染组件的测试（`*.render.test.js`） | MSCA |
| 静态页没写 charset | 截图里中文乱码 | 加上 `<meta charset="utf-8">` | — |
