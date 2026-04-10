# mwj-skills

梦无矶 Claude Code 个人 Skills 集合，包含代码审查、需求文档生成等自动化工作流。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[English](README.en.md)

---

## Skills 列表

### `/code-review` — 代码审查

自动化代码审查流程，结合工具检查与资深工程师视角的深度审查。

**审查流程（9 步）：**

1. 预检上下文 — `git diff` 确定变更范围，识别关键路径
2. 运行工具链 — 按顺序执行 Flake8 → Black → isort → Mypy
3. SOLID 原则审查 — SRP / OCP / LSP / ISP / DIP 逐项检查
4. 冗余代码识别 — 区分"立即可删"与"需计划后删"
5. 安全扫描 — XSS、注入、SSRF、路径遍历、竞态条件、密钥泄露等
6. 代码质量扫描 — 错误处理、N+1 查询、边界条件、静默失败
7. 工具结果分析 — 自动修复常见问题（未使用导入、布尔比较、f-string 等）
8. 生成审查报告 — 按 P0–P3 分级输出，含统计信息
9. 确认下一步 — 等待用户选择修复范围后再执行

**审查结果分级：**

| 级别 | 含义 | 处理方式 |
|------|------|----------|
| P0 | 安全漏洞、数据丢失风险、正确性 bug | 必须阻塞合并 |
| P1 | 逻辑错误、严重 SOLID 违反、性能退化 | 合并前应修复 |
| P2 | 代码异味、可维护性问题 | 本次或后续修复 |
| P3 | 风格、命名建议 | 可选改进 |

**触发方式：**
```
/code-review
```
或直接说"帮我 review 代码"、"检查代码"、"代码审查"。

**自动触发：** 已配置 `.claude/settings.json` hook，执行 `git commit` 前自动触发审查，发现 P0/P1 问题时阻止提交。

---

### `/code-review-expert` — 专家级代码审查

从 GitHub 引入的精简版审查 skill，不含 Python 工具链步骤，语言无关，适合快速架构审查。

**审查流程（7 步）：**

1. 预检上下文 — 确定变更范围，支持大型 diff 分批审查
2. SOLID + 架构审查 — 检查五大原则违反，提出渐进式重构方案
3. 冗余代码识别 — 未使用代码、已关闭 feature flag 的清理计划
4. 安全与可靠性扫描 — 注入、认证/授权漏洞、竞态条件、不安全默认配置
5. 代码质量扫描 — 错误处理、性能热点、边界条件
6. 生成审查报告 — P0–P3 分级 + 行内注释格式
7. 确认下一步 — 用户选择修复范围

**与 `/code-review` 的区别：**
- 无 Flake8 / Black / isort / Mypy 工具链步骤
- 不限定 Python，适用于任何语言
- 更侧重架构和安全深度分析

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

## 目录结构

```
skills/
├── code-review/
│   ├── SKILL.md                    # 主 skill 文件（9 步审查流程）
│   └── references/
│       ├── solid-principles.md     # SOLID 原则检查清单
│       ├── security-risks.md       # 安全风险检查清单
│       ├── code-quality.md         # 代码质量检查清单
│       └── cleanup-plan.md         # 冗余代码清理模板
├── code-review-expert/             # 精简版（语言无关，无工具链）
│   ├── SKILL.md
│   ├── agents/agent.yaml
│   └── references/
│       ├── solid-checklist.md
│       ├── security-checklist.md
│       ├── code-quality-checklist.md
│       └── removal-plan.md
└── req-doc-generator/
    ├── SKILL.md                    # 三阶段流水线定义
    ├── evals/evals.json            # 10 个评估用例
    └── templates/
        ├── requirement-template.md     # 需求文档模板（7 章节）
        ├── database-design-template.md # 数据库设计模板
        └── api-design-template.md      # API 设计文档模板

.claude/
└── settings.json                   # 项目级 hook 配置（git commit 前自动审查）
```

## Hook 配置说明

`.claude/settings.json` 配置了 `PreToolUse` hook，在执行 `git commit` 前自动触发代码审查。发现 P0/P1 级别问题时会阻止提交。

如需在其他项目使用相同 hook，将 `.claude/settings.json` 复制到对应项目根目录即可。

如需全局生效（所有项目），将 hook 配置合并到 `~/.claude/settings.json`。

---

MIT License © mwj
