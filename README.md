# mwj-skills

Claude Code 个人 Skills 集合，包含代码审查、需求文档生成等自动化工作流。

## Skills 列表

### `/code-review` - 代码审查

对当前 git 变更进行全面审查，包括：
- 自动运行 Flake8 / Black / isort / Mypy
- SOLID 原则与架构审查
- 安全漏洞扫描（XSS、注入、SSRF 等）
- 代码质量检查（错误处理、性能、边界条件）
- 冗余代码识别

审查结果按 P0~P3 优先级分级，等待用户确认后再修复。

**触发方式：**
```
/code-review
```
或直接说"帮我 review 代码"、"检查代码"、"代码审查"。

**自动触发：** 已配置 `.claude/settings.json` hook，执行 `git commit` 前自动触发审查，发现 P0/P1 问题时阻止提交。

---

### `/code-review-expert` - 专家级代码审查

从 GitHub 引入的精简版审查 skill，不含工具链检查，专注于架构和安全深度分析。与 `/code-review` 的区别：无 Python 工具链步骤，语言无关，适合快速架构审查。

---

### `/req-doc-generator` - 需求文档生成

按三阶段流水线生成完整模块设计文档：

1. 需求文档（功能需求、非功能需求、用例）
2. 数据库设计（表结构、字段、索引、关系）
3. API 设计（接口定义、请求/响应格式）

每个阶段用户确认后再进入下一阶段。

**触发方式：**
```
/req-doc-generator
```
或说"写需求文档"、"生成需求文档"、"设计数据库"、"设计 API 接口"。

---

## 目录结构

```
skills/
├── code-review/
│   ├── SKILL.md                    # 主 skill 文件
│   └── references/
│       ├── solid-principles.md     # SOLID 原则检查清单
│       ├── security-risks.md       # 安全风险检查清单
│       ├── code-quality.md         # 代码质量检查清单
│       └── cleanup-plan.md         # 冗余代码清理模板
├── code-review-expert/             # GitHub 引入的精简版（参考用）
│   ├── SKILL.md
│   ├── agents/agent.yaml
│   └── references/
└── req-doc-generator/
    ├── SKILL.md
    └── templates/

.claude/
└── settings.json                   # 项目级 hook 配置（git commit 前自动审查）
```

## Hook 配置说明

`.claude/settings.json` 配置了 `PreToolUse` hook，在执行 `git commit` 前自动触发代码审查。发现 P0/P1 级别问题时会阻止提交。

如需在其他项目使用相同 hook，将 `.claude/settings.json` 复制到对应项目根目录即可。

如需全局生效（所有项目），将 hook 配置合并到 `~/.claude/settings.json`。

---

# mwj-skills (English)

A personal Claude Code Skills collection featuring automated workflows for code review, requirements documentation, and more.

## Skills

### `/code-review` - Code Review

Performs a comprehensive review of current git changes, including:
- Automatically runs Flake8 / Black / isort / Mypy
- SOLID principles and architecture review
- Security vulnerability scanning (XSS, injection, SSRF, etc.)
- Code quality checks (error handling, performance, edge cases)
- Redundant code identification

Results are prioritized P0~P3, waiting for user confirmation before applying fixes.

**Trigger:**
```
/code-review
```
Or say "review my code", "check code", "code review".

**Auto-trigger:** A `.claude/settings.json` hook is configured to automatically trigger a review before `git commit`. Commits are blocked when P0/P1 issues are found.

---

### `/code-review-expert` - Expert Code Review

A streamlined review skill imported from GitHub, focused on deep architecture and security analysis without toolchain checks. Difference from `/code-review`: no Python toolchain steps, language-agnostic, ideal for quick architecture reviews.

---

### `/req-doc-generator` - Requirements Document Generator

Generates a complete module design document via a three-stage pipeline:

1. Requirements doc (functional requirements, non-functional requirements, use cases)
2. Database design (table structure, fields, indexes, relationships)
3. API design (interface definitions, request/response formats)

Each stage requires user confirmation before proceeding.

**Trigger:**
```
/req-doc-generator
```
Or say "write requirements doc", "generate requirements", "design database", "design API".

---

## Directory Structure

```
skills/
├── code-review/
│   ├── SKILL.md                    # Main skill file
│   └── references/
│       ├── solid-principles.md     # SOLID principles checklist
│       ├── security-risks.md       # Security risk checklist
│       ├── code-quality.md         # Code quality checklist
│       └── cleanup-plan.md         # Redundant code cleanup template
├── code-review-expert/             # Streamlined version from GitHub (reference)
│   ├── SKILL.md
│   ├── agents/agent.yaml
│   └── references/
└── req-doc-generator/
    ├── SKILL.md
    └── templates/

.claude/
└── settings.json                   # Project-level hook config (auto-review before git commit)
```

## Hook Configuration

`.claude/settings.json` configures a `PreToolUse` hook that automatically triggers a code review before `git commit`. Commits are blocked when P0/P1 issues are detected.

To use the same hook in another project, copy `.claude/settings.json` to that project's root directory.

To apply globally (all projects), merge the hook config into `~/.claude/settings.json`.
