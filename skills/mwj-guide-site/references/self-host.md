# 内网自托管与开机自启

静态站点，任何能发文件的服务都行；下面是不装额外软件的做法。端口示例 8090，先查占用：`lsof -iTCP:8090 -sTCP:LISTEN`（Windows：`netstat -ano | findstr :8090`）。

## macOS

站点目录放在家目录下（如 `~/xxx-site`），**不要放桌面 / 文稿 / 下载**：后台服务被隐私保护拦住，读不到这些目录。

### 登录后自启（LaunchAgent，不需要管理员）

`~/Library/LaunchAgents/<label>.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.example.guide-site</string>
  <key>ProgramArguments</key><array>
    <string>/绝对路径/python3</string><string>-I</string><string>-m</string><string>http.server</string>
    <string>8090</string><string>--bind</string><string>0.0.0.0</string><string>--directory</string><string>/Users/你/xxx-site</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardErrorPath</key><string>/Users/你/xxx-site.log</string>
</dict></plist>
```

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.guide-site.plist
```

python3 用绝对路径（`python3 -c "import sys;print(sys.executable)"`），launchd 里没有 shell 的 PATH。

### 开机即起、不用登录（LaunchDaemon，需要管理员）

同一份 plist 加 `<key>UserName</key><string>你的用户名</string>`（以本人身份跑，不用 root），由**本人在桌面终端**执行（会要密码；SSH / 代理会话里 sudo 常不可用）：

```bash
launchctl bootout gui/$(id -u)/com.example.guide-site; rm ~/Library/LaunchAgents/com.example.guide-site.plist
sudo cp guide-site.daemon.plist /Library/LaunchDaemons/com.example.guide-site.plist
sudo chown root:wheel /Library/LaunchDaemons/com.example.guide-site.plist
sudo launchctl bootstrap system /Library/LaunchDaemons/com.example.guide-site.plist
```

- 开了 FileVault 的机器，开机后要有人登录一次磁盘才解锁，Daemon 也起不来：`fdesetup status` 先看。
- 装完马上 curl 可能是 000（服务还没起来），等 2 秒再试；`launchctl print system/<label>` 看 `state = running`。

## Windows

计划任务「登录时 / 开机时」运行（开机时需要管理员）：

```powershell
schtasks /Create /TN "GuideSite" /SC ONSTART /RU "%USERNAME%" /TR "pythonw -m http.server 8090 --bind 0.0.0.0 --directory C:\guide-site"
```

防火墙第一次会弹窗，选「专用网络」允许。

## 验证

- 本机：`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8090/`
- 别人：用内网 IP（macOS `ipconfig getifaddr en0`）再访问一次，首页、`view.html?f=doc0.md`、下载链接都 200。
