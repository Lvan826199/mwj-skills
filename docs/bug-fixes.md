# Bug 修复记录

### [ui-ux-pro-max-new] SKILL.md 中 10 处脚本路径错误导致命令不可用

**发现时间：** 2026-06-10
**问题描述：** SKILL.md 第 163~313 行的示例命令均写为 `python3 skills/ui-ux-pro-max/scripts/search.py`（缺少 `-new` 后缀），实际目录为 `skills/ui-ux-pro-max-new/`。按文档执行命令会直接报"文件不存在"，影响该 skill 的全部搜索功能。
**根因分析：** skill 由上游 `ui-ux-pro-max` 项目复制改名而来，目录改名后文档内路径未同步更新。
**修复方案：** 全部统一为相对 skill 根目录的写法 `python3 scripts/search.py`，并在 "How to Use This Skill" 处增加路径说明（按实际安装位置补全前缀）。同时统一 `mwj-design-system` 中对该脚本的引用方式（`$UI_SKILL` 占位符 + 说明）。
**修复状态：** 已修复

---

### [py-code-review] 审查流程自相矛盾：第二步直接修改代码，第九步声称"确认前不修改"

**发现时间：** 2026-06-10
**问题描述：** 原第二步直接运行 `black app/`、`isort app/`（写入式格式化），"自动修复常见问题"一节也允许改完再告知；但第九步明确要求"在用户明确确认之前，不要实施任何修改"。两者冲突，实际执行时可能在用户确认前改写代码。
**根因分析：** skill 编写时混合了"CI 自动格式化"与"审查优先"两种工作流，未统一。
**修复方案：** 第二步全部改为只读检查（`black --check --diff`、`isort --check-only --diff`），"自动修复"章节改名为"常见问题快速修复（第九步用户确认后执行）"，示例对话同步改为先确认后修复。
**修复状态：** 已修复

---

### [mwj-design-system] 圆角规范前后矛盾

**发现时间：** 2026-06-10
**问题描述：** "元素圆角推荐对照"写 Card/Modal → 16px，但 Token 注释定义 `--radius-xl: 24px /* 卡片、容器 */`、`--radius-lg: 16px /* 弹窗、Drawer */`，且 Card 组件示例代码使用 `var(--radius-xl)`（24px）。同一文档内三处口径不一致。
**根因分析：** 对照表编写时误将 Card 与 Modal 归为同一档，未与 Token 定义核对。
**修复方案：** 以 Token 注释为准统一：Modal/Drawer → 16px（--radius-lg），Card/大容器/看板卡 → 24px（--radius-xl），对照表各项补注对应 Token 名。
**修复状态：** 已修复

---

### [hooks] prompt 型 PreToolUse hook 对每条 Bash 命令做 LLM 评估，拖慢所有命令

**发现时间：** 2026-06-10
**问题描述：** `.claude/settings.json` 原配置为 prompt 型 hook，matcher 为 Bash——每执行一条 Bash 命令（包括 ls、grep 等）都要先经过一次 LLM 判断"是否包含 git commit"，显著拖慢所有命令执行。
**根因分析：** "是否为 git commit 命令"是确定性字符串匹配问题，不需要 LLM 判断；prompt 型 hook 用错了场景。
**修复方案：** 改为 command 型 hook，由 `.claude/hooks/check-commit.py` 做字符串匹配：非 commit 命令零开销放行；commit 命令无 `# review-passed` 标记时 exit 2 拦截并提示先完成 py-code-review 审查，审查通过后附加标记放行。
**修复状态：** 已修复
