# Windows 打包验收提示词骨架

在 device-handoff 的任务单骨架基础上，专门用于发版打包。路径一律写正斜杠：反斜杠经过对话、命令行、PowerShell 的层层传参后容易被吞掉（MoneyFree R2 曾把 `\build` 吞成 `uild`）。把 `<…>` 换成实际值；项目的发版文档里有现成的提示词（如 iPhoneUsbTouch `docs/打包发布.md §7.3`），就直接用它。

````text
任务：在这台 Windows 上把 <项目> vX.Y.Z 打成 <exe / 安装包 / zip / 7z>，并<连真机验收 / 做启动冒烟>。只打包和验收，不改任何代码。
不做：<不打 APK / 不碰 <下游项目> / 不发布 Release>
规矩：遵守仓库 <docs/打包发布.md §x / AGENTS.md「跨机器协作」>，这里不再复述。不改代码、不提交源码、不提交产物；打包出现 FAIL 就停下回报；会打断人的操作先问一句。

1. 拉代码并核对版本
   cd <仓库目录>
   git pull origin <分支> --tags
   git log --oneline -1 vX.Y.Z      # 标签必须指向 chore(release): vX.Y.Z
   git describe --tags              # vX.Y.Z，或者 vX.Y.Z-N-g<hash>（定版后只加了文档提交也可以）
   git diff --stat vX.Y.Z -- <源码目录> <构建脚本> pyproject.toml uv.lock   # 必须为空
   （模型 B 还没打 tag：把 vX.Y.Z 换成 chore(release) 那个提交的 hash）
   Get-Date -Format "yyyy-MM-dd HH:mm:ss"   # 记为拉取时间
   任何一项不对就停下，回报你实际看到的输出。

2. 打包
   <powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build_exe.ps1>
   最后必须出现 <selftest: PASS / 退出码 0>。出现 FAIL 就把 FAIL 那一行和前后各 20 行贴出来，然后停下。

3. 核对产物
   - 路径：<dist/xxx-X.Y.Z-win64.zip>
   - 用 Get-Item 取 LastWriteTime 和 Length，用 Get-FileHash 取 SHA256。LastWriteTime 必须晚于第 1 步的拉取时间
   - 版本：<xxx.exe --version / 文件属性 ProductVersion> 必须等于 X.Y.Z
   - 压缩：<按用户要求打成 7z / zip>
   - APK（仅当本轮要求时才打）：一律用 gradlew.bat clean assembleRelease，不加 clean 时 Gradle 可能判定 UP-TO-DATE 而不重新打包
   - 拷贝产物前先关掉正在运行的旧 exe。拷贝后回读大小和 SHA256：Copy-Item 失败时不会设置 $LASTEXITCODE，必须靠回读来确认
   - 产物统一拷到 <releases/vX.Y.Z/ 或 releases/R<N>/>（该目录已被 gitignore）

4. 验收
   - 命令行项：<逐条可复制的命令，以及每条的通过标准>
   - 需要人看的项：<短清单>。只把人说的原话抄进回执，agent 自己不去点界面

回执：
- 写到：<回执路径>，格式照 <模板>。产物表必须有路径、LastWriteTime、大小、SHA256
- 只提交回执文件，commit message 用 <receipt: vX.Y.Z 可测 / test(release): vX.Y.Z 打包回执>
- 一句话回复：可测 / 不可测 + 回执文件名
````
