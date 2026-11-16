"""scripts/sync_skills.py 的保留清单行为测试，一律走 main(argv) 真实入口。"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "sync_skills.py"
KEEP = {"Kept/.claude/skills/demo": "测试用定制"}


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("sync_skills", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["sync_skills"] = module
    spec.loader.exec_module(module)
    return module


class Env:
    """本仓库一个 skill（新版），Kept、Plain 两个项目各有一份旧副本。"""

    def __init__(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self.sync = load_module()
        repo = tmp_path / "repo"
        source = repo / "skills" / "demo"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("新版\n", encoding="utf-8")
        self.projects = tmp_path / "projects"
        for name in ("Kept", "Plain"):
            copy = self.projects / name / ".claude" / "skills" / "demo"
            copy.mkdir(parents=True)
            (copy / "SKILL.md").write_text("项目定制\n", encoding="utf-8")
        self.keep_file = tmp_path / "sync_keep.json"
        monkeypatch.setattr(self.sync, "REPO_ROOT", repo)
        monkeypatch.setattr(self.sync, "SOURCE_DIR", repo / "skills")
        monkeypatch.setattr(self.sync, "KEEP_FILE", self.keep_file)

    def write_keep(self, keep: dict[str, str]) -> None:
        self.keep_file.write_text(json.dumps(keep, ensure_ascii=False), "utf-8")

    def run(self, *argv: str) -> int:
        code: int = self.sync.main([*argv, "--projects-root", str(self.projects)])
        return code

    def read(self, name: str) -> str:
        path = self.projects / name / ".claude" / "skills" / "demo" / "SKILL.md"
        return path.read_text(encoding="utf-8")


@pytest.fixture()
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Env:
    return Env(tmp_path, monkeypatch)


def test_push_skips_kept_copy(env: Env) -> None:
    env.write_keep(KEEP)
    assert env.run("push-projects", "--apply") == 0
    assert env.read("Kept") == "项目定制\n"
    assert env.read("Plain") == "新版\n"


def test_push_skips_kept_copy_even_with_only(env: Env) -> None:
    env.write_keep(KEEP)
    env.run("push-projects", "--apply", "--only", "demo")
    assert env.read("Kept") == "项目定制\n"


def test_push_without_keep_file_updates_all(env: Env) -> None:
    assert env.run("push-projects", "--apply") == 0
    assert env.read("Kept") == "新版\n"


def test_check_marks_keep_and_stale(
    env: Env, capsys: pytest.CaptureFixture[str]
) -> None:
    env.write_keep({**KEEP, "Gone/.claude/skills/demo": "已删除的项目"})
    assert env.run("check") == 0
    out = capsys.readouterr().out
    assert "KEEP  Kept/.claude/skills/demo 改动 1（测试用定制）" in out
    assert "DIFF  Plain/.claude/skills/demo 改动 1" in out
    assert "!! 保留清单里的 Gone/.claude/skills/demo 不存在" in out


@pytest.mark.parametrize("content", ['["不是对象"]', "{坏 JSON", '{"a": 1}'])
def test_bad_keep_file_stops_before_writing(
    env: Env, capsys: pytest.CaptureFixture[str], content: str
) -> None:
    env.keep_file.write_text(content, encoding="utf-8")
    assert env.run("push-projects", "--apply") == 2
    assert "保留清单读不了" in capsys.readouterr().err
    assert env.read("Plain") == "项目定制\n"
