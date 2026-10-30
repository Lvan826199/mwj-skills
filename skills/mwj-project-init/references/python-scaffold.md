# Python 脚手架模板

`<name>` 是分发名（如 `mwj-foo`），`<pkg>` 是包名（如 `mwj_foo`），`<cmd>` 是命令名。

## pyproject.toml

```toml
[project]
name = "<name>"
version = "0.1.0"
description = "<一句话说明>"
readme = "README.md"
requires-python = ">=3.11,<3.14"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=5.0", "ruff>=0.6", "mypy>=1.10"]

[project.scripts]
<cmd> = "<pkg>.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/<pkg>"]

[[tool.uv.index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "W"]
# 中文标点（全角逗号、冒号等）在注释和文案里是正常的
ignore = ["RUF001", "RUF002", "RUF003"]

[tool.mypy]
strict = true
mypy_path = "src"
packages = ["<pkg>"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers -m 'not smoke'"
markers = [
    "unit: 纯单元测试，不依赖外部环境",
    "integration: 需要真实服务或数据库",
    "smoke: 真机或真模型冒烟，默认跳过",
]
```

> FastAPI 项目在 `[tool.ruff.lint.flake8-bugbear]` 里写 `extend-immutable-calls = ["fastapi.Depends", "fastapi.Query"]`，放行 B008。

## src/<pkg>/__init__.py

```python
"""<一句话说明>。"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("<name>")
except PackageNotFoundError:  # 源码未安装时（例如直接把 src 加进 PYTHONPATH）
    __version__ = "0.0.0"
```

## src/<pkg>/cli.py

```python
"""命令行入口。"""

from __future__ import annotations

import argparse

from <pkg> import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="<cmd>", description="<一句话说明>")
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## tests/test_version.py

```python
"""版本号只有一个来源：pyproject.toml。"""

import tomllib
from pathlib import Path

import pytest

import <pkg>

pytestmark = pytest.mark.unit


def test_version_matches_pyproject() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    expected = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]
    assert <pkg>.__version__ == expected
```

## tests/test_cli.py

```python
"""CLI 走真实入口 main(argv)。"""

import pytest

from <pkg> import __version__
from <pkg>.cli import main

pytestmark = pytest.mark.unit


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == __version__


def test_no_args_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "usage" in capsys.readouterr().out
```

## scripts/check.sh

```bash
#!/usr/bin/env bash
# 质量门禁的唯一入口（本地与 CI 共用），任一步失败即非零退出。
# 默认不改环境：只有加 --sync 才先执行 uv sync（审查类 skill 只跑只读部分）。
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "${1:-}" == "--sync" ]]; then
  echo "==> uv sync"
  uv sync --extra dev
fi

echo "==> ruff check";          uv run --no-sync ruff check src tests
echo "==> ruff format --check"; uv run --no-sync ruff format --check src tests
echo "==> mypy";                uv run --no-sync mypy
echo "==> pytest";              uv run --no-sync pytest
echo "✅ 全部门禁通过"
```

## FastAPI 服务类追加

`src/<pkg>/settings.py`：

```python
"""配置：环境变量统一用 <PREFIX>_ 前缀，.env.example 入库、.env 不入库。"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="<PREFIX>_", env_file=".env")

    host: str = "127.0.0.1"
    port: int = 8000
    log_dir: str = "logs"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

依赖增加：`fastapi`、`uvicorn[standard]`、`pydantic-settings`；测试增加：`httpx`（通过 ASGITransport 在进程内测试）。

`start.sh` 和 `start.ps1` 要成对出现、行为一致：检查 uv → `uv sync` → 没有 `.env` 时从 `.env.example` 复制一份 → 先检查端口是否被占用 → 启动；支持 `--stop`、`--restart`。`.bat` 文件只写 ASCII，开头加 `chcp 65001`。

## 打包类追加

Windows 桌面应用用 Nuitka standalone：`scripts/build_exe.ps1` 从 pyproject 读出版本号写进 exe 元数据，产物命名为 `<name>-vX.Y.Z-windows-x64.zip`，放在已经 gitignore 的 `dist/` 目录。发版流程写进 `docs/打包发布.md`，并配合 release-ship 使用。
