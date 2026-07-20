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
- 🛡️ 局域网管控：**一键禁止上网 / 恢复**（点击"管控"列开关）
- 📊 观测局域网内其他设备的实时上行/下行网速 (KB/s)

## Windows 版
```bash
python lan_scanner.py
# 或双击 build_exe.bat 打包成 lan_scanner.exe
```

### 局域网管控功能（一键禁止上网 / 观测网速）
普通电脑不是路由器，无法真正"路由拦截"。本功能采用 **ARP 中间人** 方式实现：
- **禁止上网**：把自己伪装成网关，丢弃目标设备发往外网的包 → 断网。
- **观测网速**：同样当中间人，但正常转发流量并统计上行/下行字节。

**使用前准备：**
1. 必须 **以管理员身份运行** 程序（右键 → 以管理员身份运行）。
2. 安装依赖：
   ```bash
   pip install scapy
   ```
3. 安装 **Npcap**（https://npcap.com ，安装时勾选 WinPcap 兼容模式）。

**使用方法：**
- 列表「管控」列显示 `○允许 / ■已禁网 / ●测速中`，**直接点击该列单元格**即可一键禁网或恢复。
- 右键菜单 →「禁止上网 / 恢复」「观测网速 / 停止」。
- 顶部「⛔ 停止全部管控」一键还原所有被控设备。
- 「流量」列实时显示上行/下行 KB/s（仅观测中显示）。
- 关闭程序会自动停止欺骗并还原 ARP 表。

⚠️ **仅限你自己拥有或已授权的局域网内测试使用**，并事先取得相关方同意。开启管控后目标流量会经过本机；关闭开关或退出程序会立即还原，不影响网络。

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
