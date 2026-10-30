<!-- Author: 梦无矶 -->
# CLAUDE.md

本文件为 Claude Code 在此仓库工作时提供指引。

> **你必须严格遵守本文档。**
>
> 始终使用简体中文回复用户，包括思考过程，尽量不要使用其他语言。
>
> 请勿跳过任何步骤。
>
> 请勿对未明确说明的要求进行假设。
>
> 任何不确定之处必须在继续之前向用户确认。

---

## 项目概述

`mwj-skills` 是梦无矶的 Claude Code 个人 Skills 集合仓库，包含可复用的自动化工作流 skill。

| Skill | 触发方式 | 用途 |
|-------|----------|------|
| `py-code-review` | `/py-code-review` | Python 代码审查（9 步流程，P0–P3 分级；自动探测 Ruff/Flake8 工具链，含梦无矶项目约定审查） |
| `req-doc-generator` | `/req-doc-generator` | 三阶段需求/数据库/API 文档生成 |
| `mwj-design-system` | `/mwj-design-system` | MWJ Design System v2.0 前端规范执行器（标准 / 柔和双变体；项目有自己风格时不强制） |
| `ui-ux-pro-max-new` | `/ui-ux-pro-max-new` | UI/UX 设计智能助手（67 风格/96 配色/13 技术栈） |
| `delegate-to-cli` | `/delegate-to-cli` 或提到"派 kimi/codex/claude 跑"、"整体巡检/审计" | 将读多写少的子任务委派给本地 CLI 智能体（kimi-cli/codex/claude），并行执行、严格验收并输出 token 节省报告 |
| `device-handoff` | `/device-handoff` 或说"给 Windows 提示词"、"回执来了"、"按联调任务执行" | 跨机器真机联调闭环：Linux 侧下发自检/任务单/回执审批/复验，Windows 侧照单执行并写回执 |
| `postmortem` | `/postmortem` 或说"写归因"、"复盘"；修完 bug 主动触发 | 收工归因，三档粒度（表格行/条目/独立文档），根因按证据分级 |
| `release-ship` | `/release-ship` 或说"发版"、"出 vX.Y.Z"、"打 tag" | 发版流程：版本号确认（只升末位）、门禁、版本号全量同步、CHANGELOG、标签、Windows 打包验收、发布逐项确认 |
| `ui-selfcheck` | `/ui-selfcheck` 或说"截图看看"、"自检一下界面"；界面改动交付前主动触发 | 界面改动截图自检：隔离环境、多视口多状态截图、机器检查、逐张看图，附 `shot.py` |
| `project-readthrough` | `/project-readthrough` 或说"通读"、"找隐藏问题"、"先不改，你看看" | 只读通读找隐藏问题，证据分级编号，用户逐项选定后再修 |
| `session-handoff` | `/session-handoff` 或说"收工"、"交接"、"挪到 X 目录"、"恢复任务继续执行" | 收工交接 / 会话与记忆迁移（只复制校验）/ 中断后恢复 |
| `mwj-project-init` | `/mwj-project-init` 或说"新建项目"、"初始化项目"、"规范对齐" | 新建项目脚手架（AGENTS.md 单源 + uv/Ruff/Mypy/pytest 门禁，实跑全绿）/ 已有项目规范对齐审计 |
| `mwj-python-style` | `/mwj-python-style` 或在 Python 项目写代码时；说"按我的风格写" | 写代码时就遵守的编码习惯，规则唯一清单与 py-code-review 共用 |
| `mwj-architecture` | `/mwj-architecture` 或说"用什么架构"、"分层"、"补架构测试" | A–F 六种架构模式库、选型表、越层判断、AST 依赖方向架构测试模板 |
| `mwj-memory` | `/mwj-memory` 或说"记忆进仓库"、"同步记忆"、"审计记忆" | 记忆方案选型、写入规范、三方同步脚本（冲突不覆盖、敏感拦截）与审计 |

---

## Skill 分发规则

本仓库 `skills/` 是所有 skill 的**唯一来源**，修改只在这里做，然后用 `scripts/sync_skills.py` 分发：

```bash
python scripts/sync_skills.py check                    # 报告用户级与各项目副本的漂移
python scripts/sync_skills.py link-user [--apply]      # ~/.claude/skills/<name> 软链到本仓库
python scripts/sync_skills.py push-projects [--apply]  # 更新各项目里已存在的副本（复制）
```

- 默认只演练，加 `--apply` 才写入；写入用户级目录和其他项目前须经用户确认
- 用户级用软链（改一处立即生效）；项目副本跟项目仓库走、需在 Windows 可用，用复制
- 副本里有本仓库没有的文件时脚本拒绝覆盖：先评估并收回本仓库，再分发
- 在项目里直接改过的 skill（如 lint 修复），先判断差异方向，较新的一方收回本仓库

---

## 上下文管理规则

**压缩触发条件：** Token 用量 ≥ 80%

**压缩策略：**
- 保留当前任务上下文（最近 10 轮对话）
- 保留关键文件路径和代码片段
- 保留用户明确指令和决策
- 压缩历史执行日志和工具调用结果
- 压缩重复性内容和中间过程

**压缩后行为：** 继续执行当前任务，无需用户干预；通过读取文件恢复必要上下文；优先使用任务清单（Task List）跟踪进度。

---

## 开发流程

- 所有开发任务**必须以任务清单（Task List）为驱动**
- 计划文档放在项目根目录下的 `plan/` 目录，而不是默认的用户目录
- 每一个任务必须完整经历以下阶段：
  1. 开发实现
  2. 代码审查（使用 `py-code-review` skill）
  3. 功能测试
  4. 状态更新与代码提交

- 代码审查或测试未通过：禁止进入下一任务，必须回到开发阶段修复问题

- 遇到以下情况必须**暂停并与用户确认：**
  - 需求描述不清晰
  - 存在多种实现方案且影响结果
  - 存在影响业务结果的关键设计决策

---

## 代码规范

### Python

- ✅ 符合 PEP 8（Flake8）
- ✅ 使用 Black（88 字符行宽）
- ✅ 使用 isort
- ✅ 全量类型注解
- ❌ 禁止无注释的复杂逻辑
- ❌ 禁止提交无关或未使用代码

**代码质量检查命令：**
```bash
# 完整检查（Flake8 + Black + isort + Mypy）
flake8 . && black . && isort . && mypy .

# 仅检查不修改
black . --diff
isort . --check-only

# 自动修复
black .
isort .
```

---

## 文档规范

### 提交前必须同步的文档

每次代码提交前，根据变更类型检查并同步对应文档：

| 变更类型 | 必须更新的文档 |
|----------|----------------|
| 新增 skill | `README.md` skill 列表、`CLAUDE.md` 项目概述表 |
| 修改 skill 行为 | 对应 `skills/*/SKILL.md`、`README.md` 相关说明 |
| 修复 bug | `docs/bug-fixes.md`（记录问题、根因、修复方案） |
| 新增功能 / 重要变更 | `docs/changelog.md`（版本更新日志） |
| 新增或调整工作规则 | `CLAUDE.md` 对应章节 |

**禁止"功能完成但文档未更新"的情况出现。**

### 记忆存储规范

Claude Code 的记忆文件存放在 `.claude/memory/`，通过 `MEMORY.md` 索引。

- 保存对未来对话有价值的信息：用户偏好、反馈、项目决策、外部资源引用
- 不保存可从代码/git 历史直接推导的内容（代码结构、文件路径、最近改动等）
- 记忆内容发生变化时及时更新，避免过期记忆误导后续对话

### 更新日志规范（`docs/changelog.md`）

```markdown
## [版本号或日期] - YYYY-MM-DD

### 新增
- 简述新增内容

### 变更
- 简述行为变更

### 修复
- 简述修复内容
```

- 每次有用户可见的变更（新 skill、行为调整、重要修复）必须追加一条记录
- 日期使用实际完成日期，格式 `YYYY-MM-DD`

### Bug 修复记录规范（`docs/bug-fixes.md`）

```markdown
### [模块名] 问题标题

**发现时间：** YYYY-MM-DD
**问题描述：** 现象与影响范围
**根因分析：** 问题根本原因
**修复方案：** 具体修复措施
**修复状态：** 待修复 / 修复中 / 已修复
```

- 代码审查或测试发现的 P0/P1 问题必须在此留档
- 修复完成后更新状态，不得删除历史记录

---

## Git 规范

### 提交信息格式

```
<类型>(<可选范围>): <简短描述>

<可选正文：说明改动动机，每行不超过 72 字符>
```

**允许的类型：**

| 类型 | 用途 |
|------|------|
| `feat` | 新增功能 |
| `fix` | 修复缺陷 |
| `docs` | 仅文档变更 |
| `refactor` | 重构 |
| `test` | 新增或修改测试 |
| `chore` | 杂项维护 |

- 描述使用简体中文，祈使语气，不加句号，控制在 50 字符以内
- 禁止使用模糊前缀（`update`、`misc`、`todo` 等）

**示例：**
```
feat(skill): 新增 mwj-design-system 前端规范执行器
docs: 完善 README 各 skill 使用说明
fix(py-code-review): 修复 P0 判定遗漏安全扫描场景
```

### 推送规范

```bash
# 提交代码
git add <具体文件>
git commit -m "类型(范围): 描述"
git push origin master
```

- 暂存文件时**指定具体文件名**，避免 `git add .` 误提交敏感文件
- 推送前确认远程名称：`git remote -v`
