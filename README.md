# LAN Scanner — 局域网设备扫描器

复古 Win9x 风格局域网扫描工具，支持 Windows 和 Android。

## 功能
- 🔍 并发 Ping 扫描 (1-254)
- 📋 ARP MAC 地址解析
- 🏷️ OUI 厂商识别 (~90 条常见厂商)
- 💻 设备名反向 DNS 解析
- 🚪 30 个常用端口扫描
- 🕐 最近在线时间
- 📡 本机 WiFi/有线连接检测
- 🔎 实时搜索过滤
- 💾 保存/加载/导出 (JSON / CSV)
- ✏️ 编辑名称备注、删除设备

## Windows 版
```bash
python lan_scanner.py
# 或双击 build_exe.bat 打包成 lan_scanner.exe
```

## Android 版 (Kivy)
```bash
# 本地打包 (需 Linux):
pip install buildozer
buildozer android debug

# GitHub Actions 自动打包:
# 推送代码到 main 分支 → Actions 自动构建 APK → Artifacts 下载
```

## 下载 APK
推送到 GitHub 后，前往 **Actions → Build Android APK → Artifacts** 下载 `LANScanner-debug-apk.zip`，解压后安装 APK。

⚠️ 安卓上 ping/ARP 可能受系统权限限制；部分 ROM 需 root 才能读 `/proc/net/arp`。
