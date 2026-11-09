# 视频投屏：USB QuickTime

协议以开源项目 quicktime_video_hack（qvh）为蓝本。（真机 17 / 18.3 / 26.2 / 27）

## 激活与握手

- 激活隐藏的**配置 5**：控制请求 `bmRequestType=0x40, bRequest=0x52, wValue=0, wIndex=2`；关闭时 `wIndex=0`。
- 握手顺序（只列关键步骤，AFMT / CLOK / TIME 等消息按 qvh 处理）：
  1. PING
  2. CWPA（+1000）
  3. HPD1 ×2，HPA1
  4. CVRP（+0x1000AF）
  5. 之后每收到一个 FEED，回一个 NEED
- 停止：发 HPA0 / HPD0，等两次 RELS。
- 视频数据 `sdat` 是 AVCC 格式，送解码器前要转成 Annex-B。
- **激活慢**：设备只在刚重枚举后才接受激活请求。发开启后等 5s 没反应，就复位端口，并用节点地址判断设备是否真的重枚举了。（真机）

## 与触控共存（usbmux）

- `set_configuration(5)` 会把 Apple 的 usbmux 踢掉，触控隧道随之断开。
- 解法：在配置 5 里 claim `0xFE` 接口，自己实现 usbmuxd，再用 `USBMUXD_SOCKET_ADDRESS` 环境变量让 pymobiledevice3 接进来。这样触控和视频可以同时用。（真机 18.3 / 26.2 / 27）
- libusb0 的 bulk 读超时那一瞬，会丢掉刚到的半个传输。所以 usbmux 读超时设 **30s**，再配合每 25s 一次保活。（真机；30s 方案的通宵复验未完成）
- 设备的 TCP-over-USB 是否重传：原始资料前后说法矛盾（一处说不重传，一处说带重传），**未决**。不要依赖重传来兜底。

## 常见现象

| 现象 | 原因 / 处理 |
|---|---|
| 只有音频，没有 CVRP | 屏幕没亮，先按一次 Home 唤醒（真机 18.3） |
| 状态栏变成 9:41 | Valeria 标志为 true 时进入演示模式 |
| 部分游戏、视频画面变黑 | Valeria 标志为 false 时，被当成了外接显示器 |
| 断流 | 发 fatal `video_lost`，进程以退出码 3 退出；**每一条流都要有断流出口**（曾经拔线后 sidecar 挂了十几个小时都没退出） |

Valeria 标志为 true 和 false 各有代价，**两者不可兼得**，按场景选择，并在界面上说明。

## 卡顿根因（宿主侧）

1. Python 逐字节扫描 590KB 的 IDR 帧找 NAL 边界，每 0.5 秒卡住 100～200ms。改用向量化扫描，或者交给原生代码处理。
2. SPS 缺少 `bitstream_restriction`，解码器会攒满 DPB 才开始输出，表现为约 200ms 没有画面。补上 `max_num_reorder_frames=0` 后渲染达到 59.9fps。（真机 18.3）

**经验**：探针要把循环的每一段都覆盖到（等帧、扫描、发送）；有平均值的地方，同一个时间窗口的最大值也要记下来。只看平均 fps，会得出「发送是稳的」这种假结论。

## 帧率参考

- 正常是 60fps。静止画面的帧率因环境而异：有的环境约 20fps（设备不推重复帧，属于正常），修复卡顿后的宿主上测到 59.3～59.9fps。不要拿静止画面的帧率判断是否卡顿。
- Windows 定时器默认精度是 15.6ms，用 `timeBeginPeriod(1)` 提到 1ms。
- 只有 2fps 左右：说明没装过滤驱动，走的是降级路径（见 windows-driver.md）。
