# AGENTS.md / CLAUDE.md / 记忆 / 文档模板

`<…>` 换成实际值。可选节在不适用时整节删除，不要留空标题。

## AGENTS.md

````markdown
# <项目名>

> 本文件是唯一维护的 AI 助手规则（Claude Code / Codex / Cursor 共用，换电脑、换工具照此执行）。
> `CLAUDE.md` 只是对本文件的引用，规则改这里。

<一句话：这个项目是什么、给谁用、当前主线>

改动前先读：
- `README.md`：用途、安装与快速开始
- `docs/memory/MEMORY.md`：共享记忆索引（跨会话、跨机器的决定与踩坑）
- `docs/问题归因.md`：历史问题与根因，排障先在这里搜

## 语言
- 回复、文档、注释、提交描述一律用简体中文；标识符、命令、专有名词保持原文。
- 注释写「为什么」，不写「做了什么」；超时、阈值等常量要注明出处（哪次实测、哪份回执）。

## 边界
- <不要碰的目录或项目，例如：`reference/` 是只读参考副本；不碰已发版的下游项目>
- 本地 AI 工具目录（`.claude/`、`.codex/` 等）只留在本机，不入库。

## 工作流
- 用户没说「做」，就不改代码；先给方案，确认后再执行。需要用户拿主意时，用选项提问并标出推荐项。
- 计划文档放 `plan/`；多步任务用任务清单推进。
- 每个任务按顺序走：实现 → 代码审查（py-code-review）→ 测试 → 同步文档 → 提交。审查或测试没通过，不进入下一项。
- 界面改动先自己截图看过再交付（ui-selfcheck）。

## 提交与推送
- 提交信息：`<类型>(<范围>): <中文描述>`，类型限 feat / fix / docs / refactor / test / chore；描述不超过 50 字，不加句号。
- 提交前门禁 `bash scripts/check.sh` 必须全绿。提交信息里写的「通过」，只能在结果出来之后写。
- `git add` 时逐个列出文件，禁止 `git add .`；推送到 `<origin（Gitee）>`。
- 二进制和构建产物（exe、apk、zip）不入库。

## 文档同步（和代码在同一个提交里）
| 改了什么 | 同步到 |
|---|---|
| CLI 参数或行为 | `README.md`、<使用手册> |
| 修了 bug | `docs/问题归因.md` 追加一行（postmortem） |
| 用户能感知的变化 | `CHANGELOG.md` 的「未发布」段 |
| 新的决定或踩坑 | `docs/memory/` 新增一条并更新索引 |
| 工作规则 | 本文件 |

## 版本号
- 唯一来源是 `pyproject.toml`，运行时用 `importlib.metadata` 读取，`tests/test_version.py` 守住一致性。
- 默认只升末位；升中间位或主版本要用户明确同意。发版走 release-ship。

## 记忆
- 共享记忆放在 `docs/memory/`，一条一个文件（frontmatter：name / description / type；正文写 Why / How to apply），在 `docs/memory/MEMORY.md` 里加一行索引。
- 本机记忆桶（`~/.claude/projects/...`）只放和这台机器相关的内容。
- 凭据、token、本机绝对路径不写进记忆。

<!-- 可选：需要 Windows 真机或打包时保留 -->
## 跨机器协作（Linux 开发 ⇄ Windows 真机）
- 联调协议见 `docs/联调/README.md`（device-handoff）；发版流程见 `docs/打包发布.md`。
- Windows 侧不改源码，只提交回执；对 Windows 侧说「按联调任务执行」即可。
````

## CLAUDE.md

```markdown
@AGENTS.md
```

## docs/memory/MEMORY.md

```markdown
# 共享记忆索引

一行一条：`- [标题](文件.md) — 一句话说明`。规则见 AGENTS.md「记忆」一节。
```

## docs/问题归因.md

用 postmortem skill `references/templates.md` 里档 1 的文件头，第一个分组可以叫「## 1. 环境与安装」。

## CHANGELOG.md

```markdown
# 更新日志

格式参考 Keep a Changelog（中文）；版本号只升末位，见 AGENTS.md。

## [未发布]

### 新增
- 初始化项目骨架
```

## .gitignore 追加块

```gitignore
# Python
__pycache__/
*.pyc
.venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage

# 产物与临时文件
dist/
build/
releases/
.tmp/
logs/

# 本地配置与凭据
.env

# AI 助手本地配置（权限、缓存、机器路径只留本机）
.claude/
.agent/
.agents/
.codex/
.Codex/
```
