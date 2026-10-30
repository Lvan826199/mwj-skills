---
name: mwj-python-style
description: 梦无矶的 Python 编码习惯，写代码时就遵守（不是等审查再改）：模块结构与命名、中文注释写「为什么」与实测出处、错误码异常体系与可行动报错、日志与脱敏、asyncio/subprocess/重试与超时、CLI 签名与退出码与 --json、打包路径与 Windows 兼容、数据安全底线、测试写法与反模式。在 Python 项目里新写或修改 .py 代码时触发；用户说「按我的风格写」「Python 编码规范」「代码风格」时触发。py-code-review 审查时引用同一份规则清单；项目级的规范对齐（AGENTS.md、工具链、文档套件）归 mwj-project-init 管。
---

# MWJ Python Style：写代码时的习惯

规则清单只有一份：`references/rules.md`。写代码时照着做，py-code-review 审查时逐条对照。

## 写之前（30 秒）

1. **先看项目自己的规则**：AGENTS.md / CLAUDE.md，以及 pyproject 里的行宽、目标 Python 版本、lint 规则。和本清单冲突的，**以项目为准**。
2. **看周围的代码**：同目录下 2～3 个文件的写法，包括 docstring、异常基类、logger 获取方式、常量位置。新代码要像周围的代码，不要另起一套。
3. 判断项目类型：服务类（FastAPI、有库）、CLI 或设备工具、桌面应用。rules.md 里标了「服务类」的条目，只对服务类项目适用。

## 写的时候（最常用的 12 条，完整规则见 rules.md）

1. 文件头写一句中文 docstring 说明职责；然后写 `from __future__ import annotations`；新文件的类型写 `X | None`，改旧文件时跟随该文件已有的写法。
2. 注释写「为什么」；超时和阈值常量的上方写出处（日期、回执或问题编号）。
3. 异常：一个基类加稳定的 `code`，带 `suggestion`；用 `raise … from`；不把故障吞成空结果。
4. 给用户的报错 = 现象 + 一句中文可执行建议；不把堆栈暴露给前端。
5. 宽泛的 except 必须带 `# noqa: BLE001` 并写上理由。
6. subprocess 统一走 `_run(cmd: list, timeout)`；等设备一律用 `asyncio.wait_for`；重试只保留一层。
7. 日志用 `getLogger(__name__)` 加 `%s` 占位；凭据统一经过脱敏模块，不进日志。
8. CLI：`main(argv) -> int`；退出码 0/1/2/3/130；`--json` 只输出一行到 stdout，进度写到 stderr。
9. 对外的协议、错误码、JSON 字段、参数：**只增不改**；改默认值之前，先回答「不带参数的那条命令现在走哪」。
10. 读写文本显式写 `encoding="utf-8"`；用 `PACKAGED`/`APP_DIR` 判断是否打包。
11. 数据：搬库按「复制 → 核对 → 切换」；同步时空数据不能覆盖有数据的；确定性计算不交给 AI。
12. 测试：走真实入口、用真实数据；假对象记录调用；平台专用的测试加 skip。

## 写完之后

- 跑项目的门禁（`scripts/check.sh` 或项目规定的命令）。
- 用 rules.md 对照自己写的 diff 过一遍，P0/P1 当场修掉。
- 正式审查交给 py-code-review。

## 不要做的

- 不要为单一场景造抽象、加兼容 shim、预留开关。
- 不要顺手改旧代码的风格（例如把 `Optional` 批量换成 `X | None`）；要改就单独提交，并且先问用户。
