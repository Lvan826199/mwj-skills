#!/usr/bin/env python3
"""token_report.py — Compute token usage for delegate-to-cli sessions.

Parses kimi-cli session files (~/.kimi/sessions/<hash>/<sid>/wire.jsonl) and
codex stdout logs to produce a markdown token report. Estimates how much
the main Claude agent saved by delegating, vs running everything itself.

Usage:
    python3 token_report.py \\
        --kimi A:<sid_a> B:<sid_b> ... \\
        --codex A:<log_a> B:<log_b> ... \\
        [--claude-overhead 50000] \\
        [--out report.md]

Examples:
    # After delegating 4 kimi tasks, you have session ids in stderr logs.
    python3 token_report.py \\
        --kimi A:831f3862-... B:50ea52ab-... \\
        --codex A:/tmp/codex/log_A.txt B:/tmp/codex/log_B.txt \\
        --out /tmp/token_report.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

KIMI_SESSIONS_ROOT = Path.home() / ".kimi" / "sessions"


def parse_kimi_session(session_id: str) -> dict[str, Any]:
    if not KIMI_SESSIONS_ROOT.exists():
        return {"error": f"~/.kimi/sessions does not exist"}

    session_dir = None
    for hash_dir in KIMI_SESSIONS_ROOT.iterdir():
        candidate = hash_dir / session_id
        if candidate.is_dir():
            session_dir = candidate
            break
    if not session_dir:
        return {"error": f"session {session_id} not found under ~/.kimi/sessions/"}

    wire = session_dir / "wire.jsonl"
    if not wire.exists():
        return {"error": f"no wire.jsonl in {session_dir}"}

    totals = {
        "input_other": 0,
        "input_cache_read": 0,
        "input_cache_creation": 0,
        "output": 0,
        "events": 0,
    }
    with wire.open() as fh:
        for line in fh:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            payload = (obj.get("message") or {}).get("payload") or {}
            tu = payload.get("token_usage")
            if not isinstance(tu, dict):
                continue
            for k in ("input_other", "input_cache_read", "input_cache_creation", "output"):
                totals[k] += int(tu.get(k) or 0)
            totals["events"] += 1

    totals["sum_input"] = (
        totals["input_other"] + totals["input_cache_read"] + totals["input_cache_creation"]
    )
    totals["grand"] = totals["sum_input"] + totals["output"]
    totals["session_id"] = session_id
    return totals


def parse_codex_log(log_path: str) -> dict[str, Any]:
    p = Path(log_path)
    if not p.exists():
        return {"error": f"log not found: {log_path}"}
    text = p.read_text(errors="replace")
    m = re.search(r"tokens used\s*\n\s*([\d,]+)", text)
    if not m:
        return {"error": "no `tokens used` marker found in codex log"}
    return {"grand": int(m.group(1).replace(",", "")), "log_path": str(p)}


def parse_claude_json(json_path: str) -> dict[str, Any]:
    """Parse `claude -p --output-format json` output (Mode 6)."""
    p = Path(json_path)
    if not p.exists():
        return {"error": f"json not found: {json_path}"}
    try:
        obj = json.loads(p.read_text(errors="replace"))
    except Exception as exc:
        return {"error": f"invalid json in {json_path}: {exc}"}
    usage = obj.get("usage")
    if not isinstance(usage, dict):
        return {"error": f"no `usage` field in {json_path}"}
    totals: dict[str, Any] = {
        "input_other": int(usage.get("input_tokens") or 0),
        "input_cache_read": int(usage.get("cache_read_input_tokens") or 0),
        "input_cache_creation": int(usage.get("cache_creation_input_tokens") or 0),
        "output": int(usage.get("output_tokens") or 0),
    }
    totals["sum_input"] = (
        totals["input_other"] + totals["input_cache_read"] + totals["input_cache_creation"]
    )
    totals["grand"] = totals["sum_input"] + totals["output"]
    totals["cost_usd"] = obj.get("total_cost_usd")
    return totals


def render_report(
    kimi_results: dict[str, dict],
    codex_results: dict[str, dict],
    claude_results: dict[str, dict],
    claude_overhead: int,
) -> str:
    lines: list[str] = ["# Token Usage Report", ""]

    kimi_total = 0
    if kimi_results:
        lines.append("## kimi-cli sessions")
        lines.append("")
        lines.append("| 任务 | session | input_other | cache_read | output | grand |")
        lines.append("|---|---|---:|---:|---:|---:|")
        for label, r in kimi_results.items():
            if "error" in r:
                lines.append(f"| {label} | ERROR | — | — | — | _{r['error']}_ |")
                continue
            kimi_total += r["grand"]
            lines.append(
                f"| {label} | `{r['session_id'][:8]}…` "
                f"| {r['input_other']:,} | {r['input_cache_read']:,} "
                f"| {r['output']:,} | **{r['grand']:,}** |"
            )
        lines.append(f"| **小计** | | | | | **{kimi_total:,}** |")
        lines.append("")

    codex_total = 0
    if codex_results:
        lines.append("## codex sessions")
        lines.append("")
        lines.append("| 任务 | tokens used |")
        lines.append("|---|---:|")
        for label, r in codex_results.items():
            if "error" in r:
                lines.append(f"| {label} | _{r['error']}_ |")
                continue
            codex_total += r["grand"]
            lines.append(f"| {label} | {r['grand']:,} |")
        lines.append(f"| **小计** | **{codex_total:,}** |")
        lines.append("")

    claude_total = 0
    if claude_results:
        lines.append("## claude sessions（Mode 6）")
        lines.append("")
        lines.append("| 任务 | input | cache_read | output | grand | cost(USD) |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for label, r in claude_results.items():
            if "error" in r:
                lines.append(f"| {label} | — | — | — | _{r['error']}_ | — |")
                continue
            claude_total += r["grand"]
            cost = f"{r['cost_usd']:.4f}" if isinstance(r.get("cost_usd"), (int, float)) else "—"
            lines.append(
                f"| {label} | {r['input_other']:,} | {r['input_cache_read']:,} "
                f"| {r['output']:,} | **{r['grand']:,}** | {cost} |"
            )
        lines.append(f"| **小计** | | | | **{claude_total:,}** | |")
        lines.append("")

    delegated = kimi_total + codex_total + claude_total
    coordinated_actual = delegated + claude_overhead

    lines.extend(
        [
            "## 估算节省",
            "",
            "> 该节省比例为粗略估算。Claude 主会话的真实 token 无法从外部精确测算（系统提示、工具 schema、tool_use/tool_result 反复传入，受 prompt cache 影响）。下方采用保守模型。",
            "",
            f"- 派给 sub-CLI 实际消耗：**{delegated:,}** token",
            f"- Claude 主 agent 协调开销（写 prompt + 读 sub-CLI 报告 + 综合，估算）：**{claude_overhead:,}** token",
            f"- 委派模式总成本（估算）：**{coordinated_actual:,}** token",
            "",
        ]
    )

    if delegated > 0:
        # 保守模型：Claude 单跑要做相同量的 grep/read，token ≈ delegated
        # 上限模型：Claude 主上下文累积，相比 sub-CLI 多 N×overhead 的反复传入
        n_tasks = sum(
            1
            for r in (
                list(kimi_results.values())
                + list(codex_results.values())
                + list(claude_results.values())
            )
            if "error" not in r
        )
        solo_lower = delegated
        solo_upper = delegated + claude_overhead * max(1, n_tasks)

        # 总节省（含 sub-CLI 计费成本）
        total_savings_lo = (solo_lower - coordinated_actual) / solo_lower * 100 if solo_lower else 0
        total_savings_hi = (solo_upper - coordinated_actual) / solo_upper * 100 if solo_upper else 0

        # 主 agent 节省（最重要的指标 — 你最关心的"主会话上下文压力"）
        # 单跑：Claude 主 agent 自己消耗 solo_lower / solo_upper
        # 委派：Claude 主 agent 仅消耗 claude_overhead，其余转嫁 sub-CLI
        main_savings_lo = (solo_lower - claude_overhead) / solo_lower * 100 if solo_lower else 0
        main_savings_hi = (solo_upper - claude_overhead) / solo_upper * 100 if solo_upper else 0

        lines.extend(
            [
                f"- 完全由 Claude 主 agent 单跑预估：**{solo_lower:,}** ~ **{solo_upper:,}** token",
                f"  - 下限：假设 Claude 自跑等量 grep/read，token ≈ 委派总量",
                f"  - 上限：Claude 上下文累积，{n_tasks} 个子任务每个都把前面任务的上下文带进来",
                "",
                "### 两种节省口径",
                "",
                "| 指标 | 含义 | 节省比例 |",
                "|---|---|---:|",
                f"| **总 token 节省** | (单跑预估 − 委派模式总成本) ÷ 单跑预估，含 sub-CLI 计费 | **{total_savings_lo:+.1f}% ~ {total_savings_hi:+.1f}%** |",
                f"| **主 agent 节省** | (单跑预估 − 主 agent 协调开销) ÷ 单跑预估，**只看主会话承担的 token** | **{main_savings_lo:+.1f}% ~ {main_savings_hi:+.1f}%** |",
                "",
                "### 解读",
                "- **总 token 节省**通常很小或为负 — 因为子任务的 token 仍然由 sub-CLI 消耗，全局工作量没减。",
                "- **主 agent 节省**才是你真正关心的：主会话只承担『写 prompt + 读报告 + 综合』，重活全转嫁给 sub-CLI。比例越高，主上下文越干净、context window 越扛得住、长会话越能持续。",
                "- kimi 的 cache_read 比例（典型 80%+）说明跨子任务的系统提示命中缓存，sub-CLI 这部分按计费可能折扣，间接也降低**总成本**。",
                "",
            ]
        )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a token usage report for delegate-to-cli sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--kimi",
        nargs="*",
        default=[],
        metavar="LABEL:SID",
        help="kimi session entries, e.g. A:831f3862-... B:50ea52ab-...",
    )
    parser.add_argument(
        "--codex",
        nargs="*",
        default=[],
        metavar="LABEL:LOG_PATH",
        help="codex log entries, e.g. A:/tmp/log_A.txt",
    )
    parser.add_argument(
        "--claude",
        nargs="*",
        default=[],
        metavar="LABEL:JSON_PATH",
        help="claude -p --output-format json entries, e.g. A:/tmp/out_A.json",
    )
    parser.add_argument(
        "--claude-overhead",
        type=int,
        default=50000,
        help="estimated main Claude agent overhead in tokens (default: 50000)",
    )
    parser.add_argument("--out", help="write report to file (default: stdout)")
    args = parser.parse_args()

    if not args.kimi and not args.codex and not args.claude:
        parser.error("at least one of --kimi, --codex or --claude required")

    kimi_results = {}
    for spec in args.kimi:
        label, sep, sid = spec.partition(":")
        if not sep:
            print(f"skipping malformed --kimi entry: {spec!r}", file=sys.stderr)
            continue
        kimi_results[label] = parse_kimi_session(sid)

    codex_results = {}
    for spec in args.codex:
        label, sep, log = spec.partition(":")
        if not sep:
            print(f"skipping malformed --codex entry: {spec!r}", file=sys.stderr)
            continue
        codex_results[label] = parse_codex_log(log)

    claude_results = {}
    for spec in args.claude:
        label, sep, json_path = spec.partition(":")
        if not sep:
            print(f"skipping malformed --claude entry: {spec!r}", file=sys.stderr)
            continue
        claude_results[label] = parse_claude_json(json_path)

    report = render_report(
        kimi_results, codex_results, claude_results, args.claude_overhead
    )

    if args.out:
        Path(args.out).write_text(report)
        print(f"Wrote {args.out} ({len(report)} chars)")
    else:
        print(report)


if __name__ == "__main__":
    main()
