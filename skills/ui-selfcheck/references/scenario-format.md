# shot.py 用法与场景格式

## 运行环境

- 用 `uv run --with playwright python <skill 目录>/scripts/shot.py ...` 运行，不需要在项目里装依赖。
- 浏览器优先用本机 Chrome。查找顺序：`--chrome` 参数 → `MWJ_BROWSER_PATH` → `/usr/bin/google-chrome` 等常见路径。都找不到才用 Playwright 自带的浏览器。
- **不要用 `npx playwright`**：项目的 node_modules 里没有它，会触发一次大下载。
- 以 root 身份运行或在容器里运行时，加 `--no-sandbox`。

## 简单场景（命令行）

```bash
uv run --with playwright python <skill 目录>/scripts/shot.py \
  --name settings --base https://localhost:5173 \
  --page /settings@settings --page /home \
  --viewports 1920x1080,390x844 --full-height \
  --local-storage 'token=xxx'
```

- `--page /path[@key]`：可重复。key 用于文件名，不写时由路径推导。
- `--wait-ms`：页面就绪后再等多少毫秒，默认 1500。图表、动画多的页面要调大。
- `--full-height`：把视口拉到页面全高再截，上限 6000px。
- `--out`：输出根目录，默认 `.tmp/screenshots`。

## 复杂场景（--scenario JSON）

```json
{
  "name": "device-list",
  "base": "http://127.0.0.1:5391",
  "viewports": ["1920x1080", "390x844"],
  "wait_ms": 2000,
  "full_height": false,
  "local_storage": {
    "user": {"token": "fake", "permissions": ["*"]}
  },
  "storage_state": null,
  "mock": {
    "**/api/devices": {"json": {"code": 0, "data": [{"id": 1, "name": "很长很长的设备名称用于测试截断"}]}},
    "**/api/devices/empty": {"json": {"code": 0, "data": []}},
    "**/api/stats": {"file": "fixtures/stats.json"},
    "**/api/broken": {"status": 500, "body": "boom", "content_type": "text/plain"}
  },
  "pages": [
    {"key": "list", "path": "/devices"},
    {"key": "list-dialog", "path": "/devices", "click": ["button.add-device"], "wait_for": ".el-dialog"},
    {"key": "list-error", "path": "/devices-broken", "allow_errors": ["/api/broken", "500"]}
  ]
}
```

- `mock` 的键是 Playwright 的 URL glob。值可以写 `json`、`file`（相对于场景文件所在目录）或 `body`，可选 `status`、`content_type`。
- `local_storage` 的值如果是对象，会先 JSON 序列化再写入。脚本会先打开一次同源页面把值写进去，然后再正式导航。
- `storage_state`：Playwright 导出的登录态文件，适合 cookie 登录的项目。
- `click`：页面就绪后依次点击这些选择器，用来打开弹窗、抽屉、下拉框。点击或 `wait_for` 失败时，仍然截下当时的页面，并把失败记进 `step_errors`。
- `allow_errors`：本页**预期内**的报错，按子串匹配，例如截「接口失败态」时故意模拟的 500。匹配到的报错移到 `allowed_errors`，不算失败。
- **空态**：为同一页面单独写一个场景，把接口模拟成空数组。

## 输出

- 截图：`.tmp/screenshots/<name>/<时间戳>/<key>-<W>x<H>.png`。H 是实际截图高度，开了 `--full-height` 时就是页面全高
- `manifest.json`：每张截图的 `path`、`console_errors`、`http_errors`、`step_errors`、`allowed_errors`、`overflow_x`、`is_blank`、`ok`。`/favicon.ico` 的 404 和控制台里重复出现的「Failed to load resource」不计入
- 退出码：任一张截图的机器检查不过，退出码为 1

**机器检查通过不等于界面没问题**，截图仍然要用 Read 一张张看。
