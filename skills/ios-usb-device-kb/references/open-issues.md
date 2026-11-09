# 未决问题与参考仓库

## 未决与待验（截至 2026-11）

| 问题 | 状态 |
|---|---|
| iOS 27 上的多指 dtuhidd 布局 | 未验 |
| iOS 27 上的键盘直发表面 512 | 未验，目前要显式开启 |
| 横屏时用界面方向（UIInterfaceOrientation）转正坐标 | 已实现，未经真机验证 |
| 26.2 上关闭投屏后弹出「信任此电脑」 | 未查清，怀疑和配对记录有关 |
| 用 `clear_halt` 代替 `CLEAR_FEATURE` | 有线索，未验证 |
| usbmux 读超时 30s 的通宵稳定性 | 复验未完成 |
| iOS 27 上不装过滤驱动、走 `startmediastream` 取视频 | 未验 |
| 首次安装驱动时，安装器的静默参数（Inno 用 `/SILENT`，NSIS 用 `/S`） | 待核对 |
| 富文本剪贴板单独取数据（RESOLVE）的路径 | 未解决，目前是设备限制 |
| macOS 上 Valeria 状态卡死（`valeria connection not seen`） | 未解决 |

验证了其中任何一条，把结论连同证据等级和 iOS 版本，移到对应主题的文件里。

## 参考仓库

| 仓库 | 用途与结论 |
|---|---|
| [pymobiledevice3](https://github.com/doronz88/pymobiledevice3) | 运行时依赖，提供完整的 CoreDevice 协议栈（隧道、RSD、DDI、剪贴板）。注意它是 GPL 许可 |
| [quicktime_video_hack](https://github.com/danielpaulus/quicktime_video_hack)（qvh） | USB QuickTime 视频协议的权威蓝本，有测试夹具可参考 |
| [RayrenSX/iPhoneMirror](https://github.com/RayrenSX/iPhoneMirror) | 投屏和控制的参考实现，多指 dtuhidd 布局、表面 512、Home 双击等做法可以对照；它没有剪贴板功能 |
| [jkcoxson/idevice](https://github.com/jkcoxson/idevice) | Rust 实现的设备协议库，HID 报文与我们同源；试点能跑通，但没换底层，可以作为长期去 GPL 的备选 |
| [libimobiledevice/usbmuxd](https://github.com/libimobiledevice/usbmuxd) | 设备侧 mux 协议格式的参考 |
| libusb-win32 | 过滤驱动本身 |
