[app]

# (str) Title of your application
title = LAN Scanner

# (str) Package name
package.name = lanscanner

# (str) Package domain (namespace for the package)
package.domain = com.lan.scanner

# (str) Source code directory
source.dir = .

# (str) Source code includes filename patterns
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Source code excludes filename patterns
# source.exclude_exts = spec

# (str) Application versioning
version = 1.0.0

# (str) Application requirements
# kivy==2.2.0 or latest stable; ensure compatibility
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.2.0

# (str) Custom application flags
# android.allow_backup = True

# (str) Presplash animation — optional, leave blank if none
# presplash.filename = %(source.dir)s/presplash.png

# (str) Application icon — TODO: replace with actual icon file
# icon.filename = %(source.dir)s/icon.png
icon.filename =

# (str) Application orientation — support both portrait and landscape
orientation = portrait,landscape

# (bool) Fullscreen mode — 0 = not fullscreen, allow system bars
fullscreen = 0

# (str) Android platform API level — target SDK 33 (Android 13+)
android.api = 33

# (str) Android minimum API level — minSDK 21 (Android 5.0)
android.minapi = 21

# (str) Android NDK version (use r25b or compatible)
android.ndk = 25b

# (str) Android SDK version to download (if not installed)
android.sdk = 33

# (str) Android archs to build for — mainstream ARM architectures
android.archs = armeabi-v7a, arm64-v8a

# (str) Android permissions required
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE

# (str) Android entry point (main.py or custom)
android.entrypoint = lan_scanner_android.py

# (bool) Skip update check
android.skip_update = False

# (str) Android logcat filters
# android.logcat_filters = *:S python:D

# (str) Android build mode — release or debug
# android.mode = debug

# (bool) Copy Python libraries instead of symlinking
# android.copy_libs = 1

# (str) Kivy launcher mode — set to 0 for standalone APK
# android.kivy_launcher = 0

# (str) App theme (default or dark)
# android.apptheme = @android:style/Theme.NoTitleBar

# (bool) Use Android's default theme
# android.default_theme = True

# (str) Buildozer spec version
# spec.version = 1

# ────────────────────────────────────────────────
# Build configuration
# ────────────────────────────────────────────────

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug, 3 = debug+trace)
log_level = 2

# (bool) Warn on missing build dependencies
warn_on_missing = True

# (str) Build directory
# build.dir = ./.buildozer

# (str) Bin directory
# bin.dir = ./bin

# ────────────────────────────────────────────────
# iOS configuration (not used for this Android app)
# ────────────────────────────────────────────────

# [ios]
# Not applicable — this is an Android-only build
