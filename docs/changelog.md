# 更新日志

## [新增 mwj-project-init] - 2026-10-30

### 新增
- 新增 `mwj-project-init` skill：新建模式生成 AGENTS.md 唯一规则源（用户 2026-10-30 定）+ `@AGENTS.md` 的 CLAUDE.md、仓库内共享记忆、中文文档套件与 Python 脚手架（uv / src 布局 / Ruff / Mypy strict / pytest 标记 / importlib.metadata 版本 / check.sh 门禁），交付前实跑门禁；审计模式按清单只读检查已有项目并出偏差表；吸收 OcrYoloEngine `agent-rules-single-source` 的单源与 gitignore 规则

## [skill 分发机制] - 2026-10-30

### 新增
- 新增 `scripts/sync_skills.py`：以本仓库为唯一来源分发 skill，`check` 报告漂移、`link-user` 建用户级软链、`push-projects` 更新项目副本；默认演练，副本有独有文件时拒绝覆盖
- `CLAUDE.md` 新增「Skill 分发规则」

### 修复
- `ui-ux-pro-max-new` 收回项目副本里的 lint 修复：删除未使用的导入与变量、去掉无占位符的 f-string（行为不变，`--persist` 实测正常）

## [从历史会话反哺第二批 skill] - 2026-10-30

### 新增
- 新增 `ui-selfcheck` skill：界面改动截图自检，含通用截图脚本 `scripts/shot.py`（多视口、模拟接口、localStorage 注入、控制台/接口/横向溢出/白屏机器检查、manifest 输出）、看图清单、各技术栈适配与已知坑清单
- 新增 `project-readthrough` skill：只读通读，零改动、子代理分工 + 主线抽查、证据四档、编号清单交用户选、修复回填
- 新增 `session-handoff` skill：收工交接 / 会话与记忆迁移 / 中断恢复三模式，含交接记忆模板与 `scripts/copy_sessions.py`（只复制、sha256 校验、不覆盖不删除）

### 变更
- `py-code-review` 第二步改为按优先级探测工具链（项目门禁脚本或项目规定命令 → Ruff → Flake8 家族），无配置时默认 Ruff，只跑只读部分不改环境；新增第六步半「梦无矶项目约定审查」与 `references/mwj-conventions.md`；报告格式改为工具链无关

## [从历史会话反哺第一批 skill] - 2026-10-30

### 新增
- 新增 `device-handoff` skill：跨机器真机联调闭环，一个 skill 双角色（Linux 下发侧 / Windows 执行侧），含任务单与复验提示词骨架、回执骨架、下发前自检清单、回执审批清单、联调协议 README 模板；提炼自 MSCA、MoneyFree、iPhoneUsbTouch、AiTestProject 的联调实践
- 新增 `postmortem` skill：收工归因，按问题大小选表格行 / 条目 / 独立文档三档，根因按证据分级，收工主动交付
- 新增 `release-ship` skill：发版流程，版本号默认只升末位并先确认、版本号位置全量同步、CHANGELOG 转版本、附注标签、Windows 打包验收交给 device-handoff、对外发布逐项确认
- 新增 `plan/2026-10-30-skills-from-history.md`：从 12 个项目、约 160 条记忆、约 60 个历史会话提炼的完整 skill 方案（A–F 组）与施工顺序

## [delegate-to-cli 新增 Claude 系列模型] - 2026-07-08

### 新增
- `delegate-to-cli` 新增 Mode 6（claude-only）：通过 `claude -p` headless 模式委派子任务，按 Claude 系列模型分级选型（fable-5 最难任务 / opus-4.8 默认 / opus-4.6 降级备选 / sonnet-4.6 批量并发 / haiku-4.5 机械任务），优先使用当前环境可用的 CLI 与模型
- `token_report.py` 新增 `--claude LABEL:JSON_PATH` 参数，解析 `claude -p --output-format json` 的 `usage` 与 `total_cost_usd`，claude 子任务一并计入 token 节省估算

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
