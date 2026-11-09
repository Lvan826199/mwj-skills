---
name: ios-usb-device-kb
description: iOS 真机 USB 开发知识库（截至 2026-11，免越狱、不用 WDA）：CoreDevice 隧道 + HID 触控（单指/多指 dtuhidd 整帧报文、横屏坐标）、键盘直发表面 512 与中文剪贴板粘贴、pasteboardservice 剪贴板、USB QuickTime 投屏（配置 5、自研 usbmux 与触控共存、卡顿根因）、Windows libusb 过滤驱动（UpperFilters 0x11、只写父节点）、sidecar 协议约定、真机联调守则、版本矩阵与排障决策树。做 iOS 触控、投屏、剪贴板、键盘、设备连接、Windows 驱动相关的开发或排障时触发；看到 9021、IncompleteReadError、only audio、video_lost、no_device、GOAWAY 等现象时触发。
---

# iOS USB 真机知识库

这些结论是在真机上一轮轮踩出来的，每条都标了证据等级：**真机**（注明 iOS 版本）、**推断**、**未决**。**先查这里再动手**，别重走弯路。版本号和设备行为会变，遇到和这里对不上的，以新的真机证据为准，并回来更新本知识库。

## 版本矩阵

| 能力 | iOS 16 及以下 | 17.x | 18.x | 26.x | 27.0（仅一台 iPad 验证） |
|---|---|---|---|---|---|
| 触控（CoreDevice HID） | ✗ 没有 CoreDevice | ✗ HID 表面列表为空 | ✓ 直连（媒体流鉴权返回 9021） | ✓ 直连（9021） | ✓ 媒体流鉴权能通过 |
| 多指（dtuhidd 整帧） | — | — | ✓ 18.3 | ✓ 26.2 | 未验 |
| 键盘（直发表面 512） | — | — | ✓ 自动启用 | ✓ | 未验，需显式开启 |
| 剪贴板（pasteboardservice） | — | — | ✓ 18.3 | ✓ 写入 26.2（读取推断可用） | 推断可用 |
| 视频（USB QuickTime） | 理论可用，未测 | ✓ | ✓ | ✓ | ✓ |

前置条件（每台设备）：已点「信任此电脑」、开了开发者模式、挂载了个性化 DDI。DDI **每次开机都要重新签名挂载**，签名需要能访问 `gs.apple.com`。

## 硬规则（违反就会出事）

1. **不用 WDA、tidevice、go-ios**。触控只走 CoreDevice 隧道 → RSD → `universalhidservice`。
2. **绝不调用 `create_keyboard_service`**（createService）。所有版本上它都会让隧道 EOF。键盘报文直接发到设备自带的表面 512。
3. **多指只用 dtuhidd 整帧布局**；每一帧都要带上全部活动触点，漏掉的触点会被当成抬起。
4. **鉴权顺序是先试媒体流，被拒（9021）再直连**。不要按版本号去猜。
5. **剪贴板：一条连接只发一次 PULL**。每个请求自己开连接、自己关。
6. **Windows 过滤驱动只写 Apple 复合设备父节点的 UpperFilters（属性码 0x11）**，绝不写 `MI_*` 接口节点。写完用 `reg query` 独立回读验证。
7. **投屏窗口不许强杀**，强杀会导致设备端服务卡死。设备僵死时重启手机，**只重试一次**。
8. **sidecar 协议、错误码、capabilities、`--json` 字段只增不改**。
9. **每一条流都要有断流出口**：拔线、对端死掉时，进程必须能退出或上报，不能一直挂着。
10. 超时常量按实测最慢值留余量，并在注释里写明出处。

## 排障决策树

| 现象 | 先怎么做 | 详见 |
|---|---|---|
| 一台设备都列不出来（`no_device`） | 跑 `doctor`，逐层检查：AMDS 服务 → USB 节点 → usbmuxd → 配对记录 → 过滤驱动 → 开发者模式 | windows-driver.md |
| 装过驱动后整台电脑读不到 iOS 设备 | 大概率是写进了 LowerFilters，或者写到了 `MI_*` 节点；先按恢复流程清掉，再重装 | windows-driver.md |
| 媒体流鉴权返回 9021 | 正常现象（18/26），改走直连 HID | touch-hid.md |
| 触控点了没反应 / 位置偏 | 坐标要用逻辑点（pt），不能用像素；横屏要看界面方向；一次性客户端断开前要等约 150ms | touch-hid.md |
| 双指缩放无效 | 检查是不是整帧报文、identity 表、时间戳偏移 45、slot 有没有碰撞 | touch-hid.md |
| 隧道 `IncompleteReadError 0/9` | 是不是调用了 createService；Python 3.11+ 要先单独接住 `TimeoutError`，不要当成连接被掐 | keyboard-clipboard.md |
| 中文输入变成乱字母 | 走「剪贴板 + Cmd+V」，组合键要分报文发 | keyboard-clipboard.md |
| 剪贴板写入后整条连接断掉（GOAWAY） | 单帧超过 16384 字节，要分片 | keyboard-clipboard.md |
| 剪贴板读取超时 | 别人 App 复制的富文本读不出来，这是设备限制；纯文本约 2.5s；预算留 25s | keyboard-clipboard.md |
| 只有声音、没有画面 | 屏幕没亮：先按一次 Home 唤醒 | video-quicktime.md |
| 投屏激活很慢或没反应 | 设备只在刚重枚举后才接受激活；等 5s 没反应就端口复位 | video-quicktime.md |
| 开了投屏后触控断了 | 配置 5 会踢掉 Apple usbmux，要自研 usbmux 共存 | video-quicktime.md |
| 只有 2fps 左右 | 没装过滤驱动，走的是降级路径 | windows-driver.md |
| 画面卡顿或延迟大 | 宿主侧 Python 逐字节扫描 IDR；SPS 缺 `bitstream_restriction` | video-quicktime.md |
| 状态栏变成 9:41 / 某些 App 画面黑屏 | Valeria 标志两难，二者不可兼得 | video-quicktime.md |
| 设备不发 PING、OUT 写超时 | 重启手机后只重试一次，进程内重试无效 | field-testing.md |
| 退出时蓝屏（Windows） | 收尾时不要 `set_configuration` 回切；读线程没退出时不要释放接口 | windows-driver.md |

## 参考资料

| 文件 | 内容 |
|---|---|
| `references/touch-hid.md` | 路线与鉴权、单指和多指报文、坐标与方向、历次失败与翻案 |
| `references/keyboard-clipboard.md` | 键盘表面 512、组合键、中文粘贴、pasteboardservice 读写 |
| `references/video-quicktime.md` | 配置 5 握手、usbmux 共存、超时与丢包、Valeria、卡顿根因、帧率 |
| `references/windows-driver.md` | libusb-win32 过滤驱动、UpperFilters 与 LowerFilters、ctypes、doctor、收尾蓝屏 |
| `references/field-testing.md` | sidecar 协议约定、真机联调守则、环境依赖、打包 |
| `references/open-issues.md` | 未决与待验问题、参考仓库 |

在真机上证实了新结论、或者推翻了旧结论，**当天就回来更新对应文件**，并标上证据等级和 iOS 版本。
