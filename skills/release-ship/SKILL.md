---
name: release-ship
description: 发版流程（Linux 定版 → Windows 打包验收 → 审批 → 正式发布）。先判断该不该发、确认版本号（默认只升末位，不跳号）、门禁、同步当前版本声明、CHANGELOG「未发布」转版本、提交与附注标签、推送；Linux 打不了的包交给 device-handoff 生成 Windows 打包验收提示词；审批通过后合并主分支、发布 Release 等对外动作逐项确认。用户说「发版」「定版」「出 vX.Y.Z」「打 tag」「发布 Release」「打包 exe/apk/安装包」时触发。没要求打包时不要主动打包。
---

# Release Ship：发版

用户纠正过的事，先记住：

- 「不对啊，应该是 0.3.3 啊。你怎么就到 0.4 了」「怎么一下到了 1.0.5」→ **版本号不自作主张，默认只升末位，先确认**。
- 「以后我没说你就不用打包 apk 了」→ **只打用户这一轮要求的产物**。
- 产物（exe / apk / zip / 7z）**不进仓库**。

## 第 0 步：读项目的发版规矩，识别发版模型

```bash
grep -nE "发版|版本号|打包|release|Release|tag" AGENTS.md CLAUDE.md 2>/dev/null | head -30
ls doc*/*发布*.md doc*/*发版*.md doc*/*更新日志*.md CHANGELOG.md 2>/dev/null
git tag --sort=-creatordate | head -5; git remote -v; git branch -a | head
```

项目文档有发版章节（如 iPhoneUsbTouch `docs/打包发布.md §7`、MoneyFree `AGENTS.md`「跨机器协作」与 `docs/开发与发布.md`、MSCA `doc/发版信息.md`）→ **以项目为准**，本 skill 只补它没写的部分。

识别属于哪种模型，后续步骤按模型走：

| 模型 | 特征 | 例子 |
|---|---|---|
| **A 先定版后打包** | Linux 改版本号 → 提交 → 打 tag → 推送；Windows 按 tag 打包验收 | iPhoneUsbTouch |
| **B 验收后打 tag** | 在开发分支改版本号并推送；Windows 打包、人工验收通过后，把开发分支 `merge --no-ff` 进 master，在合并提交上打 tag，再发 Release | MSCA（develop → master） |
| **C 发布点 / 迭代包** | 每打一次包末位 +1，不一定每次打 tag；回执审批制 | MoneyFree（R<N> 发布点） |

拿不准就用 AskUserQuestion 问一次。

## 第 1 步：该不该发、发哪个版本号（必须确认）

1. 读当前版本（最新 tag + 版本文件），列出上个 tag 以来的提交摘要。
2. **先判断要不要升版**：
   - 上个 tag 以来没有代码变更（只有文档）→ 建议不升版（MoneyFree 规则：只改文档、不打包的推送不加版本号）。
   - 上一版还没验收（CHANGELOG 或回执里写着「尚未真机验证」）→ 建议先补验收上一版，而不是升新版。
3. 默认建议 **末位 +1**；项目规则另有规定的按项目来（MoneyFree：每打一次包末位 +1，开新发布点升中间位）。
4. 用 AskUserQuestion 确认，推荐项放第一个。**用户没有明确同意，不升中间位或主版本。** 版本号只增不减，不复用（Android 不能覆盖安装更低的版本）。

## 第 2 步：门禁（任一失败 → 停下汇报，不发版）

- [ ] `git status` 干净；当前分支与远端一致（`git fetch && git status -sb`）
- [ ] **项目规定的**检查入口全绿：`scripts/check.sh`、`make check`，或项目文档写明的命令（iPhoneUsbTouch 是 `uv run --frozen pytest -q` 加 `pyflakes`，不用 ruff 默认规则）。项目没规定时，再按技术栈补测试、lint、类型检查。
- [ ] 已发版的下游在调用的协议、错误码、JSON 字段：**只增不改**（`git diff <上个tag> -- <协议文件>` 过一眼）
- [ ] 本轮有界面改动的，已经截图自查过

## 第 3 步：同步**当前版本的声明**

只改「当前版本是多少」的声明。**不改**「X.Y.Z 起支持…」这类历史说明、版本历史、第三方依赖版本、编译产物。

```bash
OLD=<当前版本>
git grep -nIF "$OLD" -- ':!CHANGELOG.md' ':!*.lock' ':!**/target/**' ':!**/node_modules/**' ':!**/dist/**'
```

对照 `references/version-locations.md` 逐条判断哪些是声明，然后一次改完：

- 锁文件单独处理：`uv lock` 后跑 `uv lock --check --offline`；npm 用 `npm install --package-lock-only`
- 项目有版本一致性检查的（如 `tests/test_version.py`、`npm run check:version`）要跑一遍
- 文档里的协议示例版本号、产物路径示例一起改

## 第 4 步：CHANGELOG

沿用最近一个版本的标题格式：iPhoneUsbTouch 是 `## 未发布` → `## vX.Y.Z（日期）`；Keep a Changelog 风格的是 `## [未发布]` → `## [X.Y.Z] - 日期`。上方新开一个空的「未发布」段。条目写用户看得懂的变化，不要直接贴 commit 列表。

## 第 5 步：提交、打标签、推送

```bash
git add <逐个列出改动的文件>          # 禁止 git add .
git commit -m "chore(release): vX.Y.Z"
```

- **模型 A**：`git tag -a vX.Y.Z -m "vX.Y.Z"` → `git push <远端> <分支> vX.Y.Z`
- **模型 B**：这一步只推开发分支，**先不打 tag**；tag 在第 7 步合并后，打在主分支的合并提交上
- **模型 C**：按项目规则决定打不打 tag，一般只推送

远端以 `git remote -v` 和项目规矩为准（通常是 Gitee）。

## 第 6 步：打包

- **Linux 能打的**（wheel、Linux 包、Docker 镜像）→ 直接打，产物放在已 gitignore 的目录，报告路径、大小、SHA256。
- **Windows / 真机产物**（exe、安装包、APK）→ 调用 `device-handoff` skill，按本 skill 的 `references/windows-build-prompt.md` 生成打包验收提示词。项目文档里已有现成提示词的（如 iPhoneUsbTouch §7.3），以它为底，补上拉取时间、产物校验、「不做」三节，路径改用正斜杠。
- **只打用户这一轮要求的产物**：APK、安装包、压缩格式（7z / zip）都按用户说的来，没说的写进提示词的「不做」一节。

## 第 7 步：审批与正式发布

1. 回执到了，按 device-handoff 的审批清单逐项核对：tag 或 commit、退出码、产物版本号、修改时间、SHA256（**和上一轮完全相同说明是旧包**）、build-stamp。
2. 审批通过后，把对外动作逐项列给用户，**每一项单独确认后才执行**：
   - 模型 B：`merge --no-ff` 开发分支进 master → 在合并提交上打 tag → 推送
   - 发布 GitHub / Gitee Release，上传产物；各渠道发布的边界按项目规则，例如 MSCA 在 Gitee 不上传 exe
   - 推送到其他远端、通知相关人

   这些动作可以由 Linux 侧做，也可以写进任务单交给执行侧做（device-handoff 执行侧遇到「任务单明确授权的发版动作」属于例外）。不论谁做，都把用户的确认原话抄进回执，例如「确认合并master」「确认打tag」「确认发布 Release」。
3. 发布后检查下游：如果下游项目会把本项目产物打进自己的包（例如 MSCA 打包时会带上 iostouch），提醒用户，下游重新打包就会带进新版本，需要重新验收。

## 汇报

结论先说：vX.Y.Z 走到哪一步了（已定版 / 等打包回执 / 已发布）。然后给出产物和校验值。最后写清还差哪一步、需要用户做什么。
