# 联调协议 README 模板

项目还没有联调协议、用户选了「仓库协议」时，用这份模板创建 `docs/联调/README.md`，并创建 `docs/联调/回执/`、`docs/联调/历史任务/` 两个目录，各放一个 `.gitkeep`。同时在 AGENTS.md（或 CLAUDE.md）里加一句：「Windows 侧收到『按联调任务执行』时，读 docs/联调/README.md 并照做」。

````markdown
# 跨机器联调协议（Linux 开发机 ⇄ Windows 真机）

> 读者：Windows 那台机器上的 AI 助手（Claude Code / Codex），以及人。
> 两边只通过 git 交换信息，不靠人肉复制日志。

## Windows 侧每次要做的事

1. `git pull` 任务单写明的分支。
2. 打开 `docs/联调/当前任务.md`，**只做上面写的事**，按顺序，不改代码。如果写的是「当前没有待执行的联调任务」，就回复一句后停下，不重跑历史任务。
3. 结果写成回执：`docs/联调/回执/<YYYY-MM-DD>-任务<编号>.md`，格式见下。
4. `git add docs/联调/回执/<文件>` → `git commit -m "test(<scope>): 联调回执 <编号>"` → `git push`。
5. 回复人一句话：通过 / 部分通过 / 阻塞 + 回执文件名。然后停下。

## 不要做的事

- 不改源码；不改 `当前任务.md`；不提交二进制。
- 不截断日志；不超过允许的重试次数。
- 不碰桌面（不点界面、不截图、不抢焦点）；装包、重启、拔插先问人。

## 启动方式

对 Windows 侧的 AI 说「按联调任务执行」即可。

## 回执格式

<粘贴 device-handoff/references/receipt-template.md 的骨架>

## 目录

| 路径 | 谁写 | 内容 |
|---|---|---|
| `docs/联调/README.md` | Linux | 本协议 |
| `docs/联调/当前任务.md` | Linux | 当前待执行的一份任务单 |
| `docs/联调/回执/` | Windows | 每次执行的回执，不删不改旧的 |
| `docs/联调/历史任务/` | Linux | 已完成任务单归档 |
````
