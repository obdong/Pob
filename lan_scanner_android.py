#!/usr/bin/env python3
"""
LAN Scanner - Android Version (Kivy Framework)
Retro Win9x Style LAN Device Scanner for Android
Single-file application with all UI, logic, and data embedded.
"""

import os
import sys
import json
import csv
import socket
import subprocess
import threading
import time
import re
import concurrent.futures
from datetime import datetime
from functools import partial

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.properties import (
    StringProperty, NumericProperty, ListProperty,
    ObjectProperty, BooleanProperty
)
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp, sp

# ──────────────── Platform Detection ────────────────
try:
    import android as _android_mod
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = os.path.exists('/proc/net/arp')

# ──────────────── OUI Vendor Dictionary ────────────────
OUI_DICT = {
    "3C22FB": "Apple", "A4B197": "Apple", "ACDE48": "Apple", "000393": "Apple",
    "0017F2": "Apple", "001CB3": "Apple", "5C95AE": "Apple", "7C6D62": "Apple",
    "881FB4": "Apple", "A45E60": "Apple", "A8667F": "Apple", "B8782E": "Apple",
    "C82A14": "Apple", "D02312": "Apple", "E0F847": "Apple", "F01898": "Apple",
    "F45C89": "Apple", "DC2C6E": "Apple", "A8BB19": "Apple", "28A01B": "Apple",
    "581FAA": "Apple", "90B931": "Apple", "948426": "Apple", "6C72D9": "Apple",
    "508CE6": "Samsung", "A0CBFD": "Samsung", "B47443": "Samsung",
    "C8BA94": "Samsung", "E0D9E3": "Samsung", "F895C7": "Samsung",
    "00A0D6": "Samsung", "001F3F": "Samsung", "002566": "Samsung",
    "78CA39": "Samsung", "E4BEED": "Samsung",
    "8CEC4B": "Huawei", "483B38": "Huawei", "7061AE": "Huawei",
    "CC2D1B": "Huawei", "E894F6": "Huawei", "A088C2": "Huawei",
    "20A6CD": "Huawei", "B4FBE4": "Huawei", "00E08F": "Huawei",
    "C8B25A": "Huawei", "881FAA": "Huawei",
    "9C99A0": "Xiaomi", "C86F9D": "Xiaomi", "F0B4D2": "Xiaomi",
    "788B2A": "Xiaomi", "50EC50": "Xiaomi", "DC2C26": "Xiaomi",
    "28E31F": "Xiaomi", "6C9462": "Xiaomi",
    "50C7BF": "TP-Link", "9CA2F4": "TP-Link", "B0A7B9": "TP-Link",
    "6032B1": "TP-Link", "EC172F": "TP-Link", "5C628B": "TP-Link",
    "A842A1": "TP-Link", "C006C3": "TP-Link", "F8111D": "TP-Link",
    "1027F5": "TP-Link", "BC7670": "TP-Link",
    "001195": "D-Link", "000D88": "D-Link", "001346": "D-Link",
    "0050BA": "D-Link", "000784": "D-Link", "001CF6": "D-Link",
    "B8AC6F": "D-Link", "5CF7E6": "D-Link",
    "00095B": "Netgear", "001B2F": "Netgear", "008EF2": "Netgear",
    "A42B8C": "Netgear", "C43DC0": "Netgear", "9C3DCF": "Netgear",
    "6038E0": "Netgear", "E046EA": "Netgear", "24B2DE": "Netgear",
    "00000C": "Cisco", "001013": "Cisco", "001225": "Cisco",
    "001B54": "Cisco", "00216A": "Cisco", "0022BD": "Cisco",
    "00255D": "Cisco", "0030F2": "Cisco", "F4CFE2": "Cisco",
    "5C5A4E": "Cisco", "68BDAB": "Cisco", "A41937": "Cisco",
    "001111": "Intel", "0020AF": "Intel", "0022FA": "Intel",
    "00902B": "Intel", "5882A8": "Intel", "B4D5BD": "Intel",
    "7C67A8": "Intel", "3C970E": "Intel", "F46B8C": "Intel",
    "00E04C": "Realtek", "525400": "Realtek", "B4B517": "Realtek",
    "8C891A": "Realtek", "E8231A": "Realtek",
    "001018": "Broadcom", "002128": "Broadcom", "001BD3": "Broadcom",
    "0023AE": "Broadcom", "A0D396": "Broadcom",
    "005056": "VMware", "000C29": "VMware", "000569": "VMware", "001AA0": "VMware",
    "001DD8": "Microsoft", "002675": "Microsoft", "7CFD22": "Microsoft",
    "281822": "Microsoft",
    "001422": "Dell", "001B78": "Dell", "F8BC12": "Dell", "B88303": "Dell",
    "001C11": "HP", "0024E8": "HP", "3C219F": "HP", "C4346B": "HP",
    "18A905": "HP", "2C41A1": "HP", "34E4D2": "HPE",
    "001DE0": "Lenovo", "F46D04": "Lenovo", "5C59AC": "Lenovo",
    "00E0FC": "Qualcomm", "A0F6FD": "Qualcomm", "D4619D": "Qualcomm", "24F5A2": "Qualcomm",
    "00C0E0": "MediaTek", "4C11BF": "MediaTek", "806AB0": "MediaTek", "C46E1F": "MediaTek",
    "240AC4": "Espressif", "30AEA4": "Espressif", "BCDDC2": "Espressif",
    "18FE34": "Espressif", "A4CF12": "Espressif",
    "B827EB": "Raspberry Pi", "DCA632": "Raspberry Pi", "E45F01": "Raspberry Pi",
    "00A040": "Sony", "001F83": "Sony", "5C969D": "Sony",
    "001CBF": "LG", "A8E544": "LG", "E89EB0": "LG",
    "00DBAF": "Ubiquiti", "0418D6": "Ubiquiti", "24A43E": "Ubiquiti",
    "FC9398": "Ubiquiti", "788A20": "Ubiquiti",
    "0015BD": "MikroTik", "4C5E6C": "MikroTik", "D4CA6D": "MikroTik",
    "3C5A3C": "Google", "A4C093": "Google", "F8F1B6": "Google",
    "54D46B": "Google", "7C11BE": "Google",
    "40B4CD": "Amazon", "747548": "Amazon", "FCA183": "Amazon",
    "A40138": "Amazon", "F8D111": "Amazon",
    "00405C": "NVIDIA", "9C6B2E": "NVIDIA",
    "8C8401": "ZTE", "C88E3E": "ZTE", "E4C22A": "ZTE",
    "6C72D9": "OPPO", "5CF7E6": "OPPO", "B4FBE4": "OPPO",
    "C86F9D": "vivo", "9888BA": "vivo",
    "001E8C": "ASUS", "04D4C4": "ASUS", "1CBFCE": "ASUS", "60A40C": "ASUS", "B06EBF": "ASUS",
    "000585": "Juniper", "00A06E": "Juniper",
    "704C3C": "Fortinet",
    "0019A6": "Aruba(HPE)", "24DE80": "Aruba(HPE)",
    "0025A0": "Motorola",
    "DC2C26": "Shenzhen IoT",
}

# ──────────────── Port Constants ────────────────
COMMON_PORTS = [
    20, 21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445,
    465, 587, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900,
    6379, 8080, 8443, 8888, 9200, 27017, 5000
]
PORT_NAMES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS", 143: "IMAP",
    443: "HTTPS", 445: "SMB", 3306: "MySQL", 3389: "RDP",
    5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB"
}

# ──────────────── Theme Colors ────────────────
BG_SILVER = [0.753, 0.753, 0.753, 1]      # #c0c0c0 classic silver
NAVY = [0, 0, 0.502, 1]                    # #000080 navy blue
GREEN_ONLINE = [0.18, 0.78, 0.18, 1]      # online indicator
GRAY_OFFLINE = [0.55, 0.55, 0.55, 1]      # offline indicator
DARK_TEXT = [0.15, 0.15, 0.15, 1]         # primary text
MID_TEXT = [0.35, 0.35, 0.35, 1]          # secondary text
WHITE_HIGHLIGHT = [1, 1, 1, 1]
BLACK_SHADOW = [0, 0, 0, 1]
GRAY_SHADOW = [0.5, 0.5, 0.5, 1]


# ════════════════════════════════════════════════════
#                   SCANNER LOGIC
# ════════════════════════════════════════════════════

class LanScanner:
    """Core LAN scanning logic — all network operations run in threads."""

    def __init__(self):
        self.devices = {}
        self.scan_active = False
        self.progress_cb = None   # called via Clock: (progress, phase, dt)
        self.result_cb = None     # called via Clock: (devices_list, progress, phase, dt)
        self.complete_cb = None   # called via Clock: (devices_list, dt)

    # ── Ping ──
    def ping_host(self, ip):
        """Ping single host. Android: ping -c 1 -W 1 IP"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3
            )
            return result.returncode == 0
        except Exception:
            return False

    # ── ARP Table ──
    def read_arp_table(self):
        """Read ARP table — /proc/net/arp first, then ip neigh show."""
        arp = {}
        # Method 1: /proc/net/arp
        try:
            with open('/proc/net/arp', 'r') as f:
                for line in f:
                    m = re.match(
                        r'(\d+\.\d+\.\d+\.\d+)\s+\S+\s+\S+\s+([0-9a-fA-F:]{17})\s',
                        line
                    )
                    if m:
                        ip_addr, mac = m.group(1), m.group(2).upper()
                        if mac != '00:00:00:00:00:00':
                            arp[ip_addr] = mac
        except Exception:
            pass
        # Method 2: ip neigh show
        if len(arp) < 3:
            try:
                result = subprocess.run(
                    ['ip', 'neigh', 'show'],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    parts = line.strip().split()
                    if not parts:
                        continue
                    ip_addr = parts[0]
                    mac = ''
                    # Find MAC: look for lladdr keyword or MAC-format string
                    for i, p in enumerate(parts):
                        if p == 'lladdr' and i + 1 < len(parts):
                            mac = parts[i + 1].upper()
                            break
                    if not mac:
                        for p in parts:
                            if re.match(
                                r'^[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:'
                                r'[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}$',
                                p
                            ):
                                mac = p.upper()
                                break
                    if ip_addr and mac and mac != '00:00:00:00:00:00':
                        arp[ip_addr] = mac
            except Exception:
                pass
        return arp

    # ── DNS ──
    def resolve_hostname(self, ip):
        """Reverse DNS lookup via socket.gethostbyaddr."""
        try:
            name = socket.gethostbyaddr(ip)[0]
            return name
        except Exception:
            return ''

    # ── OUI ──
    def lookup_vendor(self, mac):
        """Look up vendor from MAC OUI prefix."""
        if not mac or mac == 'Unknown':
            return 'Unknown'
        oui = mac.replace(':', '').upper()[:6]
        return OUI_DICT.get(oui, 'Unknown')

    # ── Port Scan ──
    def scan_port(self, ip, port, timeout=1.0):
        """Scan a single TCP port."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            s.close()
            return port if result == 0 else None
        except Exception:
            return None

    # ── Connection Type ──
    def get_connection_type(self):
        """Detect WiFi / Mobile Data / Wired from default route interface."""
        try:
            result = subprocess.run(
                ['ip', 'route', 'show', 'default'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split()
                # Format: default via X.X.X.X dev IFACE ...
                for i, p in enumerate(parts):
                    if p == 'dev' and i + 1 < len(parts):
                        iface = parts[i + 1]
                        if 'wlan' in iface or 'wifi' in iface:
                            return 'WiFi'
                        elif 'rmnet' in iface or 'ccmni' in iface:
                            return 'Mobile Data'
                        elif 'eth' in iface:
                            return 'Wired'
                        else:
                            return iface
        except Exception:
            pass
        return 'Unknown'

    # ── Local IP ──
    def get_local_ip(self):
        """Get local IP by UDP connect trick."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '127.0.0.1'

    # ── Main Scan ──
    def start_scan(self, subnet, resolve_names=True, scan_ports=True):
        """Full scan workflow: ping → ARP → DNS → ports."""
        self.devices = {}
        self.scan_active = True

        # ── Phase 1: Ping Sweep (40% progress) ──
        total = 254
        alive_hosts = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = {}
            for i in range(1, 255):
                ip = f"{subnet}.{i}"
                fut = executor.submit(self.ping_host, ip)
                futures[fut] = ip

            done_count = 0
            for fut in concurrent.futures.as_completed(futures):
                if not self.scan_active:
                    executor.shutdown(wait=False)
                    break
                ip = futures[fut]
                try:
                    alive = fut.result()
                except Exception:
                    alive = False
                done_count += 1
                progress = done_count / total * 0.4

                if alive:
                    alive_hosts.append(ip)
                    self.devices[ip] = {
                        'ip': ip,
                        'mac': 'Unknown',
                        'vendor': 'Unknown',
                        'hostname': '',
                        'name': '',
                        'notes': '',
                        'ports': {},
                        'last_seen': datetime.now().strftime('%H:%M:%S'),
                        'is_online': True,
                    }
                    if self.result_cb:
                        Clock.schedule_once(
                            partial(self.result_cb,
                                    list(self.devices.values()), progress, 'Ping Scan')
                        )
                if self.progress_cb:
                    Clock.schedule_once(
                        partial(self.progress_cb, progress,
                                f'Ping: {done_count}/{total}')
                    )

        if not self.scan_active:
            return

        # ── Phase 2: ARP Table (10% progress) ──
        if alive_hosts:
            arp = self.read_arp_table()
            for ip in alive_hosts:
                if ip in arp:
                    self.devices[ip]['mac'] = arp[ip]
                    self.devices[ip]['vendor'] = self.lookup_vendor(arp[ip])
            progress = 0.50
            if self.result_cb:
                Clock.schedule_once(
                    partial(self.result_cb,
                            list(self.devices.values()), progress, 'ARP Lookup')
                )
            if self.progress_cb:
                Clock.schedule_once(
                    partial(self.progress_cb, 0.50, 'ARP Lookup')
                )

        if not self.scan_active:
            return

        # ── Phase 3: DNS Resolution (20% progress) ──
        if resolve_names and alive_hosts:
            total_dns = len(alive_hosts)
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                futures = {
                    executor.submit(self.resolve_hostname, ip): ip
                    for ip in alive_hosts
                }
                done_dns = 0
                for fut in concurrent.futures.as_completed(futures):
                    if not self.scan_active:
                        executor.shutdown(wait=False)
                        break
                    ip = futures[fut]
                    try:
                        hostname = fut.result()
                    except Exception:
                        hostname = ''
                    done_dns += 1
                    if hostname and ip in self.devices:
                        self.devices[ip]['hostname'] = hostname
                    progress = 0.50 + done_dns / total_dns * 0.20
                    if self.result_cb:
                        Clock.schedule_once(
                            partial(self.result_cb,
                                    list(self.devices.values()), progress,
                                    'DNS Resolution')
                        )
                    if self.progress_cb:
                        Clock.schedule_once(
                            partial(self.progress_cb, progress,
                                    f'DNS: {done_dns}/{total_dns}')
                        )

        if not self.scan_active:
            return

        # ── Phase 4: Port Scan (30% progress) ──
        if scan_ports and alive_hosts:
            total_ports = len(alive_hosts) * len(COMMON_PORTS)
            scanned = 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                futures = {}
                for ip in alive_hosts:
                    for port in COMMON_PORTS:
                        fut = executor.submit(self.scan_port, ip, port)
                        futures[fut] = (ip, port)

                for fut in concurrent.futures.as_completed(futures):
                    if not self.scan_active:
                        executor.shutdown(wait=False)
                        break
                    ip, port = futures[fut]
                    try:
                        result = fut.result()
                    except Exception:
                        result = None
                    scanned += 1
                    if result and ip in self.devices:
                        pname = PORT_NAMES.get(port, str(port))
                        self.devices[ip]['ports'][port] = pname
                    progress = 0.70 + scanned / total_ports * 0.30
                    if scanned % 15 == 0 or scanned == total_ports:
                        if self.result_cb:
                            Clock.schedule_once(
                                partial(self.result_cb,
                                        list(self.devices.values()), progress,
                                        'Port Scan')
                            )
                        if self.progress_cb:
                            Clock.schedule_once(
                                partial(self.progress_cb, progress,
                                        f'Ports: {scanned}/{total_ports}')
                            )

        # ── Scan Complete ──
        self.scan_active = False
        if self.complete_cb:
            Clock.schedule_once(
                partial(self.complete_cb, list(self.devices.values()))
            )


# ════════════════════════════════════════════════════
#                  UI WIDGETS
# ════════════════════════════════════════════════════

class RetroButton(Button):
    """Classic Win9x 3D raised button with silver background."""

    btn_highlight = ListProperty(WHITE_HIGHLIGHT)
    btn_shadow = ListProperty(BLACK_SHADOW)
    btn_fill = ListProperty(BG_SILVER)

    def __init__(self, **kwargs):
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        kwargs.setdefault('background_color', [0, 0, 0, 0])
        kwargs.setdefault('color', NAVY)
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, state=self._redraw)
        self._redraw()

    def _redraw(self, *_args):
        self.canvas.before.clear()
        x, y = self.pos
        w, h = self.size
        bw = dp(2)

        with self.canvas.before:
            # Main fill
            Color(*self.btn_fill)
            Rectangle(pos=self.pos, size=self.size)

            if self.state == 'normal':
                # 3D raised: white highlight top+left, dark shadow bottom+right
                Color(*self.btn_highlight)
                Rectangle(pos=(x, y + h - bw), size=(w, bw))      # top
                Rectangle(pos=(x, y + bw), size=(bw, h - bw))     # left
                Color(*self.btn_shadow)
                Rectangle(pos=(x, y), size=(w, bw))                # bottom
                Rectangle(pos=(x + w - bw, y), size=(bw, h))      # right
            else:
                # 3D sunken: reversed
                Color(*self.btn_shadow)
                Rectangle(pos=(x, y + h - bw), size=(w, bw))      # top
                Rectangle(pos=(x, y + bw), size=(bw, h - bw))     # left
                Color(*self.btn_highlight)
                Rectangle(pos=(x, y), size=(w, bw))                # bottom
                Rectangle(pos=(x + w - bw, y), size=(bw, h))      # right
                # Darker fill when pressed
                Color(0.70, 0.70, 0.70, 1)
                Rectangle(pos=(x + bw, y + bw),
                          size=(w - 2 * bw, h - 2 * bw))


class DeviceRow(RecycleDataViewBehavior, BoxLayout):
    """RecycleView row for a single device — 2-line display."""
    index = NumericProperty(0)
    line1 = StringProperty('')
    line2 = StringProperty('')
    status_color = ListProperty(GREEN_ONLINE)
    device_ref = ObjectProperty(None, allownone=True)
    is_selected = BooleanProperty(False)
    _touch_start = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(56)
        self.padding = [dp(6), dp(2)]

        # First line: IP | MAC | Vendor | Status
        self._label1 = Label(
            text='', font_size=sp(11), color=GREEN_ONLINE,
            halign='left', valign='middle', size_hint_y=0.55,
            text_size=(None, None),
        )
        self._label1.bind(size=self._label1.setter('text_size'))

        # Second line: Name | Ports | Last Seen
        self._label2 = Label(
            text='', font_size=sp(9), color=MID_TEXT,
            halign='left', valign='middle', size_hint_y=0.45,
            text_size=(None, None),
        )
        self._label2.bind(size=self._label2.setter('text_size'))

        self.add_widget(self._label1)
        self.add_widget(self._label2)

        self.bind(pos=self._update_bg, size=self._update_bg,
                  is_selected=self._update_bg)
        self._update_bg()

    # Property change handlers
    def on_line1(self, _inst, val):
        self._label1.text = val

    def on_line2(self, _inst, val):
        self._label2.text = val

    def on_status_color(self, _inst, val):
        self._label1.color = val

    def refresh_view_attrs(self, rv, index, data):
        """Called by RecycleView when data changes."""
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    # Background drawing (silver default, navy when selected)
    def _update_bg(self, *_args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_selected:
                Color(*NAVY)
            else:
                Color(*BG_SILVER)
            Rectangle(pos=self.pos, size=self.size)

    # Touch handling — click vs long-press
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_start = time.time()
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            elapsed = time.time() - self._touch_start
            app = App.get_running_app()
            ui = app.root
            if elapsed < 0.5:
                # Short click — detail / edit popup
                if self.device_ref:
                    ui.show_device_detail(self.device_ref)
            else:
                # Long press — action menu popup
                if self.device_ref:
                    ui.show_action_menu(self.device_ref)
            return True
        return super().on_touch_up(touch)


# ════════════════════════════════════════════════════
#                  MAIN UI LAYOUT
# ════════════════════════════════════════════════════

class LanScannerUI(BoxLayout):
    """Root widget — full app UI with retro Win9x styling."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [dp(4)]
        self.spacing = dp(2)

        # Data
        self.scanner = LanScanner()
        self.devices = []
        self.filtered_devices = []
        self.scan_running = False

        # ─── Top Bar ───
        top_bar = BoxLayout(orientation='vertical',
                            size_hint_y=0.14, spacing=dp(2))

        # Row 1: Subnet + Scan button
        row1 = BoxLayout(orientation='horizontal',
                         size_hint_y=0.55, spacing=dp(4))
        self.subnet_input = TextInput(
            text=self._default_subnet(),
            hint_text='Subnet (e.g. 192.168.1)',
            size_hint_x=0.55, multiline=False,
            font_size=sp(13),
            background_color=BG_SILVER,
            foreground_color=DARK_TEXT,
            padding=[dp(6), dp(4), dp(6), dp(4)],
        )
        self.scan_btn = RetroButton(
            text='Start Scan', size_hint_x=0.45,
            font_size=sp(13),
        )
        self.scan_btn.bind(on_release=self._on_scan_btn)
        row1.add_widget(self.subnet_input)
        row1.add_widget(self.scan_btn)

        # Row 2: Checkboxes
        row2 = BoxLayout(orientation='horizontal',
                         size_hint_y=0.45, spacing=dp(6))

        cb_left = BoxLayout(orientation='horizontal', size_hint_x=0.5)
        self.resolve_cb = CheckBox(active=True, size_hint_x=0.2)
        resolve_lbl = Label(text='Resolve Names', font_size=sp(10),
                            color=DARK_TEXT, halign='left', size_hint_x=0.8)
        resolve_lbl.bind(size=resolve_lbl.setter('text_size'))
        cb_left.add_widget(self.resolve_cb)
        cb_left.add_widget(resolve_lbl)

        cb_right = BoxLayout(orientation='horizontal', size_hint_x=0.5)
        self.port_cb = CheckBox(active=True, size_hint_x=0.2)
        port_lbl = Label(text='Scan Ports', font_size=sp(10),
                         color=DARK_TEXT, halign='left', size_hint_x=0.8)
        port_lbl.bind(size=port_lbl.setter('text_size'))
        cb_right.add_widget(self.port_cb)
        cb_right.add_widget(port_lbl)

        row2.add_widget(cb_left)
        row2.add_widget(cb_right)

        top_bar.add_widget(row1)
        top_bar.add_widget(row2)
        self.add_widget(top_bar)

        # ─── Search Bar ───
        search_bar = BoxLayout(orientation='horizontal',
                               size_hint_y=0.05, spacing=dp(4))
        self.search_input = TextInput(
            hint_text='Search filter (IP/MAC/vendor/name)...',
            multiline=False, font_size=sp(11),
            background_color=BG_SILVER,
            foreground_color=DARK_TEXT,
            padding=[dp(6), dp(2), dp(6), dp(2)],
        )
        self.search_input.bind(text=self._on_search_change)
        search_bar.add_widget(self.search_input)
        self.add_widget(search_bar)

        # ─── Toolbar ───
        toolbar = BoxLayout(orientation='horizontal',
                            size_hint_y=0.06, spacing=dp(2))
        self.save_btn = RetroButton(text='Save', font_size=sp(10),
                                    size_hint_x=0.25)
        self.load_btn = RetroButton(text='Load', font_size=sp(10),
                                    size_hint_x=0.25)
        self.export_btn = RetroButton(text='Export', font_size=sp(10),
                                      size_hint_x=0.25)
        self.clear_btn = RetroButton(text='Clear', font_size=sp(10),
                                     size_hint_x=0.25)
        self.save_btn.bind(on_release=lambda _i: self.show_save_popup())
        self.load_btn.bind(on_release=lambda _i: self.show_load_popup())
        self.export_btn.bind(on_release=lambda _i: self.show_export_popup())
        self.clear_btn.bind(on_release=lambda _i: self._clear_all())
        toolbar.add_widget(self.save_btn)
        toolbar.add_widget(self.load_btn)
        toolbar.add_widget(self.export_btn)
        toolbar.add_widget(self.clear_btn)
        self.add_widget(toolbar)

        # ─── Device List (RecycleView) ───
        self.device_rv = RecycleView(size_hint_y=0.66)
        self.device_rv.viewclass = DeviceRow
        layout_mgr = RecycleBoxLayout(
            orientation='vertical',
            default_size=(None, dp(56)),
            default_size_hint=(1, None),
            key_size='view_size',
        )
        self.device_rv.layout_manager = layout_mgr
        self.device_rv.data = []
        self.add_widget(self.device_rv)

        # ─── Bottom Bar ───
        bottom = BoxLayout(orientation='horizontal',
                           size_hint_y=0.09, spacing=dp(4))
        self.status_label = Label(
            text='Ready | Connection: Unknown',
            font_size=sp(9), color=DARK_TEXT,
            halign='left', valign='middle',
            size_hint_x=0.6,
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.progress_bar = ProgressBar(
            max=1.0, value=0.0,
            size_hint_x=0.4,
        )
        bottom.add_widget(self.status_label)
        bottom.add_widget(self.progress_bar)
        self.add_widget(bottom)

        # Initial status
        Clock.schedule_once(self._refresh_status, 0.5)

    # ── Helpers ──
    def _default_subnet(self):
        local_ip = self.scanner.get_local_ip()
        parts = local_ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}"
        return '192.168.1'

    def _refresh_status(self, _dt=0):
        conn = self.scanner.get_connection_type()
        total = len(self.devices)
        online = sum(1 for d in self.devices if d.get('is_online'))
        self.status_label.text = f'{conn} | Devices: {total} | Online: {online}'

    # ── Scan Button ──
    def _on_scan_btn(self, _instance):
        if self.scan_running:
            self._stop_scan()
        else:
            self._start_scan()

    def _start_scan(self):
        subnet = self.subnet_input.text.strip()
        parts = subnet.split('.')
        if len(parts) != 3 or not all(
            p.isdigit() and 0 <= int(p) <= 255 for p in parts
        ):
            self._show_info_popup('Invalid subnet! Use format: 192.168.1')
            return

        self.devices = []
        self.filtered_devices = []
        self.device_rv.data = []
        self.scan_running = True
        self.scan_btn.text = 'Stop Scan'
        self.progress_bar.value = 0.0

        self.scanner.progress_cb = self._on_progress
        self.scanner.result_cb = self._on_result
        self.scanner.complete_cb = self._on_complete

        resolve = self.resolve_cb.active
        ports = self.port_cb.active

        thread = threading.Thread(
            target=self.scanner.start_scan,
            args=(subnet, resolve, ports),
            daemon=True
        )
        thread.start()

    def _stop_scan(self):
        self.scanner.scan_active = False
        self.scan_running = False
        self.scan_btn.text = 'Start Scan'
        self.status_label.text = 'Scan stopped'
        self.progress_bar.value = 0.0

    # ── Scan Callbacks (called on main thread via Clock) ──
    def _on_progress(self, progress, phase, _dt=0):
        self.progress_bar.value = progress
        self.status_label.text = phase

    def _on_result(self, devices, progress, phase, _dt=0):
        self.devices = devices
        self._apply_filter()

    def _on_complete(self, devices, _dt=0):
        self.devices = devices
        self._apply_filter()
        self.scan_running = False
        self.scan_btn.text = 'Start Scan'
        self.progress_bar.value = 1.0
        self._refresh_status()

    # ── Search / Filter ──
    def _on_search_change(self, _instance, value):
        self._apply_filter()

    def _apply_filter(self):
        search = self.search_input.text.strip().lower()
        if search:
            self.filtered_devices = [
                d for d in self.devices if
                search in d['ip'].lower() or
                search in d['mac'].lower() or
                search in d['vendor'].lower() or
                search in (d.get('name') or '').lower() or
                search in (d.get('hostname') or '').lower() or
                search in (d.get('notes') or '').lower()
            ]
        else:
            self.filtered_devices = list(self.devices)
        self._update_device_list()
        self._refresh_status()

    def _update_device_list(self):
        data = []
        for d in self.filtered_devices:
            port_keys = sorted(d.get('ports', {}).keys())
            port_short = ','.join(str(p) for p in port_keys[:5])
            if len(port_keys) > 5:
                port_short += '...'
            status_icon = '\u25cf' if d.get('is_online') else '\u25cb'
            name_display = d.get('name') or d.get('hostname') or 'Unknown'
            line1 = f"{d['ip']}  {d['mac']}  {d['vendor']}  {status_icon}"
            line2 = f"{name_display}  {port_short or 'No ports'}  {d.get('last_seen', '')}"
            sc = GREEN_ONLINE if d.get('is_online') else GRAY_OFFLINE
            data.append({
                'line1': line1,
                'line2': line2,
                'status_color': sc,
                'device_ref': d,
                'view_size': dp(56),
            })
        self.device_rv.data = data

    # ── Popup: Device Detail / Edit ──
    def show_device_detail(self, device):
        content = BoxLayout(orientation='vertical', spacing=dp(4),
                            padding=[dp(10), dp(8)])
        # Info section
        ports_full = ', '.join(
            f"{p}({n})" for p, n in sorted(device.get('ports', {}).items())
        ) or 'No open ports found'
        info = (
            f"IP: {device['ip']}\n"
            f"MAC: {device['mac']}\n"
            f"Vendor: {device['vendor']}\n"
            f"Hostname: {device.get('hostname', '')}\n"
            f"Ports: {ports_full}\n"
            f"Last Seen: {device.get('last_seen', '')}\n"
            f"Status: {'Online' if device.get('is_online') else 'Offline'}"
        )
        info_lbl = Label(text=info, font_size=sp(10), color=DARK_TEXT,
                         halign='left', valign='top', size_hint_y=0.45)
        info_lbl.bind(size=info_lbl.setter('text_size'))
        content.add_widget(info_lbl)

        # Edit section
        name_lbl = Label(text='Custom Name:', font_size=sp(9),
                         color=DARK_TEXT, size_hint_y=0.06,
                         halign='left')
        name_lbl.bind(size=name_lbl.setter('text_size'))
        content.add_widget(name_lbl)
        name_input = TextInput(
            text=device.get('name', ''), hint_text='Enter custom name',
            multiline=False, font_size=sp(11),
            background_color=BG_SILVER, foreground_color=DARK_TEXT,
            size_hint_y=0.08,
        )
        content.add_widget(name_input)

        notes_lbl = Label(text='Notes:', font_size=sp(9),
                          color=DARK_TEXT, size_hint_y=0.06,
                          halign='left')
        notes_lbl.bind(size=notes_lbl.setter('text_size'))
        content.add_widget(notes_lbl)
        notes_input = TextInput(
            text=device.get('notes', ''), hint_text='Enter notes',
            multiline=True, font_size=sp(10),
            background_color=BG_SILVER, foreground_color=DARK_TEXT,
            size_hint_y=0.18,
        )
        content.add_widget(notes_input)

        # Buttons
        btn_row = BoxLayout(orientation='horizontal',
                            size_hint_y=0.12, spacing=dp(4))
        save_btn = RetroButton(text='Save Changes', font_size=sp(11))
        close_btn = RetroButton(text='Close', font_size=sp(11))
        btn_row.add_widget(save_btn)
        btn_row.add_widget(close_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title=f'Device: {device["ip"]}',
            content=content,
            size_hint=(0.92, 0.85),
            background_color=BG_SILVER,
            separator_color=NAVY,
            title_color=WHITE_HIGHLIGHT,
        )

        def do_save(_inst):
            device['name'] = name_input.text.strip()
            device['notes'] = notes_input.text.strip()
            self._apply_filter()
            popup.dismiss()

        def do_close(_inst):
            popup.dismiss()

        save_btn.bind(on_release=do_save)
        close_btn.bind(on_release=do_close)
        popup.open()

    # ── Popup: Action Menu (Long Press) ──
    def show_action_menu(self, device):
        content = BoxLayout(orientation='vertical', spacing=dp(8),
                            padding=[dp(10), dp(8)])
        del_btn = RetroButton(text='Delete This Device', font_size=sp(12))
        clear_btn = RetroButton(text='Clear All Devices', font_size=sp(12))
        cancel_btn = RetroButton(text='Cancel', font_size=sp(12))
        content.add_widget(del_btn)
        content.add_widget(clear_btn)
        content.add_widget(cancel_btn)

        popup = Popup(
            title='Actions',
            content=content,
            size_hint=(0.75, 0.45),
            background_color=BG_SILVER,
            separator_color=NAVY,
            title_color=WHITE_HIGHLIGHT,
        )

        def do_delete(_inst):
            self.devices = [d for d in self.devices if d is not device]
            self._apply_filter()
            popup.dismiss()

        def do_clear(_inst):
            self._clear_all()
            popup.dismiss()

        def do_cancel(_inst):
            popup.dismiss()

        del_btn.bind(on_release=do_delete)
        clear_btn.bind(on_release=do_clear)
        cancel_btn.bind(on_release=do_cancel)
        popup.open()

    # ── Clear All ──
    def _clear_all(self):
        self.devices = []
        self.filtered_devices = []
        self.device_rv.data = []
        self._refresh_status()

    # ── Info Popup ──
    def _show_info_popup(self, message):
        content = BoxLayout(orientation='vertical', spacing=dp(8),
                            padding=[dp(10), dp(8)])
        msg_lbl = Label(text=message, font_size=sp(12), color=DARK_TEXT)
        content.add_widget(msg_lbl)
        ok_btn = RetroButton(text='OK', font_size=sp(12),
                             size_hint_y=0.3)
        content.add_widget(ok_btn)

        popup = Popup(title='Info', content=content,
                      size_hint=(0.8, 0.4),
                      background_color=BG_SILVER,
                      separator_color=NAVY,
                      title_color=WHITE_HIGHLIGHT)

        ok_btn.bind(on_release=lambda _i: popup.dismiss())
        popup.open()

    # ── Save Popup ──
    def show_save_popup(self):
        content = BoxLayout(orientation='vertical', spacing=dp(4),
                            padding=[dp(10), dp(8)])
        lbl = Label(text='Save devices to JSON file:', font_size=sp(10),
                    color=DARK_TEXT, size_hint_y=0.1, halign='left')
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)
        default_path = self._default_save_path() + 'lan_scan.json'
        path_input = TextInput(
            text=default_path, multiline=False, font_size=sp(10),
            background_color=BG_SILVER, foreground_color=DARK_TEXT,
            size_hint_y=0.15,
        )
        content.add_widget(path_input)

        btn_row = BoxLayout(orientation='horizontal',
                            size_hint_y=0.15, spacing=dp(4))
        save_btn = RetroButton(text='Save', font_size=sp(11))
        cancel_btn = RetroButton(text='Cancel', font_size=sp(11))
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(title='Save Devices', content=content,
                      size_hint=(0.9, 0.45),
                      background_color=BG_SILVER,
                      separator_color=NAVY,
                      title_color=WHITE_HIGHLIGHT)

        def do_save(_inst):
            self._save_json(path_input.text.strip())
            popup.dismiss()

        def do_cancel(_inst):
            popup.dismiss()

        save_btn.bind(on_release=do_save)
        cancel_btn.bind(on_release=do_cancel)
        popup.open()

    # ── Load Popup ──
    def show_load_popup(self):
        content = BoxLayout(orientation='vertical', spacing=dp(4),
                            padding=[dp(10), dp(8)])
        lbl = Label(text='Load devices from JSON file:', font_size=sp(10),
                    color=DARK_TEXT, size_hint_y=0.1, halign='left')
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)
        default_path = self._default_save_path() + 'lan_scan.json'
        path_input = TextInput(
            text=default_path, multiline=False, font_size=sp(10),
            background_color=BG_SILVER, foreground_color=DARK_TEXT,
            size_hint_y=0.15,
        )
        content.add_widget(path_input)

        btn_row = BoxLayout(orientation='horizontal',
                            size_hint_y=0.15, spacing=dp(4))
        load_btn = RetroButton(text='Load', font_size=sp(11))
        cancel_btn = RetroButton(text='Cancel', font_size=sp(11))
        btn_row.add_widget(load_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(title='Load Devices', content=content,
                      size_hint=(0.9, 0.45),
                      background_color=BG_SILVER,
                      separator_color=NAVY,
                      title_color=WHITE_HIGHLIGHT)

        def do_load(_inst):
            self._load_json(path_input.text.strip())
            popup.dismiss()

        def do_cancel(_inst):
            popup.dismiss()

        load_btn.bind(on_release=do_load)
        cancel_btn.bind(on_release=do_cancel)
        popup.open()

    # ── Export Popup ──
    def show_export_popup(self):
        content = BoxLayout(orientation='vertical', spacing=dp(4),
                            padding=[dp(10), dp(8)])
        lbl = Label(text='Export format:', font_size=sp(10),
                    color=DARK_TEXT, size_hint_y=0.1, halign='left')
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)

        fmt_row = BoxLayout(orientation='horizontal',
                            size_hint_y=0.15, spacing=dp(4))
        json_btn = RetroButton(text='JSON', font_size=sp(11))
        csv_btn = RetroButton(text='CSV', font_size=sp(11))
        fmt_row.add_widget(json_btn)
        fmt_row.add_widget(csv_btn)
        content.add_widget(fmt_row)

        path_lbl = Label(text='File path:', font_size=sp(9),
                         color=DARK_TEXT, size_hint_y=0.08, halign='left')
        path_lbl.bind(size=path_lbl.setter('text_size'))
        content.add_widget(path_lbl)
        default_path = self._default_save_path() + 'lan_scan_export'
        path_input = TextInput(
            text=default_path, multiline=False, font_size=sp(10),
            background_color=BG_SILVER, foreground_color=DARK_TEXT,
            size_hint_y=0.15,
        )
        content.add_widget(path_input)

        btn_row = BoxLayout(orientation='horizontal',
                            size_hint_y=0.15, spacing=dp(4))
        export_btn = RetroButton(text='Export', font_size=sp(11))
        cancel_btn = RetroButton(text='Cancel', font_size=sp(11))
        btn_row.add_widget(export_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(title='Export Devices', content=content,
                      size_hint=(0.9, 0.55),
                      background_color=BG_SILVER,
                      separator_color=NAVY,
                      title_color=WHITE_HIGHLIGHT)

        chosen_format = ['json']

        def pick_json(_inst):
            chosen_format[0] = 'json'
            json_btn.btn_fill = [0.6, 0.8, 0.6, 1]
            csv_btn.btn_fill = BG_SILVER
            json_btn._redraw()
            csv_btn._redraw()

        def pick_csv(_inst):
            chosen_format[0] = 'csv'
            csv_btn.btn_fill = [0.6, 0.8, 0.6, 1]
            json_btn.btn_fill = BG_SILVER
            csv_btn._redraw()
            json_btn._redraw()

        json_btn.bind(on_release=pick_json)
        csv_btn.bind(on_release=pick_csv)

        def do_export(_inst):
            path = path_input.text.strip()
            if chosen_format[0] == 'json':
                self._export_json(path + '.json')
            else:
                self._export_csv(path + '.csv')
            popup.dismiss()

        def do_cancel(_inst):
            popup.dismiss()

        export_btn.bind(on_release=do_export)
        cancel_btn.bind(on_release=do_cancel)
        popup.open()

    # ── File Operations ──
    def _default_save_path(self):
        for p in ['/sdcard/', '/storage/emulated/0/',
                  os.path.expanduser('~'), os.getcwd()]:
            if os.path.isdir(p):
                return p
        return os.getcwd() + '/'

    def _save_json(self, path):
        try:
            data = []
            for d in self.devices:
                entry = dict(d)
                entry['ports'] = {str(k): v for k, v in entry.get('ports', {}).items()}
                data.append(entry)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self._show_info_popup(f'Saved {len(data)} devices to:\n{path}')
        except Exception as e:
            self._show_info_popup(f'Save error:\n{e}')

    def _load_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.devices = []
            for entry in data:
                ports = {}
                raw_ports = entry.get('ports', {})
                for k, v in raw_ports.items():
                    ports[int(k)] = v
                entry['ports'] = ports
                entry.setdefault('name', '')
                entry.setdefault('notes', '')
                entry.setdefault('is_online', False)
                entry.setdefault('last_seen', '')
                self.devices.append(entry)
            self._apply_filter()
            self._show_info_popup(f'Loaded {len(self.devices)} devices from:\n{path}')
        except Exception as e:
            self._show_info_popup(f'Load error:\n{e}')

    def _export_json(self, path):
        try:
            data = []
            for d in self.devices:
                entry = dict(d)
                entry['ports'] = {str(k): v for k, v in entry.get('ports', {}).items()}
                data.append(entry)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self._show_info_popup(f'Exported JSON to:\n{path}')
        except Exception as e:
            self._show_info_popup(f'Export error:\n{e}')

    def _export_csv(self, path):
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'IP', 'MAC', 'Vendor', 'Hostname', 'Name',
                    'Notes', 'Ports', 'Last Seen', 'Online'
                ])
                for d in self.devices:
                    ports_str = ';'.join(
                        f"{p}:{n}" for p, n in sorted(d.get('ports', {}).items())
                    )
                    writer.writerow([
                        d['ip'], d['mac'], d['vendor'],
                        d.get('hostname', ''), d.get('name', ''),
                        d.get('notes', ''), ports_str,
                        d.get('last_seen', ''),
                        d.get('is_online', False)
                    ])
            self._show_info_popup(f'Exported CSV to:\n{path}')
        except Exception as e:
            self._show_info_popup(f'Export error:\n{e}')


# ════════════════════════════════════════════════════
#                     APP CLASS
# ════════════════════════════════════════════════════

class LanScannerApp(App):
    """Kivy Application entry point — LAN Scanner (Android/Kivy)."""

    title = 'LAN Scanner'
    icon = ''  # TODO: set custom icon path if available

    def build(self):
        Window.clearcolor = (0.753, 0.753, 0.753, 1)
        return LanScannerUI()

    def on_pause(self):
        return True  # Allow app to pause on Android

    def on_resume(self):
        pass


# ════════════════════════════════════════════════════
#                    ENTRY POINT
# ════════════════════════════════════════════════════

if __name__ == '__main__':
    LanScannerApp().run()
