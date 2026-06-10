# Skills 优化任务清单（2026-06-10）

来源：对仓库内 4 个 skill、README、hook 配置的全面审查，用户确认全部修复。

## 任务列表

### A. ui-ux-pro-max-new（高优先级 1、2 + 低优先级 9、12）
- [x] A1 修正 10 处错误脚本路径 `skills/ui-ux-pro-max/...` → 相对 skill 根目录写法
- [x] A2 统一三处文档中 search.py 路径写法，补充路径说明
- [x] A3 交付清单 "Use theme colors directly" 条目加 MWJ 项目限定说明
- [x] A4 越南语示例改为中文；正文补充 shadcn/ui MCP 说明；search.py `--stack` help 文案修正

### B. code-review 重命名与流程修正（高 3 + 中 4、5、6）
- [x] B1 重命名 `code-review` → `py-code-review`（目录、frontmatter、README、CLAUDE.md）
- [x] B2 第二步改为只读检查（black --check --diff / isort --check-only），修复统一移到第九步确认后
- [x] B3 删除无法实现的"Edit/Write 自动触发"描述，改为 hook 触发说明
- [x] B4 去硬编码：探测 uv/poetry/pip 工具链，检查范围以 git diff 为准，配置读项目文件
- [x] B5 修正 `git add .`、无效的 `flake8 --diff` 等遗留问题，示例对话与"确认后修复"流程对齐

### C. mwj-design-system（中 7、8 + 低 10、11）
- [x] C1 Step 1 补充 MWJ_Design_System.md 查找位置与缺失降级策略
- [x] C2 统一圆角规范：Modal/Drawer → 16px(lg)，Card/大容器 → 24px(xl)（与 Token 注释及组件示例一致）
- [x] C3 补回"技术栈要求"丢失标题
- [x] C4 SCSS 迁移规则拆分到 `references/migration-guide.md`，SKILL.md 留指引

### D. req-doc-generator（低 13）
- [x] D1 阶段零新增"文档输出位置确认"（提供默认值），通用规则注明路径可调整

### E. Hook 优化（低 14）
- [x] E1 prompt 型 hook 改为 command 型脚本 `.claude/hooks/check-commit.py`，仅拦截 git commit
- [x] E2 README Hook 配置说明同步更新

### F. 文档同步与提交
- [x] F1 README.md 同步全部变更（skill 名称、流程描述、目录树）
- [x] F2 CLAUDE.md 概述表与开发流程同步重命名
- [x] F3 新建 `docs/changelog.md`、`docs/bug-fixes.md` 并记录本次修复
- [x] F4 验证：grep 无残留旧引用、hook 脚本实测、search.py 可运行
- [x] F5 分批提交

## 关键决策记录
- skill 重命名取 `py-code-review`（突出 Python 专用，避免与 Claude Code 内置 /code-review 冲突）
- 圆角矛盾取 Token 注释为准：`--radius-lg 16px` 用于弹窗/Drawer，`--radius-xl 24px` 用于卡片/容器
- hook 改为确定性脚本拦截：git commit 命令需附 `# review-passed` 标记（审查通过后由 Claude 添加）方可放行，避免每条 Bash 命令都走 LLM 评估
