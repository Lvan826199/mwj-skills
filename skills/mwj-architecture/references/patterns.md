# 架构模式库

每种模式都按「适用场景 → 骨架 → 依赖与链路 → 不可违反的规则 → 守护手段 → 踩过的坑」来写。代表项目只作为参照，具体以各项目自己的 AGENTS/CLAUDE.md 为准。

---

## A. FastAPI 分层平台（代表：AiTestProject）

**适用场景**：多用户、多模块的 Web 平台，有数据库、权限和后台异步任务。

```
app/
├─ main.py            中间件、异常 handler、路由挂载
├─ core/              config / deps / response / exceptions / security
├─ api/v1/endpoints/<域>/
├─ schemas/<域>/      Pydantic 入参、出参
├─ services/<域>/     业务编排；口径只在一处定义（如角色矩阵）
├─ crud/base.py       CRUDBase[Model, Create, Update]，只 flush 不 commit
├─ models/<域>/
├─ tasks/             Celery：celery_app.py + <域>/
├─ db/                session（每个请求一个事务）、migration_filters
└─ libs/              不依赖平台的执行引擎
```

**链路**：endpoint（用 `SessionDep`、`CurrentUserDep` 注入依赖，先校验权限）→ service / crud → `return success(...)`。请求结束时 `get_session` 统一 commit，出异常就 rollback；`BusinessException` 由全局 handler 转成 `{code, message, data}`。

**规则**
- 统一响应 `ResponseModel[T]`；业务错误统一抛 `BusinessException`；兜底的 500 也用统一结构，并且不泄露堆栈。
- crud 层不 commit；多步操作放在同一个事务里；不许私自改 API 字段。
- 按业务域分目录，各层目录结构保持一致。新增权限要同时登记到权限表、矩阵和路由。
- Celery 任务必须在 `include` 里登记（漏登记时 worker 会报 unregistered task 并直接丢掉）；用 threads 池时 `time_limit` 不生效，要在任务内部自己 `wait_for`。
- Alembic autogenerate 只用来生成新表、增列、删列；改列和改索引一律手写迁移。

**守护**：CI 跑 lint、`pytest -m unit` 加覆盖率棘轮；用静态扫描确保「所有写接口都有权限校验」，豁免要登记原因。**建议补**一条依赖方向测试：crud 不许 import services 或 api。

**坑**
- 跨进程回写状态要用条件 UPDATE，读-改-写会丢失更新。
- cron 调度要先占位再触发，否则会重复触发。
- 测试文件不打 marker，CI 就会静默跳过它。

---

## B. 六边形架构（代表：AutoAppAgent）

**适用场景**：领域规则复杂、长期演进、外部依赖多（设备、LLM、多个库），需要注入测试替身的单体服务。

```
server/
├─ domain/            纯规则，不依赖其他任何层
├─ application/       服务 + ports.py（Protocol 端口）
├─ infrastructure/    设备 / LLM / 持久化等适配器
├─ api/               deps.py + routers/（只做转发）
├─ bootstrap/         container / app / lifecycle，唯一的装配点
└─ protocol.py        Pydantic 契约核，所有层都可以用
tests/test_architecture.py  依赖方向 + 结构规则 + 只许收缩的基线
```

**依赖规则**：domain 不依赖其他层；infrastructure 不依赖 application、api、bootstrap；application 不依赖 api、bootstrap；只有 bootstrap 可以 import 一切。

**链路**：router → 从 `app.state.container` 取服务 → application 通过端口调用 → infrastructure 实现。

**规则**
- 依赖都从容器里取，不 import 模块级单例；router 里不写业务逻辑。
- 端口只描述真正被消费的接口，并要有测试确认它真的被实现、被使用，否则会变成「伪装成契约的文档」。
- 项目要有「定义性不变量」（违反就等于换了个项目，例如「零 App 特判」）、「走偏预警」（例如同一份内容出现第二个定义点）、「改动联动表」（改 X 必须一并检查 Y），三者都写进 AGENTS/CLAUDE.md。

**守护**：`references/test_architecture_template.py`（依赖方向），可以扩展结构规则：函数不超过 150 行、禁止模块级单例、应用层依赖不许是裸 `Any`。违规基线**只许缩、不许增**，陈旧的条目也判红。

**坑**
- `ports.py` 写好了却没人引用。
- 测试读到开发机的数据目录，或者被绑到了真机上。必须有隔离夹具。

---

## C. CLI + sidecar 设备工具（代表：iPhoneUsbTouch/iostouch）

**适用场景**：设备或硬件能力既要给人用（CLI），也要给多语言的宿主程序用（子进程协议）。

```
<tool>/
├─ cli.py         argparse 子命令，main(argv) -> int
├─ sidecar.py     serve 子命令：stdin/stdout JSON-lines，PROTOCOL_VERSION + CAPABILITIES
├─ controller.py  设备能力
├─ errors.py      每个异常一个稳定的 code
├─ doctor.py      环境逐层自检，直接给出下一步怎么做，退出码 0/1
└─ *.py --json    机器可读的状态
docs/sidecar协议.md
```

**链路**：宿主往 stdin 写 `{"cmd":..,"id":..}` → 分发到 controller → stdout 返回 `ok` 或 `error{code,fatal}`；stderr 只写日志。启动顺序是 hello → status* → ready（附带 capabilities）。退出码：0 正常，2 启动失败，3 运行中丢失。

**规则**
- **协议、错误码、capabilities、`--json` 字段只能新增，不能改名或删除**；已发版的宿主还在调用它们。
- capabilities 按设备动态声明，宿主根据它置灰按钮；非致命错误不触发重连。
- **每一条流都要有断流出口**：拔线、对端死掉时必须能退出，不能一直挂着。
- 超时常量要注明出处；行为回放测试只允许回执里真实出现过的设备行为，并且要走 `cli.main(argv)` 这个真实入口。

**守护**：sidecar 协议测试、设备回放测试。**建议补**协议快照测试：把命令、事件、错误码集合存成 golden 文件，断言只增不减。

**变体：引擎 CLI + 管理平台（代表：MwjRunner）**。平台用子进程调用引擎 CLI，契约就是「退出码 + JSON 报告」；执行与报告分离，协议执行与调度分离。平台本身用 A 的简化版。

---

## D. Electron + Python 后端 sidecar（代表：MSCA）

**适用场景**：要离线可用的桌面应用，同一套前端也能以 Web 方式部署；后端可以再拉起 C 类工具。

```
electron/
├─ main.js                单实例锁、IPC、before-quit 收尾
├─ preload.js             contextBridge 白名单 API
├─ backend-manager.js     spawn、/health 轮询、崩溃重启（有上限）、端口文件
└─ source-fingerprint.js  开发模式下识别「旧后端残留」
backend/                  Python 后端（api / core / drivers / websocket）
frontend/                 Vue；所有请求都通过 getBackendUrl() 拼地址
scripts/prepare-<tool>.mjs  打包时内嵌 C 类工具的产物
```

**链路**：main 启动后端（从固定端口起探测可用端口，写入端口文件，轮询 `/health`）→ 渲染进程通过 preload 取端口 → HTTP/WS 调后端 → 后端 driver 拉起 sidecar。

**规则**
- 前端一律用 `getBackendUrl()` 拼地址，因为安装版是从 `file://` 加载的。
- 退出时先调 `stop-all` 优雅停止，再结束进程。**只清理本安装目录下的后端进程**，不按映像名全机清理。
- 第二个实例绝不能走 `stop()`，否则会停掉第一个实例的后端。
- 崩溃重启要设上限；IPC 只开放固定的目录和文件名。
- 探针、验修复的轮次用开发模式跑源码；只有发版或改了打包链路才打包。

**守护**：源码级扫描测试（禁止前端直接写地址）、指纹一致性测试、`npm run verify`。

**坑**
- 启动期后端退出一次之后就再也起不来。
- 按映像名误杀了别人的后端。
- 新起的 Electron 复用了残留的旧后端，导致新前端配旧后端。

---

## E. pywebview 桌面 + 内嵌 HTTP + Android WebView 外壳（代表：MoneyFree）

**适用场景**：单用户、本地数据（SQLite），桌面和手机共用一套前端和核心逻辑，用文件同步代替服务器。

```
<app>/core/            纯业务：db 迁移 / 账本 / 同步 / http_client（只用标准库）
<app>/android_entry.py start(data_root, dist) -> {port}
desktop/backend/api.py ThreadingHTTPServer(127.0.0.1, 0) + token
desktop/launcher.py    start_server → webview.create_window
desktop/frontend/      Vue；手机端用 body.mobile 适配
android/.../MainActivity.kt  Chaquopy 调 start() → WebView.loadUrl
```

**链路**：外壳（launcher 或 MainActivity）→ `start_server()`（先迁移，再绑随机端口）→ 返回的 index.html 里注入 token → 前端请求 `/api/*` 时带上 token → 调 core。

**规则**
- 桌面和手机都只能走 core，不许各自实现一套规则。
- 改 schema 要升 `SCHEMA_VERSION` 并写迁移，迁移只补不覆盖。
- 正在使用的数据库不放进同步目录，只交换快照；**空账本不能覆盖有数据的账本**（两个方向都要拦）。
- 确定性计算不交给 AI；搬库按「复制 → 核对 → 切换 → 退役」；同步要按条提交，不能开长事务。

**守护**：pytest 加截图脚本。**建议补** import 测试：core 不许 import desktop、webview（用模板，FORBIDDEN 里写 `{"<app>.core": ("desktop", "webview")}`）。

---

## F. 推理引擎服务（代表：OcrYoloEngine）

**适用场景**：CPU 或 GPU 重计算、需要限流和可观测性的服务（OCR、检测、模型推理）。

```
src/<pkg>/
├─ service/        FastAPI 路由 + deps（装配 registry、executor）
├─ concurrency/    有界池 + 模型锁
├─ preprocessing/
├─ recognizers/    各个模型的适配器
├─ registry/       模型和模板的注册
├─ observability/  JSON 日志 + request_id + 零依赖指标
├─ errors.py       ErrorCode(StrEnum) → HTTP 状态映射
└─ settings.py     pydantic-settings，带前缀
```

**规则**
- 错误响应带 `request_id` 和稳定的错误码；可选依赖缺失时返回 503 加说明，不返回裸 500。
- **并发名额要等任务真正结束才归还**，否则超时后的僵尸任务会架空限流。
- 测试用真实图片和真实模板，不 mock 被测对象的核心行为；覆盖率门禁只升不降。
- 架构决定写成 ADR（`docs/设计与决策.md`）。

---

## 跨模式通用原则

1. **对外契约只增不改**：协议、错误码、capabilities、`--json` 字段、API 字段都要带版本号。
2. **单一事实源**：同一个口径只定义一次（矩阵、目录、core 包）；跨层只传枚举，不传渲染好的文案。
3. **确定性的事不交给 AI**：遍历、去重、完成判定、金额计算交给框架或代码，语义判断交给模型。
4. **错误要结构化**：稳定的 code 加人话 message 加建议；「没找到」和「故障」分开报。
5. **用机器守规则**：依赖方向和门禁都用测试守住；违规基线只许缩；豁免必须写原因。
6. **进程生命周期要闭环**：每条流都有出口；退出前先优雅停止；识别进程用绝对路径或源码指纹；要有单实例锁。
7. **数据不绑定机器**：库里只存相对路径；正在使用的库不放进同步目录；迁移只补不覆盖。
8. **装配点唯一**：容器、lifespan 或 bootstrap 负责注入，测试替身也从这里注入。
