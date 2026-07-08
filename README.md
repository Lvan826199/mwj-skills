# mwj-skills

梦无矶 Claude Code 个人 Skills 集合，包含代码审查、需求文档生成、前端设计规范执行、子任务委派等自动化工作流。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Skills 列表

### `/py-code-review` — Python 代码审查

Python 代码审查流程，结合工具检查与资深工程师视角的深度审查。审查优先：先报告，经用户确认后再修复。

**审查流程（9 步）：**

1. 预检上下文 — `git diff` 确定变更范围，识别关键路径
2. 运行工具链（只读检查） — 探测项目工具链（uv/poetry/pip）后按顺序执行 Flake8 → Black `--check` → isort `--check-only` → Mypy，不修改代码
3. SOLID 原则审查 — SRP / OCP / LSP / ISP / DIP 逐项检查
4. 冗余代码识别 — 区分"立即可删"与"需计划后删"
5. 安全扫描 — XSS、注入、SSRF、路径遍历、竞态条件、密钥泄露等
6. 代码质量扫描 — 错误处理、N+1 查询、边界条件、静默失败
7. 工具结果分析 — 归类常见问题（未使用导入、布尔比较、f-string 等）
8. 生成审查报告 — 按 P0–P3 分级输出，含统计信息
9. 确认下一步 — 等待用户选择修复范围后再执行所有修复（含格式化）

**审查结果分级：**

| 级别 | 含义 | 处理方式 |
|------|------|----------|
| P0 | 安全漏洞、数据丢失风险、正确性 bug | 必须阻塞合并 |
| P1 | 逻辑错误、严重 SOLID 违反、性能退化 | 合并前应修复 |
| P2 | 代码异味、可维护性问题 | 本次或后续修复 |
| P3 | 风格、命名建议 | 可选改进 |

**触发方式：**
```
/py-code-review
```
或直接说"帮我 review 代码"、"检查代码"、"代码审查"。

> 命名为 `py-code-review` 是为了避免与 Claude Code 内置的 `/code-review` 命令冲突。

**Hook 触发：** 已配置 `.claude/settings.json` hook，执行 `git commit` 前会拦截未经审查的提交（详见文末「Hook 配置说明」）。

---

### `/req-doc-generator` — 需求文档生成

按三阶段流水线生成完整模块设计文档，每个阶段的输出是下一阶段的输入依据。

**流水线：**

```
阶段零：信息收集（模块名、背景、功能、用户、技术约束、数据量级）
    ↓
阶段一：需求文档（7 大章节，含验收标准）
    ↓ （用户确认后）
阶段二：数据库设计（表结构、索引、外键、预置数据）
    ↓ （用户确认后）
阶段三：API 设计文档（接口定义、权限要求、错误码）
```

**需求文档包含 7 大章节：**

| 章节 | 内容 |
|------|------|
| 1. 模块概述 | 简介、业务目标、适用范围、核心概念 |
| 2. 功能需求 | 功能描述、业务规则、输入项、验收标准 |
| 3. 非功能需求 | 性能要求、安全要求、可用性要求 |
| 4. 业务流程 | 纯文本箭头格式的流程图 |
| 5. 数据约束 | 唯一性、长度、枚举约束 |
| 6. 界面原型要点 | 页面布局 + 交互状态（空/加载/错误/反馈） |
| 7. 扩展需求 | 未来版本功能规划 |

**核心特性：**
- 文档带版本管理元信息（版本号、状态、变更记录）
- 每个功能点包含验收标准，覆盖正常流程和异常场景
- 性能指标根据实际业务场景填写，不套用默认值
- API 接口标注权限要求（管理员 / 登录用户 / 公开）
- 三份文档实体名、字段名、枚举值强制一致
- 支持只执行单个阶段（如"只生成数据库设计"）

**触发方式：**
```
/req-doc-generator
```
或说"写需求文档"、"生成需求文档"、"设计数据库"、"设计 API 接口"。

---

### `/mwj-design-system` — MWJ 设计系统规范执行器

MWJ Design System v1.2 前端开发规范执行器，确保所有前端代码输出严格遵循 Mwj 一体化测试平台设计系统。

**适用场景：** 开发/重构 Vue 组件、前端页面、UI 界面；涉及 Vue3 + TypeScript + TailwindCSS + Element Plus 的任何前端开发任务。

**执行流程（三阶段）：**

```
Phase 1 · 分析阶段
  → 读取 MWJ 设计规范
  → 判断页面/组件类型（登录页/管理类/接口测试/功能测试/报告看板等）
  → 决策是否补充查询 ui-ux-pro-max-new（图表/动效/Vue 最佳实践/可访问性）
        ↓
Phase 2 · 实现阶段
  → 应用 MWJ Design Token（颜色/圆角/阴影/间距/字体/动效 CSS 变量）
  → 编写代码（Vue3 script setup + TS + TailwindCSS + SCSS）
  → 使用 Mwj*/MwjBiz* 前缀组件
        ↓
Phase 3 · 交付阶段
  → 过完整自检清单（Token 合规/视觉质量/交互质量/数据状态/可访问性）
```

**权威优先级：**
1. MWJ Design Token — 最高优先级，不可覆盖
2. MWJ 组件规范（`Mwj*` / `MwjBiz*` 前缀、Element Plus 封装）
3. MWJ 布局系统（Header 64px / Sidebar 240px / 12 栅格）
4. `ui-ux-pro-max-new` 查询结果 — 补充参考，不得与 MWJ Token 冲突

**核心 Token 速览：**

| 类别 | 示例 |
|------|------|
| 品牌色 | `--color-primary: #1677FF` |
| 背景 | `--bg-page: #F5F7FB` / `--bg-card: #FFFFFF` |
| 间距 | `--space-1`(4px) 到 `--space-8`(64px) |
| 圆角 | `--radius-sm`(8px) / `--radius-xl`(24px) |
| 阴影 | `--shadow-sm` / `--shadow-md` / `--shadow-lg` |
| 动效 | `--duration-fast`(120ms) / `--duration-base`(200ms) |

**触发方式：**
```
/mwj-design-system
```
或说"写个页面"、"创建组件"、"重构前端"、"实现 UI"，以及任何涉及本项目前端开发的任务。

---

### `/ui-ux-pro-max-new` — UI/UX 设计智能助手

综合 UI/UX 设计指南，内置 67 种风格、96 套配色、57 种字体搭配、99 条 UX 准则、25 种图表类型，覆盖 13 个技术栈。

**数据库概览：**

| 维度 | 内容 |
|------|------|
| 风格 | Glassmorphism、Claymorphism、Minimalism、Brutalism、Neumorphism、Bento Grid、Dark Mode 等 67 种 |
| 配色 | SaaS、电商、医疗、美业、金融科技等 96 套 |
| 字体 | Google Fonts 精选搭配 57 种 |
| 图表 | ECharts / D3 图表类型推荐 25 种 |
| 技术栈 | React、Next.js、Vue、Svelte、SwiftUI、React Native、Flutter、Tailwind、shadcn/ui 等 13 种 |

**搜索命令：**

```bash
# 生成完整设计系统（推荐首次使用）
python3 skills/ui-ux-pro-max-new/scripts/search.py "beauty spa wellness" --design-system -p "项目名"

# 按领域查询
python3 skills/ui-ux-pro-max-new/scripts/search.py "trend dashboard" --domain chart
python3 skills/ui-ux-pro-max-new/scripts/search.py "animation loading" --domain ux
python3 skills/ui-ux-pro-max-new/scripts/search.py "dashboard admin saas" --stack vue
```

**与 mwj-design-system 的关系：**

在 MWJ 项目中，本 skill 作为 `mwj-design-system` 的**补充**，仅用于图表类型推荐、复杂动效模式、Vue 最佳实践和可访问性指引。MWJ Design Token 始终优先。

**触发方式：**
```
/ui-ux-pro-max-new
```
或涉及非 MWJ 项目的 UI 设计、配色选择、字体搭配、图表推荐等任务。

---

### `/delegate-to-cli` — 子任务委派执行器

把读多写少、可独立验证的子任务委派给本地 CLI 智能体（`kimi-cli` / `codex exec` / `claude -p`），并行执行后由主 agent 严格验收，不满意可要求重做（最多 3 次），每次任务结束输出 token 用量与节省估算报告。

**6 种执行模式：**

| 模式 | 适用场景 |
|------|----------|
| 1. kimi-only | 中文长文档审计、跨多文档对账，任务难度中低、信任度足够 |
| 2. codex-only | 精确代码语义任务（行号、调用图、函数签名审计） |
| 3. kimi 先跑 → codex 复审 | 重要审计的交叉验证（**强烈推荐**） |
| 4. kimi + codex 并行 | 要快又要二审，两边一致 = 高置信，分歧由主 agent 亲核 |
| 5. 主 agent 终审 + token 报告 | 可追加在任意模式之后收尾（建议每次都跑） |
| 6. claude-only（headless） | 环境没装 kimi/codex 或需要更强模型；按 Claude 系列分级选型：fable-5（最难）→ opus-4.8（默认）→ opus-4.6（降级）→ sonnet-4.6（批量并发）→ haiku-4.5（机械任务），优先使用当前环境可用的模型 |

**核心流程（7 步）：** 拆任务 → 写结构化 prompt（检查点清单 + 行号证据要求）→ 并发起飞 → 4 关验收（完整性/格式/抽查强声明/结论一致性）→ 不满意重做（追加反馈，最多 3 次）→ 主 agent 综合自核 → 输出 token 报告。

**适合委派的子任务（必须全部满足）：** 只读为主、可独立完成、产出格式严格可验证、失败可重试。**不要**委派写代码、改文件、需主上下文或有审批链路的操作。

**Token 报告（`token_report.py`）：** 解析 kimi session（`wire.jsonl`）、codex 日志（`tokens used` 行）与 claude JSON 输出（`usage` + `total_cost_usd`），输出两种节省口径 —— 总 token 节省（通常很小甚至为负）与主 agent 节省（核心指标，通常 90%+，代表主上下文不被中间 grep/read 输出污染）。

**前置依赖：** 至少安装并认证 `kimi-cli`、`codex`、`claude` 其中之一（在 Claude Code 内使用时 `claude` 天然可用）；派单前用 `which kimi-cli codex claude` 探测，优先使用当前环境有的。

**触发方式：**
```
/delegate-to-cli
```
或说"派 kimi/codex 跑"、"指挥 sub-agent"、"分发任务"、"整体巡检/审计/对账"、"再用 codex/kimi 复审一遍"。

---

## 目录结构

```
skills/
├── py-code-review/
│   ├── SKILL.md                        # 主 skill 文件（9 步审查流程）
│   └── references/
│       ├── solid-principles.md         # SOLID 原则检查清单
│       ├── security-risks.md           # 安全风险检查清单
│       ├── code-quality.md             # 代码质量检查清单
│       └── cleanup-plan.md             # 冗余代码清理模板
├── req-doc-generator/
│   ├── SKILL.md                        # 三阶段流水线定义
│   ├── evals/evals.json                # 10 个评估用例
│   └── templates/
│       ├── requirement-template.md     # 需求文档模板（7 章节）
│       ├── database-design-template.md # 数据库设计模板
│       └── api-design-template.md      # API 设计文档模板
├── mwj-design-system/
│   ├── SKILL.md                        # MWJ Design System v1.2 执行规范
│   └── references/
│       └── migration-guide.md          # SCSS → CSS Token 迁移实战规则
├── ui-ux-pro-max-new/
│   ├── SKILL.md                        # 设计智能助手主文件
│   ├── data/                           # 设计数据库（配色/图表/风格/排版等 CSV）
│   │   ├── colors.csv
│   │   ├── charts.csv
│   │   ├── styles.csv
│   │   ├── typography.csv
│   │   ├── ux-guidelines.csv
│   │   └── stacks/                     # 各技术栈最佳实践
│   └── scripts/                        # Python 搜索脚本
│       ├── search.py
│       ├── core.py
│       └── design_system.py
└── delegate-to-cli/
    ├── SKILL.md                        # 委派执行器主文件（6 模式/7 步流程）
    ├── token_report.py                 # kimi/codex/claude token 用量与节省估算报告
    └── README.md                       # skill 独立说明（安装/依赖/设计理念）

.claude/
├── settings.json                       # 项目级 hook 配置
└── hooks/
    └── check-commit.py                 # git commit 拦截脚本

docs/
├── changelog.md                        # 版本更新日志
└── bug-fixes.md                        # Bug 修复记录
```

## Hook 配置说明

`.claude/settings.json` 配置了 `PreToolUse` hook（command 类型，确定性脚本匹配，不消耗 LLM 调用）：

- 普通 Bash 命令直接放行，无额外开销
- `git commit` 命令会被 `.claude/hooks/check-commit.py` 拦截，提示先用 `py-code-review` skill 完成代码审查
- 审查通过（无 P0/P1 问题）后，在提交命令末尾附加 `# review-passed` 标记即可放行：
  ```bash
  git commit -m "fix(scope): 描述" # review-passed
  ```

如需在其他项目使用相同 hook，将 `.claude/settings.json` 与 `.claude/hooks/` 一并复制到对应项目根目录即可。

如需全局生效（所有项目），将 hook 配置合并到 `~/.claude/settings.json`（注意脚本路径需改为绝对路径或随之迁移）。

---

MIT License © mwj
