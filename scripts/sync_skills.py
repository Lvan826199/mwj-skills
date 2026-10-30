"""把本仓库的 skill 分发到用户级目录和各项目副本，并报告漂移。

本仓库 skills/ 是唯一来源：
- 用户级 ~/.claude/skills/<name>：软链到本仓库（与 dingtalk-* 的做法一致），
  改一处所有项目立即生效。
- 项目副本（<project>/.claude/skills/<name> 或 <project>/skills/<name>）：
  跟着项目仓库走、要在 Windows/其他机器上可用，所以用复制而不是软链；
  只更新已经存在的副本，不往项目里新增 skill。

默认只演练（打印将做什么），加 --apply 才写入。副本里有本仓库没有的
文件时不覆盖——那是要先收回本仓库的内容。

    python scripts/sync_skills.py check
    python scripts/sync_skills.py link-user [--apply]
    python scripts/sync_skills.py push-projects [--apply] [--only NAME ...]
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "skills"
USER_SKILLS = Path.home() / ".claude" / "skills"
# 被替换下来的旧目录挪到这里，不直接删除
USER_TRASH = USER_SKILLS / ".trash"
DEFAULT_PROJECTS_ROOT = REPO_ROOT.parent
PROJECT_SKILL_DIRS = (".claude/skills", "skills")
IGNORED_NAMES = {"__pycache__", ".DS_Store"}


@dataclass
class Drift:
    """一份副本相对本仓库的差异。"""

    changed: list[str] = field(default_factory=list)  # 两边都有但内容不同
    missing: list[str] = field(default_factory=list)  # 本仓库有、副本没有
    extra: list[str] = field(default_factory=list)  # 副本有、本仓库没有

    @property
    def same(self) -> bool:
        return not (self.changed or self.missing or self.extra)


def list_files(root: Path) -> set[str]:
    return {
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and not (IGNORED_NAMES & set(p.parts))
    }


def compare(source: Path, copy: Path) -> Drift:
    src_files, copy_files = list_files(source), list_files(copy)
    drift = Drift(
        missing=sorted(src_files - copy_files),
        extra=sorted(copy_files - src_files),
    )
    for rel in sorted(src_files & copy_files):
        if not filecmp.cmp(source / rel, copy / rel, shallow=False):
            drift.changed.append(rel)
    return drift


def source_skills() -> list[str]:
    return sorted(p.name for p in SOURCE_DIR.iterdir() if (p / "SKILL.md").is_file())


def project_copies(projects_root: Path) -> list[Path]:
    """找出各项目里所有 skill 目录（含只在项目里有的）。"""
    found: list[Path] = []
    for project in sorted(projects_root.iterdir()):
        if not project.is_dir() or project.resolve() == REPO_ROOT:
            continue
        for sub in PROJECT_SKILL_DIRS:
            base = project / sub
            if base.is_dir():
                found += sorted(
                    p for p in base.iterdir() if p.is_dir() and not p.is_symlink()
                )
    return found


def describe(drift: Drift) -> str:
    parts = []
    if drift.changed:
        parts.append(f"改动 {len(drift.changed)}")
    if drift.missing:
        parts.append(f"缺 {len(drift.missing)}")
    if drift.extra:
        parts.append(f"副本独有 {len(drift.extra)}: {', '.join(drift.extra[:3])}")
    return "；".join(parts)


def cmd_check(projects_root: Path) -> int:
    names = set(source_skills())
    print("== 用户级 ~/.claude/skills")
    for name in sorted(names):
        target = USER_SKILLS / name
        if target.is_symlink():
            ok = target.resolve() == (SOURCE_DIR / name).resolve()
            print(f"{'LINK ' if ok else 'LINK?'} {name} -> {target.readlink()}")
        elif target.is_dir():
            drift = compare(SOURCE_DIR / name, target)
            state = "SAME " if drift.same else "DIFF "
            print(f"{state} {name}（复制件）{describe(drift)}")
        else:
            print(f"MISS  {name}")
    print(f"\n== 项目副本（{projects_root}）")
    for copy in project_copies(projects_root):
        rel = copy.relative_to(projects_root)
        if copy.name not in names:
            print(f"ONLY  {rel}（本仓库没有，待评估是否收回）")
            continue
        drift = compare(SOURCE_DIR / copy.name, copy)
        print(f"{'SAME ' if drift.same else 'DIFF '} {rel} {describe(drift)}")
    return 0


def cmd_link_user(apply: bool) -> int:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for name in source_skills():
        source = SOURCE_DIR / name
        target = USER_SKILLS / name
        if target.is_symlink() and target.resolve() == source.resolve():
            continue
        if target.is_symlink():
            print(f"!! {name}: 已是指向别处的软链 {target.readlink()}，跳过")
            continue
        if target.exists():
            drift = compare(source, target)
            if drift.extra:
                print(f"!! {name}: 复制件有本仓库没有的文件，先收回：{drift.extra}")
                continue
            backup = USER_TRASH / f"{name}-{stamp}"
            print(f"-> {name}: 旧复制件挪到 {backup}，改为软链")
            if apply:
                USER_TRASH.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), str(backup))
        else:
            print(f"-> {name}: 新建软链")
        if apply:
            target.symlink_to(source, target_is_directory=True)
    print("已写入。" if apply else "（演练，未写入；加 --apply 执行）")
    return 0


def cmd_push_projects(projects_root: Path, apply: bool, only: list[str]) -> int:
    names = set(source_skills())
    blocked = 0
    for copy in project_copies(projects_root):
        if copy.name not in names or (only and copy.name not in only):
            continue
        rel = copy.relative_to(projects_root)
        drift = compare(SOURCE_DIR / copy.name, copy)
        if drift.same:
            continue
        if drift.extra:
            print(f"!! {rel}: 副本独有 {drift.extra}，不覆盖（先收回本仓库）")
            blocked += 1
            continue
        print(f"-> {rel}: 更新 {len(drift.changed)}、新增 {len(drift.missing)}")
        if apply:
            for item in drift.changed + drift.missing:
                (copy / item).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(SOURCE_DIR / copy.name / item, copy / item)
    print("已写入，请到各项目里自行审阅并提交。" if apply else "（演练，未写入）")
    return 1 if blocked else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="分发 skill 并报告漂移")
    parser.add_argument("command", choices=["check", "link-user", "push-projects"])
    parser.add_argument("--apply", action="store_true", help="真正写入")
    parser.add_argument("--only", nargs="*", default=[], help="只处理这些 skill")
    parser.add_argument(
        "--projects-root",
        type=Path,
        default=DEFAULT_PROJECTS_ROOT,
        help="项目根目录，默认是本仓库的上级目录",
    )
    args = parser.parse_args(argv)
    if args.command == "check":
        return cmd_check(args.projects_root)
    if args.command == "link-user":
        return cmd_link_user(args.apply)
    return cmd_push_projects(args.projects_root, args.apply, args.only)


if __name__ == "__main__":
    sys.exit(main())
