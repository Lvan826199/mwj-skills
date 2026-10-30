"""架构测试模板：用 AST 静态扫描守住分层依赖方向（mwj-architecture skill）。

复制到项目的 tests/test_architecture.py，改 PACKAGE_ROOT 和 FORBIDDEN 即可。

为什么用 AST 而不是 import 后看 sys.modules：后者会把传递依赖也算进来，
误报一片。TYPE_CHECKING 块内的 import 只用于类型标注，不算运行期依赖。

豁免必须写原因、只许减不许增：ALLOWED 里每条都要有一句话说明为什么暂时允许。
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# 项目在 pytest 配置里注册了 unit 标记时保留；没注册会有警告（--strict-markers 下报错）
pytestmark = pytest.mark.unit

# 被守护的顶层包目录（模块名由目录推出）
PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "src" / "mypkg"

# 键：某一层；值：这一层运行期不得 import 的模块（前缀匹配，可以是包外三方库）
FORBIDDEN: dict[str, tuple[str, ...]] = {
    "mypkg.domain": ("mypkg.application", "mypkg.infrastructure", "mypkg.api"),
    "mypkg.application": ("mypkg.infrastructure", "mypkg.api"),
    "mypkg.infrastructure": ("mypkg.api",),
}

# 已知违规的临时豁免：{("模块", "被禁的层"): "原因"}，只许减不许增
ALLOWED: dict[tuple[str, str], str] = {}


def module_name(path: Path) -> str:
    rel = path.relative_to(PACKAGE_ROOT.parent).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _is_type_checking(node: ast.If) -> bool:
    test = node.test
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def runtime_imports(path: Path) -> set[str]:
    """收集运行期 import 的完整模块名（展开相对导入与 from x import y）。

    全树遍历（函数、try、with、match 分支里的 import 都算），只跳过
    TYPE_CHECKING 块。
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    current = module_name(path)
    package = current if path.name == "__init__.py" else current.rpartition(".")[0]

    type_only: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _is_type_checking(node):
            for stmt in node.body:  # else 分支仍是运行期，不跳过
                type_only.update(id(n) for n in ast.walk(stmt))

    found: set[str] = set()
    for node in ast.walk(tree):
        if id(node) in type_only:
            continue
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                anchor = package.split(".")
                anchor = anchor[: len(anchor) - (node.level - 1)]
                base = ".".join([*anchor, base] if base else anchor)
            # from pkg import sub 可能是子模块，两种都记下，前缀匹配时不漏
            found.add(base)
            found.update(f"{base}.{alias.name}" for alias in node.names)
    # 不过滤包外 import：FORBIDDEN 里也可以禁三方库（如 core 不得 import webview）
    return found


def _matches(name: str, prefix: str) -> bool:
    return name == prefix or name.startswith(prefix + ".")


def find_violations() -> list[tuple[str, str]]:
    violations: list[tuple[str, str]] = []
    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        current = module_name(path)
        for layer, banned in FORBIDDEN.items():
            if not _matches(current, layer):
                continue
            imported = runtime_imports(path)
            # 按「模块 → 被禁的层」记一次：from x import y 不会重复报两条
            for prefix in banned:
                if any(_matches(name, prefix) for name in imported):
                    violations.append((current, prefix))
    return violations


def test_layer_dependencies_point_inward() -> None:
    violations = [v for v in find_violations() if v not in ALLOWED]
    assert not violations, "违反分层依赖方向：\n" + "\n".join(
        f"  {src} → {dst}" for src, dst in violations
    )


def test_allowed_list_has_no_stale_entries() -> None:
    """豁免修好后要删掉，否则豁免名单只会越积越多。"""
    stale = set(ALLOWED) - set(find_violations())
    assert not stale, f"这些豁免已经不再违规，请从 ALLOWED 删除：{sorted(stale)}"
