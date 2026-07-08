# 更新日志

## [新增 delegate-to-cli] - 2026-07-08

### 新增
- 新增 `delegate-to-cli` skill：把读多写少、可独立验证的子任务委派给本地 CLI 智能体（kimi-cli / codex exec），支持 5 种执行模式（纯 kimi / 纯 codex / kimi 跑 + codex 复审 / 双 CLI 并行 / 主 agent 终审），4 关验收 + 最多 3 次重做
- 新增 `token_report.py`：解析 kimi session（wire.jsonl）与 codex 日志，生成 token 用量报告，输出"总 token 节省"与"主 agent 节省"两种口径的估算

## [skills 全面优化] - 2026-06-10

### 新增
- `mwj-design-system` 新增 `references/migration-guide.md`，承载 SCSS → CSS Token 迁移实战规则（变量映射、组件替换、已知陷阱），SKILL.md 按需引用，降低上下文占用
- `req-doc-generator` 阶段零新增第 7 项"文档输出位置"确认，输出路径不再硬编码（保留原路径为默认值）
- 新增 `.claude/hooks/check-commit.py`：git commit 拦截脚本（command 型 hook）
- 新增 `docs/changelog.md`、`docs/bug-fixes.md` 文档

### 变更
- `code-review` skill 重命名为 `py-code-review`，避免与 Claude Code 内置 `/code-review` 命令冲突
- `py-code-review` 第二步改为只读检查（`black --check --diff`、`isort --check-only`），所有修复统一移到第九步用户确认后执行，与"审查优先"原则对齐
- `py-code-review` 去除项目硬编码（`uv run`、`app/` 目录、Python 3.13 等），改为探测项目工具链（uv/poetry/pip）、以 git diff 范围为检查目标、以项目配置文件为准
- `py-code-review` 删除无法实现的"Edit/Write 后自动触发"描述，改为如实的 hook 触发说明
- `.claude/settings.json` hook 由 prompt 型改为 command 型：普通命令零开销放行，仅 `git commit` 被脚本拦截，审查通过后附加 `# review-passed` 标记放行
- `mwj-design-system` Step 1 补充 `MWJ_Design_System.md` 查找位置说明与文件缺失时的降级策略
- `ui-ux-pro-max-new` 交付清单 "Use theme colors directly" 条目增加 MWJ 项目限定说明，消除与 mwj-design-system 的规则冲突
- `ui-ux-pro-max-new` 示例对话由越南语改为中文，补充 shadcn/ui MCP 使用说明，`search.py --stack` help 文案修正为 13 个技术栈

### 修复
- `ui-ux-pro-max-new/SKILL.md` 中 10 处脚本路径错误（`skills/ui-ux-pro-max/` 缺少 `-new` 后缀），统一为相对 skill 根目录写法并补充路径说明
- `mwj-design-system` 圆角规范矛盾：统一为 Modal/Drawer → 16px（--radius-lg）、Card/大容器 → 24px（--radius-xl），与 Token 注释及组件示例一致
- `mwj-design-system` "技术栈要求"表格丢失的章节标题已补回
- `py-code-review` 中无效命令 `flake8 --diff`、违反 Git 规范的 `git add .` 示例已修正
