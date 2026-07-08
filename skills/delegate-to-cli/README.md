# delegate-to-cli

A Claude Code Skill for **delegating read-heavy, independently-verifiable subtasks** to local CLI agents (`kimi-cli` or `codex exec`), running them in parallel, then rigorously verifying the results in the main session.

> Use this when the main agent shouldn't blow its context window doing 4 parallel grep-heavy audits by itself.

## What it does

- **Splits** a large task (audit, inspection, multi-doc reconciliation) into 2+ independent subtasks
- **Dispatches** each subtask to `kimi-cli` or `codex exec` in parallel via background bash
- **Verifies** sub-CLI outputs through a 4-step gate (completeness → format → spot-check claims → consistency)
- **Retries** unsatisfactory subtasks up to 3 times (with appended feedback), then falls back to the main agent
- **Reports** per-agent token usage and estimates how much main-agent token bandwidth was saved

## 5 execution modes

| Mode | When to use |
|---|---|
| **1. kimi-only** | Chinese long-doc audit; cross-doc reconciliation; trust kimi enough to skip review |
| **2. codex-only** | Precise code semantics (line numbers, call graphs, function signatures) |
| **3. kimi first → codex cross-check** | High-stakes audits; want fast first pass + rigorous second pass (recommended) |
| **4. kimi + codex parallel → main agent synthesizes** | Want both views simultaneously; main agent reconciles disagreements |
| **5. After sub-agents finish → main agent final verification + token report** | Add this on top of any other mode for closing rigor + saved-token measurement |

## Files

```
delegate-to-cli/
├── SKILL.md              # The skill itself (Claude Code reads frontmatter to decide when to invoke)
├── token_report.py       # Parse kimi/codex session data → markdown token report
└── README.md             # This file
```

## Install

Copy the `delegate-to-cli/` directory into your Claude Code skills directory:

```bash
# For user-level skills:
cp -r delegate-to-cli ~/.claude/skills/

# Or project-level:
cp -r delegate-to-cli /path/to/your/project/.claude/skills/
```

Claude Code auto-discovers skills on session start. Triggers when the user mentions things like:
- "派 kimi/codex 干"
- "指挥 sub-agent"
- "分发任务"
- "整体巡检 / 审计 / 对账"
- "再用 codex/kimi 复审一遍"
- "delegate to kimi/codex"
- ...or whenever main task can be split into 2+ independent read-heavy subtasks.

## Prerequisites

You need at least one of these CLIs installed and authenticated:

### kimi-cli

Install per the [official docs](https://moonshotai.github.io/kimi-cli/). Test:

```bash
kimi-cli --print --yolo --quiet -p "say hello in one word"
```

The skill uses `--print --yolo --quiet` for non-interactive, auto-approve, final-message-only mode.

### codex exec

Install per OpenAI Codex CLI docs. Test:

```bash
echo "say hello in one word" | codex exec \
  --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  -
```

The skill uses `exec`, `--dangerously-bypass-approvals-and-sandbox`, and `-o <file>` to capture the final message.

## How the token report works

After a delegation run, the skill calls `token_report.py` to produce a markdown report. Example invocation:

```bash
python3 ~/.claude/skills/delegate-to-cli/token_report.py \
  --kimi A:<session_id_A> B:<session_id_B> \
  --codex A:/tmp/<session>/log_A.txt B:/tmp/<session>/log_B.txt \
  --claude-overhead 70000 \
  --out /tmp/<session>/token_report.md
```

Output (example, real numbers from one inspection run):

```
| 任务 | tokens used |
|---|---:|
| S1 | 134,990 |
| S2 |  99,674 |
| S3 |  96,532 |
| S4 | 107,476 |
| 小计 | 438,672 |

| 指标 | 节省比例 |
|---|---:|
| 总 token 节省      | -16.0% ~ +29.2% |
| 主 agent 节省      | +84.0% ~ +90.3% |
```

### Two savings metrics, explained

- **Total token savings** (often near 0 or negative): Sub-CLIs still burn tokens — they're just transferred from the main agent. The repository content has to be read by *someone*.
- **Main agent savings** (usually 90%+): The main session only carries "write prompt + read report + synthesize" overhead. Heavy grep/read is offloaded. This is the real prize: main context window stays clean, long conversations remain viable.

### Where the data comes from

- **kimi**: `~/.kimi/sessions/<hash>/<session-id>/wire.jsonl` contains a `token_usage` field per turn with `input_other`, `input_cache_read`, `input_cache_creation`, `output`. The skill grabs the session ID from kimi's stderr (`To resume this session: kimi -r <SID>`).
- **codex**: stdout contains a `tokens used\n<number>` block; `token_report.py` regex-parses it.

## Skill design philosophy

1. **Sub-CLIs do read-heavy work; the main agent reserves judgment.** Never let a sub-CLI write code, modify files, or make final calls.
2. **Trust but spot-check.** Every claimed file:line citation gets verified by the main agent (4-6 deep checks per run). If a sub-CLI fakes a citation once, you can't trust the rest.
3. **One prompt per subtask, narrow and structured.** "Look for bugs" produces vague slop. "For these 8 modules, give PASS/FAIL + file:line for these 5 specific checkpoints" produces usable data.
4. **Retry with appended feedback, not replacement.** When a sub-CLI fails, append "you missed X, line N is wrong" to the same prompt and retry. Up to 3 times.
5. **Always emit a token report.** Without data, you can't improve the next run's mode/CLI choice.

## What this skill is NOT for

- Writing or modifying code — main agent should do that
- Tasks that need main-session context — sub-CLIs start fresh
- Tasks with dependencies between subtasks — sub-CLIs don't share state
- Operations with side effects (git push, deployments, sending messages) — main agent retains approval authority
- Single-file or trivial tasks — overhead isn't worth it

## Real-world numbers

From an actual full-project audit (Phase progress + code review + library health + reconciliation, 4 subtasks via codex):

- **Sub-CLI tokens consumed**: 438,672
- **Main agent coordination overhead** (estimated): 70,000
- **Total delegated cost**: 508,672
- **Main agent savings**: **+84% to +90%**
- **Spot-check accuracy of sub-CLI claims**: **7/7 confirmed**
- **Wall-clock time**: ~3 minutes (4 codex calls in parallel)

The same audit run inside the main session alone would have likely consumed 500k–700k main-agent tokens, polluted the context with grep output, and pushed close to context limits.

## License

Personal skill. Share freely. No warranty.

## Credits

Built iteratively across several Claude Code sessions doing large multi-file audits and reviews. The 5-mode design and dual-metric token reporting emerged from real failure cases (e.g., trusting a kimi audit that turned out to have 4 errors in 18 claims — fixed by adding Mode 3 cross-check).
