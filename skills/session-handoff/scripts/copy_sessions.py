"""把 Claude Code 会话从一个项目桶复制到另一个项目桶，并逐文件校验。

只复制、不删除：删除原处必须等用户明确授权后手动做（session-handoff skill
B 节第 7 步）。正在进行中的会话 jsonl 还在追加写入，复制后校验可能不一致，
这类会话等它结束后再复制。目标里已有同名文件且内容不同时直接报错，不覆盖。

用法：

    python copy_sessions.py --src-dir /home/work2 --dst-dir /home/work2/MyProject/Foo \
        --session 4947004c-6da8-42bc-8ab3-3139a9d7a2d2 --dry-run
    python copy_sessions.py --src-bucket ~/.claude/projects/-home-work2 \
        --dst-dir /home/work2/MyProject/Foo --all
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
from pathlib import Path

PROJECTS_ROOT = Path.home() / ".claude" / "projects"

# 会话 id 是 UUID；校验格式，防止 "../xx" 读到桶外文件
SESSION_ID_RE = re.compile(r"^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$")


def bucket_for(directory: str) -> Path:
    """按 Claude Code 的规则由工作目录推出项目桶：非字母数字字符都换成 '-'。

    规则依据本机已有的桶名观察得出（/ 和 . 都变成 -）；推出的桶不存在时
    调用方应提示用户先在目标目录启动一次 claude 再核对。
    """
    resolved = str(Path(directory).expanduser().resolve())
    return PROJECTS_ROOT / re.sub(r"[^A-Za-z0-9]", "-", resolved)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def session_files(bucket: Path, session_id: str) -> list[Path]:
    """一个会话 = <id>.jsonl + 同名附属目录（subagents、tool-results 等）。"""
    files: list[Path] = []
    jsonl = bucket / f"{session_id}.jsonl"
    if jsonl.exists():
        files.append(jsonl)
    side_dir = bucket / session_id
    if side_dir.is_dir():
        files += sorted(p for p in side_dir.rglob("*") if p.is_file())
    return files


def copy_session(src: Path, dst: Path, session_id: str, dry_run: bool) -> int:
    """复制并校验一个会话，返回出错文件数。"""
    files = session_files(src, session_id)
    if not files:
        print(f"!! 源桶里没有会话 {session_id}")
        return 1
    errors = 0
    for file in files:
        target = dst / file.relative_to(src)
        if target.exists():
            same = sha256(target) == sha256(file)
            print(f"{'== 已存在且一致' if same else '!! 已存在但内容不同'} {target}")
            errors += 0 if same else 1
            continue
        if dry_run:
            print(f"-> 将复制 {file} → {target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
        if sha256(target) != sha256(file):
            print(f"!! 校验失败 {target}")
            errors += 1
    if not dry_run and errors == 0:
        total = sum(f.stat().st_size for f in files)
        print(f"OK {session_id}: {len(files)} 个文件，{total} 字节，sha256 全部一致")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="复制 Claude Code 会话到另一个项目桶")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--src-dir", help="源工作目录（由它推出项目桶）")
    src.add_argument("--src-bucket", help="源项目桶路径")
    parser.add_argument("--dst-dir", required=True, help="目标工作目录")
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument("--session", action="append", help="会话 id，可重复")
    which.add_argument("--all", action="store_true", help="源桶里的全部会话")
    parser.add_argument("--dry-run", action="store_true", help="只列出将复制的文件")
    args = parser.parse_args(argv)

    src_bucket = (
        Path(args.src_bucket).expanduser()
        if args.src_bucket
        else bucket_for(args.src_dir)
    )
    dst_bucket = bucket_for(args.dst_dir)
    if not src_bucket.is_dir():
        print(f"!! 源桶不存在：{src_bucket}")
        return 1
    if not dst_bucket.is_dir():
        print(
            f"!! 目标桶不存在：{dst_bucket}\n   先在目标目录启动一次 claude，再核对桶名"
        )
        return 1

    ids = (
        sorted(p.stem for p in src_bucket.glob("*.jsonl")) if args.all else args.session
    )
    bad_ids = [sid for sid in ids if not SESSION_ID_RE.match(sid)]
    if bad_ids:
        print(f"!! 会话 id 不是 UUID 格式：{bad_ids}")
        return 1
    if src_bucket.resolve() == dst_bucket.resolve():
        print("!! 源桶和目标桶是同一个，无需复制")
        return 1
    print(f"源桶：{src_bucket}\n目标桶：{dst_bucket}\n会话：{len(ids)} 个")
    errors = sum(copy_session(src_bucket, dst_bucket, sid, args.dry_run) for sid in ids)
    print("完成，未删除任何原件。" if not errors else f"有 {errors} 个文件出错")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
