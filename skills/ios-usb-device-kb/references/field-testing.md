# sidecar 协议、真机联调与环境

## sidecar 协议约定

- 通信方式：stdin / stdout 各一行一个 JSON，stderr 只写日志。
- **命令、事件、错误码、capabilities、`--json` 字段只增不改**：已发版的宿主还在调用，改名或删字段会直接搞坏它们。
- 启动序列：`hello` → `status`* → `ready`。`ready` 里带 `capabilities`、`auth_mode`（direct / mediastream）、`video`。
- capabilities 按设备动态声明，宿主根据它把不支持的按钮置灰。
- 退出码：0 正常，2 启动失败，3 运行中视频丢失（`video_lost`）。
- 错误分两类：
  - **非致命**：`clipboard_*`、`app_control_unavailable` 这类，只报错，不触发重连；
  - **触控断开**：进程不退出，发 `touch_lost`，等宿主或用户发起重连。
- 时间预算：
  - quit 的宽限期 12s；
  - 锁屏要在停流之后再按；
  - `ready` 的超时要留 150s 以上：锁屏或熄屏时，隐藏配置的激活要等 30～100 秒。
- 建议用协议快照测试守住「只增不改」：把命令、事件、错误码集合存成 golden 文件，断言只增不减。

## 真机联调守则

- **一轮只解决一个问题**：要么验证一个修复，要么回答一个问题。
- **假服务只允许真机上见过的行为**：行为回放测试遇到没见过的用法要当场失败，而且要走真正的命令入口（`cli.main(argv)`）。路由、时间预算、连接寿命这三层，单元测试抓不到。
- 超时、重试、阈值常量的注释要写明出处；转述实测数据前，先回原文核对，别把「约 17 秒」记成「秒回」。
- **投屏窗口必须由人正常关闭**，不许 `taskkill` 强杀，否则设备端的投屏服务会卡死。
- 设备不发 PING、OUT 写超时：重启手机、解锁后**只重试一次**。dtuhidd 卡死时，进程内重试无效。
- 同一个功能有两条调用路径（CLI / sidecar），两条都要真机验证。
- 报错先要完整的调用栈，别凭推理猜位置。
- 健康指标要同时记平均值和最大值；异常时升到 WARNING 级别。

## 环境依赖

- Python 3.10～3.13。
- `lzfse` 在 Windows 上只有到 cp312 的轮子，3.13 用 `pyliblzfse` 做垫片转发；3.14 缺 `pylzss` 的轮子。
- 部分国内 PyPI 镜像同步滞后，可能拿不到新版 pymobiledevice3，换一个镜像即可。
- DDI 首次运行要从 GitHub 下载约 30MB，离线时用 `--ddi-dir` 指定；TSS 签名仍需能访问 `gs.apple.com`。
- Windows 的 bat 脚本开头加 `chcp 65001`，提示文字只用 ASCII。

## 打包（Nuitka）

- 要显式带上 `wintun.dll`。
- 不要用 `--include-package=av`。
- 打包后在目标机上跑 `selftest` 和 `--version`，确认版本号和依赖都没问题。
