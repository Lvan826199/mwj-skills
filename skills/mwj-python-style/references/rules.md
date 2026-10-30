# 梦无矶 Python 编码规则（唯一清单）

来源：MyProject 下 9 个 Python 项目的代码抽样，以及归因文档、记忆、AGENTS/CLAUDE.md。写代码时照着做（mwj-python-style），审查时逐条对照（py-code-review）。

- 括号里的 P 级是审查时的建议级别。
- 「新代码」表示只要求新写的代码，旧代码不追溯。
- 标「服务类」的条目，CLI 和库项目可以跳过。
- **项目自己的规则（AGENTS.md、pyproject）和本清单冲突时，以项目为准。** 行宽、目标版本都跟随 pyproject，不要写死。

审查时**只审 diff 里新增或修改的行**；旧代码里的同类问题，最多在「补充建议」里提一句。

---

## 一、模块结构与命名

- 文件头写中文 docstring：第一行用一句话说清职责；复杂模块再写「为什么这样设计」「不负责什么」。（P3）
- docstring 之后、import 之前写 `from __future__ import annotations`。**新文件**用 `X | None`、`list[str]`；在已有文件里改动时，跟随该文件现有的写法（文件里用的是 `Optional`，就继续用 `Optional`），要统一就单独提交。（P3）
- import 分三组：标准库、三方库、本包。**不要在 import 之间夹常量和注释。** 重依赖放到函数里懒加载，并写明原因（`import uvicorn  # 懒加载：只有 serve 子命令需要`）。（P3）
- 常量放在模块顶部，全大写；可变的模块级状态用 `_` 前缀，并配一把锁：
  ```python
  _failure_counts: dict[str, int] = {}
  _lock = threading.Lock()
  ```
- `__all__` 只在包的 `__init__.py` 里用来做再导出。
- 标识符用英文；注释、docstring、给用户看的文案用中文。
- 布尔值和状态查询用 `is_`/`has_` 前缀；私有函数用 `_snake`。
- 单位写进名字：毫秒用 `_ms`；秒的后缀在项目内统一（新项目用 `_s`）；超时常量命名为 `XXX_TIMEOUT`，单位是秒，类型是 float。（P3）
- 环境变量用「项目前缀 + 常量名」，集中定义在 `settings.py` 或 `paths.py` 里。

## 二、注释与可追溯性

- **复杂逻辑用中文注释写「为什么」**，不写「做了什么」。（P2）
- **超时、重试、阈值这类魔法常量，上方注释写出处**：日期、回执编号、问题编号，标记跟在原因后面：
  ```python
  # 预算留宽是为了兜住慢设备，别再凭印象砍（回执 15 就是砍出来的一轮全灭）。
  CLIPBOARD_READ_TIMEOUT = 25.0
  ```
  改这类常量的 diff 如果没写出处，要追问。（P1）反例：把「约 17 秒返回」转述成「秒回」，超时砍到 6 秒，真机直接失败。
- 否决过的方案也写进注释（「实测淘汰：xx，原因是 xx」），免得下一个人再试一遍。（P3）
- 不提交无关的、未使用的代码，调试用的 print，或注释掉的大段旧代码。（P2）

## 三、类型与数据

- 值对象（配置、提示、分类结果）用 `@dataclass(frozen=True)`；API 边界用 Pydantic v2（`Field(description="中文")`，互斥校验用 `model_validator(mode="after")`）。（P3）
- 小的取值集合用 `Literal`；错误码用 `StrEnum`（3.11 以上），或者用带 `code` 属性的异常类。
- `Protocol` 只描述**真正被消费的那部分接口**，并要有测试兜底，否则会退化成形同虚设的文档。（P2）
- 时间和 sleep 做成可注入的（`ClockPort`，或模块级 `_sleep = time.sleep`）；测试里替换它，不要全局 patch。（P2）

## 四、错误处理

- **一个异常基类 + 稳定的字符串错误码**，子类只覆写 `code`；异常可以带 `suggestion`：
  ```python
  class ToolError(Exception):
      code = "error"
  class NoDeviceError(ToolError):
      code = "no_device"
  ```
  错误码属于对外契约，**只增不改**。（P1）
- **给用户的报错 = 现象 + 一句中文可执行建议**；兜底 handler 只返回「服务器内部错误，请稍后重试」，堆栈用 `logger.exception` 写进日志，不发给前端。（P1，服务类）
- 用 `raise ... from exc` 保留原异常链。（P2）
- 区分「目标没找到」和「基础设施故障」：没找到返回空结果，故障显式抛出，不要把故障吞成空结果。（P1）
- 宽泛的 `except Exception` 必须带 `# noqa: BLE001` 并在后面写上理由（分隔用 ` - ` 或空格都可以，跟随项目现有写法）。没写理由的吞异常（`pass`，或者只打日志然后继续）要标出来；写了理由的有意降级不报。（P1）
- 能不能重试按错误码区分：用 `PERMANENT_* = frozenset({...})` 列出不可自愈的码，这些码不重试。（P2）
- 提示语改在用户最终看到的那一层；要有测试断言最终 message 里有这句话。（P2）

## 五、日志

- 用 `logging.getLogger(__name__)` 获取 logger（CLI 进程用固定名）；参数用 `%s` 占位，不用 f-string。（P3）
- 服务类：用 contextvars 透传 `request_id`/`trace_id`，由中间件生成，响应头里带回。（P2，服务类）
- 级别分流：终端只显示关键信息，文件里记 DEBUG 和完整堆栈，日志按天保留并设上限。健康类指标在异常时要升到 WARNING，有平均值就要同时记最大值。（P2）
- 脱敏集中在一个工具模块里做（按键名表加正则），**凭据不进代码、测试、日志、提示词模板**，只从本机配置读取。（P0）
- 例外：项目规则里明确写了「有意保留」的（例如私有仓库里经过评估的配置快照），按项目规则处理，不再当作泄露报告。

## 六、并发、IO 与外部命令

- 设备和硬件交互用 asyncio，每次等待都包一层 `asyncio.wait_for(…, XXX_TIMEOUT)`；同步库和模型推理放到线程里并加锁；服务端 IO 用 async。（P1）
- **subprocess 封装成一个 `_run`，一律传参数列表并设置 timeout**，禁止 `shell=True` 拼字符串：
  ```python
  def _run(cmd: list[str], timeout: float) -> tuple[int, str]:
      proc = subprocess.run(cmd, capture_output=True, timeout=timeout,
                            encoding="utf-8", errors="replace",
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
      return proc.returncode, proc.stdout + proc.stderr
  ```
  （P1；拼接了用户输入的升为 P0）
- 重试写成手写循环，退避时间用常量元组（`RETRY_WAITS = (1.0, 3.0)`）；4xx 直接抛（429 除外）。**重试只保留一层**，遇到「偶发失败」不要再往上叠一层。（P2）
- ctypes 调 Win32 时，返回句柄或指针的函数必须声明 `restype`/`argtypes`（句柄用 `c_void_p`）。（P0）
- 改了系统状态的操作，要用独立的手段回读验证，回读不能和写入共用同一个常量或函数；外部 exe 报「成功」不等于真的做成了。（P1）
- 杀进程按 pid 或项目路径过滤，禁止按进程名 `pkill`、`taskkill /IM`。（P1）

## 七、CLI

- 统一的签名：`build_parser()` 加 `main(argv: Sequence[str] | None = None) -> int`，入口写 `raise SystemExit(main())`。子命令用 `add_subparsers(dest="command", required=True)`，再用 `set_defaults(handler=…)` 绑定处理函数。（P2）
- 退出码：0 成功，1 一般失败，2 参数或环境错误，3 无结果，130 是 Ctrl+C。退出码写进文档，属于契约。（P2）
- `--json` 只输出一行到 stdout（`ensure_ascii=False`）；给人看的进度写到 stderr。（P2）
- help 用中文写，说明默认值和适用场景。
- **已发版下游在调用的协议、错误码、JSON 字段、CLI 参数：只能新增，不能改名或删除。** 改默认值也算改契约，要先回答「不带参数的那条命令现在走哪条路径」，并用一条端到端测试钉住答案。（P0）

## 八、配置、路径与平台

- 打包判断和应用目录统一这样写：
  ```python
  PACKAGED = bool(getattr(sys, "frozen", False) or "__compiled__" in globals())
  APP_DIR = Path(sys.executable).resolve().parent if PACKAGED else ROOT_DIR
  ```
  外部工具先在随包目录里找（`.exe` 和无后缀两种都试），找不到再用 `shutil.which`。（P2）
- 读写文本一律显式写 `encoding="utf-8"`；控制台输出流用 `reconfigure(errors="replace")`。（P2）
- Windows 上的 asyncio 事件循环策略按项目需要定：**用到 asyncio 子进程时必须用默认的 Proactor**，Selector 不支持子进程；只有某些库要求时才切 Selector，并在注释里写明原因。（P2）
- 配置用 pydantic-settings 加项目前缀；`.env.example` 入库，`.env` 放进 gitignore。（P2，服务类）
- 版本号只有一个来源：运行时用 `importlib.metadata.version()` 读取，或者有一致性测试守住。（P2；同一项目已经报过一次、用户决定不改的，后续审查不再重复报）
- bat 文件只写 ASCII，开头加 `chcp 65001`；同一件事不要在 bat 和程序里各写一套；路径不要硬编码盘符或 `Program Files`。（P2）

## 九、数据

- **搬正在使用的数据库或文件**：复制 → 核对行数 → 切换 → 退役旧文件，不要直接用 `shutil.move`。（P0）
- 长循环、网络同步不能一直开着写事务，要按条提交。（P1）
- 同步和导入两个方向都要有「空的不能覆盖有的」这条底线。（P0）
- 跨进程回写状态要用条件 UPDATE，不能读-改-写。（P1，服务类）
- 库里只存相对路径；正在使用的数据库不要放进同步目录。（P1）
- **确定性计算（金额、收益、回测、日期）用代码算，不交给 AI**。（P1）
- 前端拉数据失败时，不能把已有数据换成错误页。（P2）

## 十、测试

- 测试名写成 `test_<对象>_<场景>_<期望>`。新项目用 pytest，加 `monkeypatch` 和 `parametrize`。
- **走真实入口**（`cli.main(argv)`、真实路由）；**用真实数据**（真图、真文件）；不要 mock 被测对象的核心行为。（P1）
- 假对象写成记录调用的类（`self.calls.append(...)`），少用 MagicMock。回放型的假服务只允许回执里真实出现过的设备行为，遇到没见过的用法当场失败。（P1）
- 同一个功能有两条调用路径的，两条都要测。（P1）
- 断言写具体值，必要时用 `assert x == y, got` 把上下文带出来。
- pytest 标记分 `unit` / `integration` / `smoke`，回归只跑 `-m unit`；集成测试要自己清理，测试库名以 `_test` 结尾。（P1，服务类）
- 平台专用的测试要加 `skipif`（例如 Windows 专用测试在 Linux 上跳过）。（P2）

## 十一、反模式（用户明确说过不要）

- 为单一场景造 helper 或抽象层，加兼容 shim，或者「预留开关」。（P2）
- 在各端各实现一套规则；网络层随手引入新的三方库（项目规定只用标准库的，就守住唯一出口）。（P2）
- 修了 bug 不写归因（见 postmortem）。（P1）
