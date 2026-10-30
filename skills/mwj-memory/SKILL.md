---
name: mwj-memory
description: AI 助手记忆的存储方式：选方案（同步脚本 / 软链 / 根目录 MEMORY.md）、搭建、日常写入规范、本机桶与仓库的三方同步（scripts/memory_sync.py：冲突不覆盖、删除不自动传播、敏感信息拦截、加锁）、定期审计（格式、索引、过期、敏感信息、@ 导入是否生效）。用户说「记忆进仓库」「换电脑记忆就没了」「同步记忆」「整理记忆」「审计记忆」「记忆太乱」「记忆存储方式」时触发；新项目初始化共享记忆（mwj-project-init）或迁移记忆（session-handoff）时配合使用。
---

# MWJ Memory：记忆存储方式

用户原话：「我的长期记忆需要上传到仓库，换了电脑你就没了」「之后不管是我换电脑还是开新的会话都要遵守」「不能全我来盯着还教你，你自己也要学习」。

**记忆要跟着仓库走，随时能同步，而且不能误导人。**

## 第 1 步：先看现状

```bash
python <skill 目录>/scripts/memory_sync.py audit --repo . --target repo    # 仓库侧
python <skill 目录>/scripts/memory_sync.py audit --repo . --target local   # 本机桶
grep -n "MEMORY.md" CLAUDE.md AGENTS.md
```

本机桶的位置：`~/.claude/projects/<仓库绝对路径里非字母数字字符都换成 -了>/memory/`。会话必须**从项目目录启动**，否则写进的是别的桶，还会把别的项目的记忆灌进当前上下文。

## 第 2 步：选方案（新项目，或现有方案出问题时）

| 方案 | 怎么做 | 适合 | 代价 |
|---|---|---|---|
| **A 同步脚本**（推荐） | 本机桶 ⇄ `docs/memory/`，用 `memory_sync.py sync` 做三方同步 | Claude 和 Codex 混用、多台机器 | 要记得跑同步；冲突需要人工处理 |
| **B 软链** | 把本机桶的 `memory/` 软链到仓库的 `docs/memory/`（`memory_sync.py link`） | 只用 Claude、机器固定 | 每台新机器都要重新建链；改完不提交就丢 |
| **C 根目录 MEMORY.md** | 一份分节的单文件，在 CLAUDE.md / AGENTS.md 里用 `@MEMORY.md` 导入 | 记忆少、规则多 | 没有逐条的 type 和 Why，越写越长 |

不管选哪个方案，都**必须用 `@` 导入索引**（`@docs/memory/MEMORY.md` 或 `@MEMORY.md`）。只用文字写「先读 MEMORY.md」不会被加载：MSCA、MwjAppPrefTrace、MwjRunner、MwjZhiWen 都出过这个问题。

方案定下来后，写进 AGENTS.md 的「记忆」一节（模板见 mwj-project-init）。

## 第 3 步：日常写入（格式见 `references/format.md`）

- 一条记忆一个文件，frontmatter 写 `name`、`description`、`metadata.type`（user / feedback / project / reference），正文按「事实 → **Why:** → **How to apply:**」写，用 `[[名字]]` 链接相关记忆。
- 写之前先查有没有已经覆盖这件事的记忆：**有就更新那条，不新建**。发现有错的记忆就删掉。
- **该记**：用户的决定和偏好（照抄原话、写上日期）、踩过的坑及其原因、外部资源的位置、指向权威文档的入口。
- **不该记**：代码或 git 历史里本来就有的东西；一次性的进度；**易变的状态和版本号**（写进文档，记忆里只放指向文档的指针）；凭据、IP、账号、私有路径。
- 和某一份具体内容绑定的记忆（比如某本书、某台设备），放到跟着那份内容走的目录里，不要放进通用记忆。

## 第 4 步：同步（方案 A）

```bash
python <skill 目录>/scripts/memory_sync.py check --repo .          # 只报告，有差异时退出码为 1
python <skill 目录>/scripts/memory_sync.py sync --repo .           # 演练
python <skill 目录>/scripts/memory_sync.py sync --repo . --apply   # 执行
```

| 情况 | 脚本的处理 |
|---|---|
| 只有一边改了 | 同步到另一边 |
| 两边都改了 | **报冲突，不覆盖**：读两份、手工合并后再同步；首次同步、确定以某一边为准时，可以加 `--prefer local` 或 `--prefer repo` |
| MEMORY.md 两边都改了 | 按行取并集，不丢条目；但删掉的行可能被另一边带回来，合并后要人工看一眼 |
| 一边删了 | 只报告；确认要删时加 `--apply-deletes`（以前误删过记忆） |
| 内容疑似含内网 IP、口令、密钥 | 拒绝写进仓库，改写后再同步 |
| 两个会话同时同步 | 用锁文件拦住；持锁进程已经退出的，自动接管 |
| 本机桶是软链（方案 B） | 指向仓库目录：不需要同步，改跑敏感扫描；指向别处：报错停下 |

同步完成后，到仓库里审阅改动，`git add docs/memory/<具体文件>` 后提交，提交信息用 `docs(memory): …`。

## 第 5 步：定期审计（每批大活收工时，或者用户觉得记忆乱了时）

`memory_sync.py audit` 会自动检查以下各项。方案 C（`--repo-dir .`）只审带 frontmatter 的文件。
- frontmatter 是否齐全、type 是否合法
- feedback/project 类有没有写 Why（「Why」「为什么」都算）
- 索引和文件是否一一对应
- 有没有敏感信息
- project 类记忆是否超过 60 天没更新：优先看 frontmatter 的 `updated`/`modified`，其次看文件修改时间
- `@` 导入是否生效

另外要人工复核（见 `references/format.md` 末尾的审计清单）：

- 记忆里提到的版本号、状态，和当前的 tag、代码对不对得上；对不上的改成指针，或者直接删掉。
- 同名记忆在多个桶里有不同版本的，合并成一份，放进对应项目的桶。
- 上层目录的桶（例如从 `~` 或 `MyProject/` 启动时写进去的）里有没有本项目的残留。
- 「禁令」类记忆是否已经作废（例如「某项目已发版，别动」）。

审计结果要先汇报：列出问题，用选项让用户决定删、改还是留。**不要擅自批量删除**。

## 硬规则

- 记忆只读写本项目的桶；上下文里出现别的项目的记忆，忽略它。
- 公开仓库里的记忆：不写书名、人名、内部系统、IP。
- 删除任何记忆原件之前，要先得到用户授权。两个会话都整理过的目录，留哪一份由用户决定。
