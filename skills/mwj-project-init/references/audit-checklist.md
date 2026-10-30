# 规范对齐审计清单

每项给出 ✅ / ❌ / —（不适用）；❌ 要附上证据（文件:行号，或命令输出）。只读检查，不改动。

## 1. AI 规则单源

- [ ] 只有一份完整的规则正文：AGENTS.md 为源（CLAUDE.md 只有 `@AGENTS.md`），或者 CLAUDE.md 为源（AGENTS.md 只是入口）。另一份不能复制规则正文。
  ```bash
  wc -l AGENTS.md CLAUDE.md; head -5 AGENTS.md CLAUDE.md
  ```
- [ ] 规则里的示例命令不和规则本身冲突，例如规则禁止 `git add .`，示例里却写了 `git add .`。
  ```bash
  grep -n "git add \.\|git add -A" AGENTS.md CLAUDE.md docs/*.md 2>/dev/null
  ```
  已知：AiTestProject/CLAUDE.md 约第 583 行、MSCA/CLAUDE.md 约第 506 行有 `git add .`（2026-10-30 审查发现）。
- [ ] AI 工具的本地目录已经写进 gitignore，并且没有被跟踪。
  ```bash
  git ls-files .claude .codex .agent .agents .Codex | head
  ```

## 2. 共享记忆

- [ ] 跨机器需要的记忆放在仓库里（`docs/memory/`、`docs/agent-memory/` 或根目录 `MEMORY.md`），并且有索引。
- [ ] 记忆里没有凭据、token、本机绝对路径。
  ```bash
  grep -rnE "password|passwd|token|api[_-]?key|/home/|[A-Z]:\\\\" docs/memory MEMORY.md 2>/dev/null | head
  ```

## 3. 文档套件

- [ ] 有 README（含快速开始）、CHANGELOG（含「未发布」段）。
- [ ] 有问题归因文档，并且最近的 fix 提交在里面都有对应条目。
  ```bash
  git log --oneline --since=60.days -- . | grep -c "^.\{8\} fix"
  ```
- [ ] 规则里有文档同步表，或者有明确的同步约定。
- [ ] 有打包的项目有发版文档（流程、版本号要改的位置、Windows 侧提示词）。

## 4. Python 工具链

- [ ] 用 uv，`uv.lock` 已入库；配了国内镜像。
- [ ] lint 配置存在（Ruff，或者沿用 Flake8 家族），`scripts/check.sh` 或 `make check` 是唯一的门禁入口。
- [ ] mypy 已配置（新项目要求 strict）。
- [ ] pytest 用了 `--strict-markers`，有 unit/integration/smoke 标记；真机和真模型测试默认跳过。
- [ ] 版本号只有一个来源：`__version__` 来自 `importlib.metadata`，或者有一致性测试守住。
  ```bash
  grep -rn "__version__ *=" src */__init__.py 2>/dev/null; ls tests/test_version.py 2>/dev/null
  ```
- [ ] 门禁当前是全绿的（只读运行，用 `.venv/bin/` 或 `uv run --no-sync`）。

## 5. 仓库卫生

- [ ] 二进制和产物没有入库。
  ```bash
  git ls-files | grep -iE "\.(exe|apk|zip|7z|dll|so|whl)$" | head
  ```
- [ ] `.env` 没有入库；`.env.example` 存在（服务类项目）。
- [ ] 运行时生成的文件（logs、.tmp、数据库）已写进 gitignore。
- [ ] 测试在当前平台上能跑通，或者已经标记 skip（例如 Windows 专用测试在 Linux 上要 skip）。

## 6. 本仓库 skill 副本

- [ ] 项目里的 skill 副本和 mwj-skills 一致。
  ```bash
  python <mwj-skills>/scripts/sync_skills.py check
  ```
  看本项目对应的那几行。
