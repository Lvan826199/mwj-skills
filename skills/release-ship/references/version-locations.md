# 版本号常见位置

改之前用 SKILL.md 第 3 步的 `git grep` 找全，下表只是提示，**以 grep 结果为准**。

**只改「当前版本声明」。** 以下几类即使匹配到也不改：
- 「X.Y.Z 起支持…」这类历史说明
- 问题归因、版本历史
- 测试里专门用来做兼容判断的版本号
- 第三方依赖的版本（例如 `async-stream-0.3.6`）
- `target/`、`dist/` 下的编译产物

| 技术栈 | 位置 | 备注 |
|---|---|---|
| Python | `pyproject.toml` `[project] version` | 唯一权威来源 |
| Python | `<pkg>/__init__.py` `__version__` | 推荐改为 `importlib.metadata.version("<dist>")`，消除漂移；没改之前必须同步 |
| Python | `uv.lock` 本包条目 | 改完 `uv lock`，再 `uv lock --check --offline` |
| Python 打包 | Nuitka `--product-version` / PyInstaller spec / 版本资源文件 | 多数从 pyproject 读取，确认一下 |
| Node / Electron | `package.json`、`package-lock.json` 或 `pnpm-lock.yaml` | 用 `npm version --no-git-tag-version X.Y.Z` 一次改两处 |
| Electron | `electron-builder` 配置里的 `buildVersion` | 有就同步 |
| Android | `versionName` / `versionCode` | 有的项目由 Python 版本号算出（MoneyFree：0.6.1 → 601），不要手改 |
| 文档 | 协议示例里的 `"version"`、产物路径示例 `xxx-X.Y.Z-win64` | iPhoneUsbTouch 的 sidecar 协议、操作手册 |
| 测试 | `tests/test_version.py`、`npm run check:version` | 有就跑，它就是一致性门禁 |

## 版本号规则（来自用户纠正）

- 默认只升末位：0.3.2 → 0.3.3，新功能也一样；升中间位或主版本必须用户明确说。
- MoneyFree：每交给 Windows 打一次包，末位 +1；开新发布点时升中间位。
- 只增不减，不复用。
