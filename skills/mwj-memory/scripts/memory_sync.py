"""AI 助手记忆：本机记忆桶 ⇄ 仓库镜像目录的三方同步与审计（mwj-memory skill）。

为什么是三方同步：只按「本机 → 仓库」或反向整份覆盖，会把另一边（例如
Codex 直接写进仓库的记忆）静默冲掉。这里用状态文件记住上次同步时每个文件的
哈希：只有一边改过 → 同步过去；两边都改过 → 报冲突，不覆盖；一边删了 →
只报告，加 --apply-deletes 才传播删除（曾经误删过记忆）。未处理的删除、冲突、
被拦截的文件，状态里保留上次的哈希，下次照样报出来，不会被当成新增「复活」。

本机桶按 Claude Code 规则由仓库路径正向编码得到（非字母数字字符都换成 '-'），
不做反向解码——反向解码遇到 mwj-skills 这种带连字符的路径会选错桶。

    python memory_sync.py check            # 只报告，有差异退出码 1（可给 CI 用）
    python memory_sync.py sync [--apply] [--prefer local|repo]
    python memory_sync.py audit [--target repo|local] [--stale-days 60]
    python memory_sync.py link [--apply]   # 把本机桶 memory/ 改成指向仓库目录的软链
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

PROJECTS_ROOT = Path.home() / ".claude" / "projects"
INDEX = "MEMORY.md"
STATE_FILE = ".memory-sync-state.json"
LOCK_FILE = ".memory-sync.lock"
SYNC_SUFFIX = ".md"
# 只留在仓库侧的说明文件，不参与同步
REPO_ONLY = {"README.md"}
VALID_TYPES = {"user", "feedback", "project", "reference"}

# 进仓库前拦截。宁可少量误报也不能漏：误报时改写成「凭据在哪」的指针说法即可
_POINTER = r"(?!\s*(?:见|在|放在|存于|参见|see\b))"
SENSITIVE_PATTERNS = [
    (
        # 必须是完整 4 段，前后不能紧挨数字或点，避免把版本号 10.15.7 当成 IP
        re.compile(
            r"(?<![\d.])(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}"
            r"|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(?![\d.])"
        ),
        "内网 IP",
    ),
    (
        re.compile(
            r"(?i)(?:password|passwd|口令|密码)\s*[:=：]" + _POINTER + r"\s*\S+"
        ),
        "口令",
    ),
    (
        re.compile(
            r"(?i)(?:api[_-]?key|secret|token)\s*[:=：]" + _POINTER + r"\s*['\"]?"
            r"[\w\-]{12,}"
        ),
        "密钥",
    ),
    (
        re.compile(
            r"\b(?:sk-[\w-]{16,}|ghp_\w{20,}|github_pat_\w{20,}"
            r"|AKIA[0-9A-Z]{16}|xox[abpr]-[\w-]{10,})"
        ),
        "API key",
    ),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "私钥"),
]


def bucket_for(repo: Path) -> Path:
    """仓库路径 → 本机记忆桶目录（正向编码）。"""
    encoded = re.sub(r"[^A-Za-z0-9]", "-", str(repo.resolve()))
    return PROJECTS_ROOT / encoded / "memory"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def memory_files(directory: Path) -> dict[str, str]:
    """{文件名: 哈希}，只看第一层的 .md。"""
    if not directory.is_dir():
        return {}
    return {
        p.name: digest(p)
        for p in sorted(directory.iterdir())
        if p.is_file() and p.suffix == SYNC_SUFFIX and p.name not in REPO_ONLY
    }


def find_sensitive(text: str) -> list[str]:
    return [label for pattern, label in SENSITIVE_PATTERNS if pattern.search(text)]


@dataclass
class Plan:
    """一次同步要做的事。"""

    to_repo: list[str] = field(default_factory=list)
    to_local: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    deleted_local: list[str] = field(default_factory=list)  # 本机删了，仓库还在
    deleted_repo: list[str] = field(default_factory=list)  # 仓库删了，本机还在
    blocked: dict[str, list[str]] = field(default_factory=dict)  # 敏感信息拦截
    index_merge: bool = False  # MEMORY.md 两边都改了，需要按行合并

    @property
    def pending(self) -> list[str]:
        """本轮不会处理、下轮还要再报的文件。"""
        return [
            *self.conflicts,
            *self.deleted_local,
            *self.deleted_repo,
            *self.blocked,
        ]

    @property
    def clean(self) -> bool:
        return not (self.to_repo or self.to_local or self.pending or self.index_merge)


def make_plan(local: Path, repo: Path, state: dict[str, str], prefer: str) -> Plan:
    """三方比较：本机、仓库、上次同步时的哈希。"""
    lf, rf = memory_files(local), memory_files(repo)
    plan = Plan()
    for name in sorted(set(lf) | set(rf) | set(state)):
        lh, rh, base = lf.get(name), rf.get(name), state.get(name)
        if lh == rh:
            continue
        if lh and rh:
            if base == rh:
                plan.to_repo.append(name)  # 只有本机改了
            elif base == lh:
                plan.to_local.append(name)  # 只有仓库改了
            elif name == INDEX:
                plan.index_merge = True
            elif prefer == "local":
                plan.to_repo.append(name)
            elif prefer == "repo":
                plan.to_local.append(name)
            else:
                plan.conflicts.append(name)  # 两边都改了（或首次同步且不同）
        elif lh and not rh:
            # 仓库没有：上次同步时有 → 仓库删了；否则是本机新增
            (plan.deleted_repo if base else plan.to_repo).append(name)
        elif rh and not lh:
            (plan.deleted_local if base else plan.to_local).append(name)
    for name in plan.to_repo:
        hits = find_sensitive((local / name).read_text(encoding="utf-8"))
        if hits:
            plan.blocked[name] = hits
    plan.to_repo = [n for n in plan.to_repo if n not in plan.blocked]
    return plan


def merge_index(local_text: str, repo_text: str) -> str:
    """MEMORY.md 按行取并集：本机的行在前，再追加仓库独有的行。

    并集不会丢条目，但删掉的行会被另一边带回来、改过的行会两版都在——
    合并后要人工看一眼索引。
    """
    lines = local_text.rstrip("\n").splitlines()
    seen = set(lines)
    lines += [line for line in repo_text.splitlines() if line not in seen]
    return "\n".join(lines) + "\n"


def print_plan(plan: Plan) -> None:
    groups = [
        ("本机 → 仓库", plan.to_repo),
        ("仓库 → 本机", plan.to_local),
        ("冲突（两边都改了，不覆盖；可用 --prefer 指定以哪边为准）", plan.conflicts),
        ("本机已删、仓库还在（加 --apply-deletes 才删仓库那份）", plan.deleted_local),
        ("仓库已删、本机还在（加 --apply-deletes 才删本机那份）", plan.deleted_repo),
    ]
    if plan.index_merge:
        print(f"== {INDEX} 两边都改了：按行取并集合并，合并后请人工看一眼")
    for title, names in groups:
        if names:
            print(f"== {title}")
            for name in names:
                print(f"   {name}")
    if plan.blocked:
        print("== 含敏感信息，拒绝写进仓库（改写成「凭据在哪」的指针后重试）")
        for name, hits in plan.blocked.items():
            print(f"   {name}: {', '.join(hits)}")
    if plan.clean:
        print("两边一致。")


class Lock:
    """防止两个会话同时整理同一批记忆；持锁进程已退出时允许接管。"""

    def __init__(self, directory: Path) -> None:
        self.path = directory / LOCK_FILE

    def _holder_alive(self) -> bool:
        try:
            pid = int(self.path.read_text().strip())
            os.kill(pid, 0)
        except (ValueError, ProcessLookupError, FileNotFoundError):
            return False
        except PermissionError:
            return True  # 进程存在但属于别的用户
        return True

    def __enter__(self) -> Lock:
        if self.path.exists() and not self._holder_alive():
            print(f"== 锁文件残留（持锁进程已退出），接管：{self.path}")
            self.path.unlink()
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            sys.exit(f"!! 另一个同步正在进行（锁文件 {self.path}）")
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return self

    def __exit__(self, *_: object) -> None:
        self.path.unlink(missing_ok=True)


def load_state(local: Path) -> dict[str, str]:
    path = local / STATE_FILE
    if not path.exists():
        return {}
    data: dict[str, str] = json.loads(path.read_text(encoding="utf-8"))
    return data


def cmd_sync(
    local: Path, repo: Path, apply: bool, apply_deletes: bool, prefer: str
) -> int:
    state = load_state(local)
    plan = make_plan(local, repo, state, prefer)
    merged: str | None = None
    if plan.index_merge:
        merged = merge_index(
            (local / INDEX).read_text(encoding="utf-8"),
            (repo / INDEX).read_text(encoding="utf-8"),
        )
        hits = find_sensitive(merged)
        if hits:
            plan.blocked[INDEX] = hits
            plan.index_merge = False
            merged = None
    print_plan(plan)
    if not apply:
        if not plan.clean:
            print("（演练，未写入；加 --apply 执行）")
        return 0 if plan.clean else 1

    repo.mkdir(parents=True, exist_ok=True)
    for name in plan.to_repo:
        shutil.copy2(local / name, repo / name)
    for name in plan.to_local:
        shutil.copy2(repo / name, local / name)
    if merged is not None:
        for target in (local / INDEX, repo / INDEX):
            target.write_text(merged, encoding="utf-8")
    deletes_applied: set[str] = set()
    if apply_deletes:
        for name in plan.deleted_local:
            (repo / name).unlink()
            deletes_applied.add(name)
        for name in plan.deleted_repo:
            (local / name).unlink()
            deletes_applied.add(name)

    # 两边一致的记新哈希；本轮没处理的（冲突、未传播的删除、被拦截）保留旧哈希，
    # 下次照样报出来，而不是被误判成「新增」把删掉的文件拷回来
    lf, rf = memory_files(local), memory_files(repo)
    new_state = {n: h for n, h in lf.items() if rf.get(n) == h}
    for name in plan.pending:
        if name in state and name not in deletes_applied:
            new_state.setdefault(name, state[name])
    (local / STATE_FILE).write_text(
        json.dumps(new_state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("已同步。仓库侧的改动请自行审阅后提交（git add 具体文件）。")
    return 1 if (plan.conflicts or plan.blocked) else 0


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """取 name/description/type/updated/modified；兼容 type 在顶层或 metadata 下、
    行尾注释、CRLF。没有 frontmatter 返回 None。"""
    text = text.replace("\r\n", "\n")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.strip().partition(":")
        if sep and key in {"name", "description", "type", "updated", "modified"}:
            fields[key] = value.split(" #", 1)[0].strip().strip("'\"")
    return fields


def _age_days(meta: dict[str, str], path: Path) -> float:
    """优先用 frontmatter 的 updated/modified（克隆会刷新 mtime，不可靠）。"""
    for key in ("updated", "modified"):
        raw = meta.get(key, "")[:10]
        try:
            return (date.today() - date.fromisoformat(raw)).days
        except ValueError:
            continue
    return (time.time() - path.stat().st_mtime) / 86400


def _strip_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def cmd_audit(directory: Path, stale_days: int, repo_root: Path) -> int:
    problems: list[str] = []
    files = memory_files(directory)
    # 方案 C（repo-dir 就是仓库根目录）：根目录的普通文档不是记忆，只审带 frontmatter 的
    single_file_mode = directory.resolve() == repo_root.resolve()
    index_path = directory / INDEX
    index_text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    linked = set(re.findall(r"\]\(([^)]+\.md)\)", index_text))
    entries = 0
    for name in files:
        path = directory / name
        text = path.read_text(encoding="utf-8")
        for hit in find_sensitive(text):
            problems.append(f"{name}: 疑似含{hit}")
        if name == INDEX:
            continue
        meta = parse_frontmatter(text)
        if meta is None:
            if not single_file_mode:
                problems.append(f"{name}: 没有 frontmatter")
            continue
        entries += 1
        for key in ("name", "description", "type"):
            if not meta.get(key):
                problems.append(f"{name}: frontmatter 缺 {key}")
        if meta.get("type") and meta["type"] not in VALID_TYPES:
            problems.append(f"{name}: type={meta['type']} 不在 {sorted(VALID_TYPES)}")
        has_why = re.search(
            r"\*\*(Why|为什么)[:：]?\*\*|^(Why|为什么)[:：]", text, re.M
        )
        if meta.get("type") in {"feedback", "project"} and not has_why:
            problems.append(f"{name}: feedback/project 类缺 Why")
        if name not in linked:
            problems.append(f"{name}: 没有写进 {INDEX}")
        age = _age_days(meta, path)
        if meta.get("type") == "project" and age > stale_days:
            problems.append(f"{name}: project 类 {age:.0f} 天未更新，复核是否过期")
    for target in sorted(linked - set(files)):
        problems.append(f"{INDEX}: 指向不存在的 {target}")
    rules = " ".join(
        _strip_code((repo_root / f).read_text(encoding="utf-8"))
        for f in ("CLAUDE.md", "AGENTS.md")
        if (repo_root / f).exists()
    )
    if "MEMORY.md" in rules and not re.search(r"(^|\s)@\S*MEMORY\.md", rules, re.M):
        problems.append(
            "CLAUDE.md/AGENTS.md 只用文字提到 MEMORY.md，没有 @ 导入，实际不会加载"
        )
    for line in problems:
        print(f"- {line}")
    print(f"共 {entries} 条记忆，{len(problems)} 个问题")
    return 1 if problems else 0


def cmd_link(local: Path, repo: Path, apply: bool) -> int:
    plan = make_plan(local, repo, {}, prefer="")
    if plan.to_repo or plan.conflicts or plan.blocked:
        print("!! 本机桶有仓库里没有或不一致的记忆，先 sync 收齐再建软链：")
        print_plan(plan)
        return 1
    backup = local.with_name(f"memory.bak-{datetime.now():%Y%m%d-%H%M%S}")
    print(f"-> {local} 挪到 {backup}，改为软链指向 {repo}")
    if apply:
        if local.exists():
            shutil.move(str(local), str(backup))
        local.symlink_to(repo.resolve(), target_is_directory=True)
    else:
        print("（演练，未写入；加 --apply 执行）")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI 记忆三方同步与审计")
    parser.add_argument("command", choices=["check", "sync", "audit", "link"])
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="仓库根目录")
    parser.add_argument(
        "--repo-dir", default="docs/memory", help="仓库内记忆目录（相对仓库根）"
    )
    parser.add_argument("--memory-dir", type=Path, help="手动指定本机记忆桶目录")
    parser.add_argument("--apply", action="store_true", help="真正写入")
    parser.add_argument("--apply-deletes", action="store_true", help="传播删除")
    parser.add_argument(
        "--prefer",
        choices=["local", "repo"],
        default="",
        help="冲突时以哪边为准（首次同步常用）",
    )
    parser.add_argument("--stale-days", type=int, default=60)
    parser.add_argument(
        "--target", choices=["local", "repo"], default="repo", help="audit 审哪一边"
    )
    args = parser.parse_args(argv)

    repo_root = args.repo.resolve()
    repo_dir = repo_root / args.repo_dir
    local: Path = args.memory_dir or bucket_for(repo_root)
    print(f"本机桶：{local}\n仓库侧：{repo_dir}")

    if args.command == "audit":
        directory = repo_dir if args.target == "repo" else local
        return cmd_audit(directory, args.stale_days, repo_root)
    if not local.exists():
        print("!! 本机桶不存在：先在仓库目录启动一次 claude，或用 --memory-dir 指定")
        return 1
    if local.is_symlink():
        # 方案 B：本机桶就是仓库目录，不需要同步；指向别处说明配错了
        if local.resolve() == repo_dir.resolve():
            print("本机桶是指向仓库目录的软链（方案 B），无需同步；改为跑敏感扫描。")
            return cmd_audit(repo_dir, args.stale_days, repo_root)
        print(f"!! 本机桶软链指向 {local.resolve()}，不是 {repo_dir}，检查 --repo-dir")
        return 1
    if args.command == "link":
        return cmd_link(local, repo_dir, args.apply)
    if args.command == "check":
        return cmd_sync(local, repo_dir, False, False, args.prefer)
    with Lock(local):
        return cmd_sync(local, repo_dir, args.apply, args.apply_deletes, args.prefer)


if __name__ == "__main__":
    sys.exit(main())
