# 从历史会话与项目反哺 Skill 方案（2026-10-30）

> 状态：**第一、二批已完成**（2026-10-30）；第三批（B1 / C2 / F）与 D 组待启动。
> 调研范围：MyProject 下 12 个项目的代码与文档、约 160 条记忆、约 60 个历史会话（去重后 776 条用户原话）。

## 一、调研结论（依据）

### 1. 每次都要手动讲一遍的流程（最该做成 skill）

| 流程 | 证据 |
|---|---|
| Linux 改代码 → 给 Windows 提示词 → 回执 → 审批 → 复验 | 「给提示词」「回执来了」类诉求约 87 次，涉及 MSCA、iPhoneUsbTouch、MoneyFree、AiTestProject；提示词已出现 13 份以上，结构基本固定 |
| 发版：版本号、CHANGELOG、打标签、打包、Windows 验收 | 约 53 次；版本号被纠正过（0.3.3 被写成 0.4、1.0.5 跳号）；「没说就不打包」 |
| 收工写归因 | 4 个项目的记忆里都有 `write-postmortem-after-fix`；「以后都要记得这个动作」 |
| 界面改动先自己截图 | 4 个项目的记忆都有；「你为什么没有自检出来」 |
| 只读通读、找隐藏 bug | 约 29 次；「先不改，你阅读下…」 |
| 切换工作目录、迁移记忆和会话 | 至少 5 个会话重复「挪过来、继承记忆、删掉原处」 |
| 中断后恢复 | 「恢复你的任务继续执行」23 次 |

### 2. 跨项目稳定的工程惯例

- 规则单源：AGENTS.md 和 CLAUDE.md 之间一方引用另一方；记忆进仓库，跨机器共享。
- Python：uv + 国内镜像，ruff（新项目）、`src/` 布局，FastAPI + pydantic-settings，pytest 标记 unit/integration/smoke，覆盖率只升不降，Nuitka 打包。
- 文档：`docs/` 下用中文命名的成套文档，包括问题归因、打包发布、快速开始、开发说明。
- 提交：前缀英文、描述中文；禁止 `git add .`；推送到 Gitee。

### 3. 现有 skill 的问题

- `py-code-review` 只认 Flake8/Black/isort，新项目已经换成 ruff。
- `mwj-design-system` 实际只有 AiTestProject 和 game-auto 遵循；MoneyFree、ZhiWen 自成一个变体；MSCA、Sujian、AutoAppAgent 是独立风格，规范里没有写清适用边界，也没有暗色模式。
- 各项目里的 skill 副本已经和本仓库的版本对不上：
  - MoneyFree 的 design-system 多出 2 份 reference；
  - AiTestProject 的 delegate-to-cli 还是旧版，没有 Claude 模式；
  - `mwj-autonomous-ui-skill-v3`、`agent-rules-single-source`、`msca-handoff` 只存在于各自项目里，没有收进本仓库。

## 二、Skill 方案

### A 组：工作流类（价值最高）

| # | Skill | 触发 | 核心内容 |
|---|---|---|---|
| A1 | `device-handoff` 双机真机联调 | 「给 Windows 提示词」「回执来了」「复验」「写回执」 | 双角色。**Linux 侧**：按固定结构生成提示词（目标与边界 → 规矩 → 第 0 步核对提交和工作区 → 分组步骤 → 回执要求）；下发前自检（只问人看得见的、一轮只解决一个问题、不让验 UI、已验过的不重复）；读回执时先核对日期、提交、文件时间再判定；生成复验提示词。**Windows 侧**：泛化现有的 msca-handoff。凭据一律从本地配置读，不写进模板 |
| A2 | `release-ship` 发版 | 「发版」「打包」「出 vX.Y.Z」 | 门禁通过 → 版本号只升末位且先确认 → 版本号多处同步 → CHANGELOG「未发布」改成版本号 → `chore(release)` → 打标签 → 推送 Gitee → 调用 A1 生成 Windows 打包验收提示词。没要求就不打包；产物不进仓库 |
| A3 | `postmortem` 收工归因 | fix 收尾、问题确认解决、「写归因」 | 三档粒度：单行表 / 条目 / 独立归因文档（结论 → 现象原话 → 根因按证据分级 → 改动 → 时间线 → 为何难找 → 教训 → 涉及代码）。收工时主动交付，并把教训同步进记忆 |
| A4 | `session-handoff` 交接、迁移、恢复 | 「收工」「交接」「挪到 X 目录」「恢复任务」 | 收工时更新进度、写入仓库记忆和索引、列出未完成项；迁移时把记忆和会话搬过来，核对后再清理原处；恢复时读进度文件，接着做并汇报 |
| A5 | `project-readthrough` 只读通读 | 「通读」「找隐藏问题」「先不改」 | 严格只读；按模块派子代理（复用 delegate-to-cli）；结论分「已证实」和「疑似」，按 ROI 排序后落到 `.planning/`；用选项让用户挑要改的项，确认后再动手 |

### B 组：工程规范类

| # | Skill | 内容 |
|---|---|---|
| B1 | `mwj-project-init` 项目脚手架与规范对齐 | 吸收 agent-rules-single-source。新建项目时生成：AGENTS.md 单源、`docs/` 中文套件、记忆入仓、uv、ruff、`src/` 布局、`start.sh` 和 `start.ps1`、`scripts/check.sh`、pytest markers、用 `importlib.metadata` 读版本、gitignore。已有项目可以做「规范对齐审计」，例如顺带修掉 AiTestProject 和 MSCA 示例命令里的 `git add .` |
| B2 | `py-code-review` 升级（不新建） | 自动识别 ruff 或 flake8+black；加入梦无矶特有的审查项：中文注释写「为什么」和实测出处、设备命令用参数列表并加超时、协议只增不改、`raise from`、版本号漂移 |

### C 组：前端类

| # | Skill | 内容 |
|---|---|---|
| C1 | `ui-selfcheck` 前端截图自检 | 和 `mwj-autonomous-ui-skill-v3` 合并评估。内容：优先复用仓库已有的截图脚本；桌面和手机两个视口；有数据、空状态、弹窗三种状态；每张图都要真的看；从导航实际点进页面；不允许横向滚动、控制台不能报错；附已知坑清单（Vue 模板里的 `{{`、ECharts 组件注册、Vite HTTPS、CHOKIDAR_USEPOLLING） |
| C2 | `mwj-design-system` 升级到 v2.0 | 拆成三部分：core（Token、暗色）、vue-element 实现层（含 echarts 模板）、变体（MoneyFree 系的大圆角和深色侧栏）。写明适用边界（不管 React/Electron 独立品牌）。把各项目副本里多出来的 reference 收回来 |

### D 组：领域类（建议放在**项目内**，不进 mwj-skills）

| # | Skill | 位置 |
|---|---|---|
| D1 | `novel-anti-ai-review` 反 AI 味审稿：句长、碎句率、句号率、口癖、手续词、数字密度、人名性别一致性 | Sujian |
| D2 | `ios-usb-device-kb` iOS USB 真机知识：CoreDevice HID、usbmux、DDI、版本门槛 | iPhoneUsbTouch，MSCA 和 imirror 引用它 |
| D3 | `anamana-api-testing` 接口测试口径：废弃接口、required 标记不可信、分档验证、重试 3 次 | AiTestProject |

> 用户决定（2026-10-30）：D 组**也收进 mwj-skills**，集中管理，各项目引用。

### E 组：不适合做 skill，建议写进用户级 `~/.claude/CLAUDE.md`

这些偏好每个会话都适用，放进 skill 反而可能不触发：

- 简体中文、大白话、先说结论、汇总式汇报
- 需要你拿主意时用选项提问并标出推荐项
- 方案确认后自主执行，**没说做就不改代码**（目前两条记忆说法相反，需要统一口径）
- 模型优先级 Fable 5.1 → Opus 5.5，子代理同样遵守
- 杀进程按项目路径过滤；多个会话并行时用 worktree，或改完立刻提交

### F 组：杂项治理

- 建立 skill 分发机制：本仓库为唯一源，各项目用软链或同步脚本引用，消除副本漂移。

## 三、建议施工顺序

1. **第一批**：A1、A3、A2（流程最痛、重复最多）
2. **第二批**：C1、B2、A5、A4
3. **第三批**：B1、C2、F
4. **按需**：D 组（在各自项目里做）、E 组（改用户级配置）

每个 skill 都按本仓库流程走：开发 → 审查 → 用一个真实项目试跑 → 同步 README、CLAUDE.md、changelog → 提交。

## 四、用户决策（2026-10-30）

- 先做第一批：A1 + A3 + A2
- A1 device-handoff：一个 skill，按角色区分 Linux 下发侧和 Windows 执行侧
- E 组全局偏好：暂不处理
- D 组领域 skill：也收进 mwj-skills

## 五、第一批任务清单

- [x] T1 读素材：msca-handoff、MSCA doc/联调/README、iPhoneUsbTouch 打包发布 §7、MoneyFree 回执模板与 AGENTS 跨机器协作、历史提示词样本
- [x] T2 A1 device-handoff：SKILL.md + references/（提示词模板、回执模板、下发自检清单、审批清单）
- [x] T3 A3 postmortem：SKILL.md + references/（三档模板）
- [x] T4 A2 release-ship：SKILL.md + references/（版本号位置探测、Windows 打包验收提示词，引用 A1）
- [x] T5 审查：按 skill 规范自查 frontmatter/触发词/路径；用 MSCA 或 MoneyFree 真实素材试跑一遍生成结果
- [x] T6 同步 README、CLAUDE.md 项目概述表、docs/changelog.md；分 skill 提交

### 第一批审查结论（2026-10-30）

子代理只读审查，并在 iPhoneUsbTouch、MSCA、MoneyFree 上干跑。查出 P0 2 条、P1 9 条，均已修复：
- P0：版本号 grep 会误改「X.Y.Z 起」这类历史说明 → 只改「当前版本声明」，并排除 target/dist 目录。
- P0：MSCA 的模型是「验收后打 tag」，与原写法的发版顺序相反 → 改为识别 A/B/C 三种发版模型；执行侧补充「任务单明确授权的发版动作」这一例外。
- P1：文档路径探测不全、未判断该不该升版、审批清单缺少旧包/人工互证/发布类核对项、没有空闲任务单约定、触发词过宽、归因的提交时机前后矛盾。

## 六、第二批任务清单（2026-10-30 启动）

- [x] U1 素材：截图自检现有脚本（AiTestProject scripts/lib、MoneyFree shot_pages.py、MSCA/Sujian 做法）+ mwj-autonomous-ui-skill-v3
- [x] U2 素材：通读审计（MSCA .planning 通读笔记、iPhoneUsbTouch v0.3.2 通读清单）+ 会话交接/迁移/恢复（handoff 记忆、sync_memory.py、progress.md）
- [x] U3 B2 py-code-review 升级：ruff 工具链探测 + 梦无矶特有审查项
- [x] U4 C1 ui-selfcheck
- [x] U5 A5 project-readthrough
- [x] U6 A4 session-handoff
- [x] U7 审查 + 真实项目干跑；修复
- [x] U8 同步 README / CLAUDE.md / changelog；分 skill 提交并推送 Gitee

### 第二批审查结论（2026-10-30）

子代理只读审查，并在 iPhoneUsbTouch、OcrYoloEngine、MwjZhiWen、MwjAppPrefTrace、imirror 上干跑。查出 P1 5 条、P2 十余条，均已修复：
- shot.py：favicon 404 被误报 → 已过滤，「Failed to load resource」不再重复计数；交互步骤失败时整批中断 → 改为记进 step_errors 后继续截图；开启 --full-height 时文件名与实际尺寸不符 → 已修正；新增 allow_errors，用于截失败态。
- copy_sessions.py：出错后仍打印「全部一致」→ 已修正；会话 id 未校验，存在路径穿越 → 增加 UUID 校验；新增「源桶等于目标桶」时拒绝执行。
- project-readthrough：「零改动」与在仓库里建 .planning 相矛盾 → 工作目录默认放到仓库外；与 delegate-to-cli 的触发词划清界限。
- py-code-review：执行门禁脚本时不再运行会改环境的步骤，命令前缀改为 .venv/bin 或 --no-sync；pyflakes 规则并入第 1 档；description 限定为 Python。
- mwj-conventions：只审 diff 中的行，带理由的 noqa 不报，服务类条目单独标注。

干跑附带发现（不属于本仓库）：
- imirror 的 tests/test_windows_tools.py 在 Linux 上失败，属于 Windows 专用测试却没加 skip。
- MwjAppPrefTrace 报告页在手机宽度下横向溢出 503px，卡片内的长文本超出卡片。
