---
name: delegate-to-cli
description: 把读多写少、可独立验证的子任务委派给本地 CLI 智能体（kimi-cli / codex），并行起飞，回收后由你严格验收，不满意要它重做（最多 3 次）。支持 5 种模式：纯 kimi、纯 codex、kimi 跑+codex 复审、kimi+codex 并行、外部 sub-agent 跑完 + 主 agent 终审。每次跑完输出每个 sub-agent 的 token 用量及对比 Claude 单跑的节省比例。当用户提到"派 kimi/codex 跑"、"指挥 sub-agent"、"分发任务"、"整体巡检/审计/对账"、"再用 codex/kimi 复审一遍"时触发；当主任务可拆成 2 个以上互不依赖、读多写少的并发子任务时也应主动考虑触发。
---

# Delegate-to-CLI

把可以独立完成、产出格式可验证的子任务**派**给本地命令行 AI（`kimi-cli` 或 `codex exec`），主 agent 留在主线做综合判断。**不要**把需要主上下文、需要写文件、或需要跨任务协调的活派出去。

每次任务结束输出 **token 用量 + 节省估算**（见末尾 §Token Reporting）。

## 触发场景与不触发场景

**触发**：
- 全仓代码审计 / 合规扫描 / Phase 进度审计 / 文档对账
- "整体巡检"、"看看现在到什么程度了"等跨多文件的报告型问题
- 一次需要并行调查 2 个以上独立点（比如同时审计代码、文档、配置）
- 写完代码后要"再帮我核一遍"的二次复核

**不触发**：
- 单文件、单函数级别修改 → 主 agent 直接做
- 需要修改文件的实现任务 → sub-CLI 写完无法保证不偏，主 agent 自己写更安全
- 跨子任务有数据依赖 → 不能并发，分开主 agent 做更快
- 涉及需要审批、产生副作用、动 git/远端的操作 → 主 agent 做，留审批链路

## 5 种执行模式

按"任务确定性 / 你对 sub-CLI 的信任度 / 时间预算"组合选择。

### Mode 1: kimi-only
**何时用**：中文长文档审计、跨多文档对账、产出报告型；**任务难度中低、信任度足够**，不需要复审。
**流程**：拆任务 → 并发派 kimi → 主 agent 抽查 → 综合。
**典型场景**：审计文档进度、列任务清单、跨多个目录读完写一份汇总。

### Mode 2: codex-only
**何时用**：精确代码语义任务（行号、调用图、函数签名审计）；**任务对行号准确度要求极高**。
**流程**：拆任务 → 并发派 codex → 主 agent 抽查 → 综合。
**典型场景**：合规扫描（grep + 代码语义判断）、API 行为审计、跨模块调用一致性。

### Mode 3: kimi 先跑 → codex 复审（**强烈推荐做"重要审计"时使用**）
**何时用**：你对结果可疑、想交叉验证；或者第一轮要快速看全貌、第二轮要核实证据。
**流程**：
1. kimi 并发产出第一轮报告（覆盖广、自然语言）
2. 把 kimi 报告作为待验事实清单丢给 codex，让它对每条 PASS/FAIL 给 CONFIRM/DISPUTE/UNVERIFIABLE
3. 主 agent 抽查 codex 的 DISPUTE → 综合两轮形成最终结论

**实战经验**（2026-05-26 跑 4 个子任务）：codex 复审揪出 kimi 4 处错误（含 1 处重大状态误判），成本约为 kimi 总量的 30%。

### Mode 4: kimi + codex 并行 → 主 agent 综合
**何时用**：要快、又想要二审；任务足够独立且 prompt 可以同时丢给两个 CLI。
**流程**：同一份 prompt 同时派给 kimi 和 codex（**不**让它们看对方）→ 主 agent 同时收两份独立结论 → 哪条声明两边一致 = 高置信，哪条分歧 = 主 agent 亲自核。
**注意**：成本最高、但对主 agent 的综合压力最小。

### Mode 5: 外部 sub-agent 跑完 → 主 agent 终审 + 计算节省
**何时用**：sub-CLI 报告已经回收完，你要主 agent 做最后一遍**结论性校验**，并产出 token 节省报告。
**流程**：
1. 收齐所有 sub-CLI 产出
2. 主 agent 抽查 4-6 条强声明（用 Read/Bash 自己核）
3. 输出综合报告 + 调用 `token_report.py` 出 token 节省估算

> 这个模式可以追加在 Mode 1/2/3/4 任意一个之后。强烈建议每次都跑 Mode 5 收尾。

## 适合派给 sub-CLI 的子任务特征（必须全部满足）

1. **只读为主**：grep / 读文件 / 列举 / 比对清单 / 写报告
2. **可独立完成**：不需要主线上下文也能独立做
3. **产出格式严格可验证**：能抽查一两条强声明就知真假
4. **失败可重试**：报告偏题/格式错/伪造数据时可以让它重做

## 选 kimi 还是 codex

| 倾向 | kimi-cli | codex exec |
|---|---|---|
| 优势 | 中文长文档审计；自然语言报告；MCP 工具链丰富；prompt cache 命中率高（同 hash 内复用） | 代码理解力强；行号精准；产出更稳；适合做强结构化代码审计 |
| 默认 | 中文报告 / 文档对账 / 探索性问题 | 代码语义检查 / 行号级证据 / cross-check |
| Token 计费 | input_other + cache_read 拆开计 | 只给一个聚合 `tokens used`，区分粒度低 |

不确定时默认用 kimi（cache 友好），结果可疑用 Mode 3 跑 codex cross-check。

## 调用模板

### kimi-cli

```bash
kimi-cli --print --yolo --quiet \
  -w <PROJECT_ROOT> \
  -p "$(cat /tmp/<session>/prompt_X.txt)" \
  > /tmp/<session>/out_X.md 2> /tmp/<session>/err_X.log
```

`--print` = 非交互；`--yolo` = 自动批准；`--quiet` = 只输出最终消息。**`err_X.log` 末尾会带 session id**（`To resume this session: kimi -r <SID>`），后续 token 报告必须收集这个 SID。

### codex exec

```bash
cat /tmp/<session>/prompt_X.txt | codex exec \
  -C <PROJECT_ROOT> \
  --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  -o /tmp/<session>/out_X.md \
  - > /tmp/<session>/log_X.txt 2>&1
```

`-o` = 最终消息写到文件；stdin 传 prompt 避免 shell 长度限制；**`log_X.txt` 包含 `tokens used` 行**，token 报告会从这里解析。

## 执行流程（每次都按这个走）

### 1. 拆任务
列出独立子任务清单（写在主回复或 TaskCreate 中）；为每个子任务标"派给谁/我自己做"。**只把适合的派出去**。

### 2. 写 prompt（关键）

每个子任务一个独立 prompt 文件 `/tmp/<session-name>/prompt_<X>.txt`，必须包含：

- **角色定位**：一句话告诉它是审计员/对账员/什么角色
- **仓库根**：绝对路径
- **任务范围**：列哪些文件 / 哪些 grep / 哪些文档要读
- **检查点清单**：每条让它给 PASS/FAIL + 文件:行号证据，禁止泛泛而谈
- **输出格式**：用 Markdown 表格或固定 section，行数上限（防长篇大论）
- **必抽查的强声明**：让它对几个关键点给具体行号，方便事后核

> ❌ 不要写"看看代码有没有问题"  
> ✅ 写"对 8 个正式 DAG 模块，每个给 5 个检查点的 PASS/FAIL + 行号证据"

### 3. 并发起飞
多个子任务**同一条消息**里用 Bash + `run_in_background:true` 全部并发启动。kimi/codex 单跑 1-3 分钟，4 个并发约等于 1 个串行。

### 4. 收回 + 验收（4 关）

每份产出过这 4 关：
1. **完整性**：文件大小不是 0；日志没崩溃
2. **格式**：是否按要求的格式（如表格头是否齐）
3. **抽查强声明**：对它报的至少 1-2 条具体行号 / grep 命中 / 文件路径，主 agent 用 Read/grep 复核
4. **结论一致性**：如果一份说"无 P0"，看它是不是真的 grep 过；如果声称某行是 bug，主 agent 看那行真不真

### 5. 不满意 → 重做（最多 3 次）

判定为不满意的常见情形：
- 偏题 / 没按格式
- 抽查强声明造假（最严重，必须重做）
- 漏掉显著范围

重做时：在原 prompt 上**追加**具体反馈（"上一轮你漏了 X / 行号 Y 说法错误，请重做并补上 Z"），不要换一份新 prompt。

3 次仍不行 → 主 agent 自己做该子任务，并在最终汇总里标"sub-CLI 重试 3 次未通过，本节由主 agent 完成"。

### 6. 综合 / 自核 / 汇总

主 agent 读所有产出，**自己再把抽查放大到 4-6 条强声明**核一遍，再产出综合报告。**不要直接转发 sub-CLI 的结论**。

### 7. **Token 报告（必出）**

跑 `token_report.py` 出本次任务的 token 用量 + 节省估算（见下一节）。

## Token Reporting

### 工作目录约定（写 prompt 时一并按这个路径走）

把每次任务的产物按 `<session-name>` 隔离：
- `/tmp/<session-name>/prompt_<X>.txt` — prompt
- `/tmp/<session-name>/out_<X>.md` — 子任务最终消息（kimi 用 `--quiet > out_X.md`；codex 用 `-o out_X.md`）
- `/tmp/<session-name>/err_<X>.log` — kimi 的 stderr（含 session id）
- `/tmp/<session-name>/log_<X>.txt` — codex 的 stdout（含 `tokens used`）

### 收集 session id / log path

**kimi**：每个子任务跑完后，从 `err_<X>.log` 末尾的 `To resume this session: kimi -r <SID>` 提取：
```bash
grep "kimi -r" /tmp/<session>/err_A.log | awk '{print $NF}'
```

**codex**：日志路径就是 `log_<X>.txt`，`token_report.py` 自己从里面提 `tokens used` 行。

### 跑报告

```bash
python3 ~/.claude/skills/delegate-to-cli/token_report.py \
  --kimi A:<sid_A> B:<sid_B> ... \
  --codex A:/tmp/<session>/log_A.txt B:/tmp/<session>/log_B.txt ... \
  --claude-overhead 80000 \
  --out /tmp/<session>/token_report.md
```

`--claude-overhead` 是主 agent 自己写 prompt + 读结果 + 综合的估算 token；首次用默认 50,000，发现明显偏离再调。

### 报告内容（自动生成）

- **每个 sub-CLI 子任务**：input_other / cache_read / output / grand 各一行
- **小计**：kimi 总和、codex 总和
- **委派总成本**：sub-CLI 总和 + Claude 主 agent 协调开销
- **Claude 单跑预估范围**：
  - 下限 = 等量 grep/read 的 token（≈ 委派总量）
  - 上限 = 委派总量 + 主上下文累积（每个子任务都重复读前面的上下文）
- **两种节省口径**：
  - **总 token 节省**（含 sub-CLI 计费）：(单跑预估 − 委派模式总成本) ÷ 单跑预估
  - **主 agent 节省**（只看主会话承担的 token）：(单跑预估 − 主 agent 协调开销) ÷ 单跑预估

### 注意：两种节省口径的真实含义

- **总 token 节省**通常很小、有时为负 — 因为子任务的 token 仍然要有人消耗（只是从主 agent 转嫁到 sub-CLI），全局工作量没减。
- **主 agent 节省**才是核心指标 — 主会话只承担"写 prompt + 读报告 + 综合"，重活全转嫁。这个比例通常 90%+，意味着：
  - 主上下文不被中间 grep/read 输出污染
  - context window 撑得住更长的对话
  - 主 agent 注意力带宽留给综合判断和决策
- kimi 的 cache_read 比例（典型 80%+）说明跨子任务的系统提示命中缓存，sub-CLI 这部分按计费会打折，间接也降低**总成本**。
- 真正想优化"总 token"：选 cache 友好的 sub-CLI（kimi 比 codex 强），写 prompt 时尽量复用同 hash 的 session（kimi 一次跑多任务）。

## 子任务 prompt 设计要点

好 prompt 长这样（节选）：

```
你是 X 项目的代码审计员。仓库根 /abs/path。

任务：审计 N 个 ETL 模块是否合规切换到 official 库。

对每个模块检查（每条 PASS/FAIL + 文件:行号证据）：
1. 目标库断言: 是否调用 get_official_database(biz)
2. 禁词残留: grep `role="v2"|v2_database|old_database` 是否 0 命中
3. 凭据来源: 是否走 data_spider.config / credentials.json
...

输出格式：
## 全局 grep 结果
（命中行号或 NONE）

## 每模块审计
### <模块名>
- 检查项 1: PASS/FAIL — etl.py:line 证据
...

## SEVERITY SUMMARY
- P0: ...
- P1: ...
- P2: ...

控制输出在 200 行以内。
```

### Mode 3 (cross-check) 的特殊 prompt 模板

```
你是 X 项目的独立代码审计员。仓库根 /abs/path。

任务：cross-check 另一个 AI 给出的"<原任务名>"产出。逐条验证它每个 PASS/FAIL 声明 + 行号证据。

待验产出：
\`\`\`markdown
<把原 sub-CLI 的产出整段贴进来>
\`\`\`

逐条给：
- ✅ CONFIRM：声明属实（不展开）
- ❌ DISPUTE：声明错误，给真实文件:行号反证
- ❓ UNVERIFIABLE：文件不存在或无法判定

净增发现部分（kimi 漏掉但你认为重要的，最多 5 条）。

总评：准确率 X/Y CONFIRM；关键 DISPUTE。
```

## Anti-patterns（不要做）

- ❌ 让 sub-CLI 写代码、改文件、做不可逆操作
- ❌ 不做抽查就直接相信它的结论
- ❌ 一个 prompt 塞 5 个独立子任务（拆开并发更快、更准）
- ❌ "看看有什么问题"这种没检查清单的开放式 prompt（产出全是水）
- ❌ 让 sub-CLI 决定"是否要重做" — 验收权一定在主 agent
- ❌ 跨子任务共享数据（sub-CLI 互不通信，要共享就放在主 agent 做）
- ❌ 跑完任务**不出 token 报告** — 没数据下次没法复盘选型

## 工具完整 flag 速查

### kimi-cli
- `--print` 非交互（必带）
- `--yolo` / `-y` 自动批准
- `--quiet` 只打印最终消息（推荐组合 `--print --yolo --quiet`）
- `-w <dir>` workdir
- `-p "<text>"` prompt（也可以 stdin pipe）
- `-m <model>` 切模型
- `--final-message-only` 与 `--quiet` 等价
- session 数据：`~/.kimi/sessions/<hash>/<sid>/wire.jsonl`

### codex exec
- `exec` 子命令本身就是非交互
- `--dangerously-bypass-approvals-and-sandbox` 自动批准（只对只读任务）
- `-C <dir>` workdir
- `--skip-git-repo-check` 当工作目录不在 git 仓库时
- `-o <file>` 最终消息写到文件
- `--json` 事件流 JSONL（高级用法，做结构化收割时用）
- 位置参数 / stdin 传 prompt
- session 数据：`~/.codex/sessions/<year>/<month>/<day>/rollout-*.jsonl`

两者都通过环境变量 `HTTP_PROXY/HTTPS_PROXY` 走代理（codex 通常已 alias 好）。
