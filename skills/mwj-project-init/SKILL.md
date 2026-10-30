---
name: mwj-project-init
description: 梦无矶项目脚手架与规范对齐。新建模式：生成 AGENTS.md（唯一规则源）+ CLAUDE.md（@AGENTS.md）、仓库内共享记忆、中文 docs 套件（问题归因 / CHANGELOG / 打包发布）、.gitignore，Python 项目再生成 uv + src 布局 + Ruff + Mypy + pytest 标记 + importlib.metadata 版本 + scripts/check.sh 门禁，并实跑一遍检查。审计模式：按清单逐项检查已有项目与规范的偏差，只出报告，用户选定后再改。用户说「新建项目」「初始化项目」「搭个脚手架」「初始化规范」「生成 AGENTS.md」「检查一下项目规范」「规范对齐」时触发。
---

# MWJ Project Init：脚手架与规范对齐

规范来自 MyProject 下 12 个项目的共性（详见 mwj-skills `plan/2026-10-30-skills-from-history.md`）。**AI 规则以 AGENTS.md 为唯一来源**（2026-10-30 用户定）：Codex、Cursor 等工具会直接读 AGENTS.md，CLAUDE.md 里只写一行 `@AGENTS.md`。

先判断走哪个模式：目录是空的、或者用户说「新建」→ **A 新建**；已有代码 → **B 审计**。

## A. 新建项目

### 第 1 步：收集信息（用一次 AskUserQuestion 问完，带默认值）

| 项 | 默认 |
|---|---|
| 项目名、一句话说明 | — |
| 类型 | CLI / 库（`src/` 布局 + `[project.scripts]`）；也可选 FastAPI 服务、桌面应用（Nuitka 打包）、纯前端 |
| Python 版本 | `>=3.11,<3.14` |
| 远端 | Gitee（`git remote -v` 显示已有远端的，就沿用） |
| 需不需要 Windows 真机 / 打包 | 不需要。需要的话加「跨机器协作」一节，并建 `docs/打包发布.md` |

### 第 2 步：生成文件

按 `references/agents-md-template.md` 和 `references/python-scaffold.md` 生成，**已经存在的文件不覆盖**，先列出差异问用户。

```
<项目>/
├── AGENTS.md                 # 唯一规则源
├── CLAUDE.md                 # 只有一行 @AGENTS.md
├── README.md                 # 一句话说明 + 快速开始
├── CHANGELOG.md              # ## [未发布]
├── .gitignore                # 含 AI 工具本地目录、.env、.tmp、dist
├── docs/
│   ├── 问题归因.md           # postmortem 表格档的文件头
│   ├── memory/MEMORY.md      # 共享记忆索引（一条一个文件）
│   └── 打包发布.md           # 仅当需要打包时生成
├── pyproject.toml            # Python 项目
├── scripts/check.sh          # 门禁唯一入口（本地与 CI 共用）
├── src/<pkg>/{__init__,cli}.py
└── tests/test_version.py, tests/test_cli.py
```

FastAPI 服务类再加：`settings.py`（pydantic-settings，带项目前缀）、`.env.example`、`start.sh` + `start.ps1`（两边行为一致）。模板见 `python-scaffold.md` 末尾一节。

### 第 3 步：实跑验证（不过不交付）

```bash
git init -q 2>/dev/null; uv sync --extra dev
bash scripts/check.sh            # ruff check / ruff format --check / mypy / pytest 全绿
uv run <命令名> --version        # 输出 pyproject 里的版本
```

任何一步不过就修模板产物，直到全绿为止。

### 第 4 步：首次提交

`git add` 时逐个列出生成的文件，禁止 `git add .`。提交信息：`chore: 初始化项目骨架与 AI 规则`。是否推送要先问用户。

## B. 已有项目：规范对齐审计

1. **只读检查**：按 `references/audit-checklist.md` 逐项过一遍。每项给出 ✅ / ❌ / —（不适用），❌ 要附证据（文件、行号）。
2. **出报告**：用表格列出偏差、影响和修改建议，按影响大小排序。**已有项目不强制迁移规则源**：已经是 CLAUDE.md 为源的项目，只检查「单源、不重复」是否成立。
3. **用 AskUserQuestion 让用户勾选**要修的项，然后停下等用户选。
4. **按勾选修改**：每一项单独提交（`chore(规范): …`）；需要同步文档的，按项目自己的文档同步表来。

## 硬规则

- 不覆盖已有文件；不改已有项目的规则源方向，除非用户明确要求。
- 凭据、本机绝对路径、权限白名单不进 AGENTS.md，也不进 `docs/memory/`。
- `.claude/`、`.codex/` 等 AI 工具的本地目录必须写进 gitignore，不入库。
- 生成的项目必须实跑门禁并全绿，才算交付。
