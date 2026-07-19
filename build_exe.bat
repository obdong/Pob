@echo off
chcp 65001 >nul
setlocal
:: 切换到本脚本所在目录，确保能找到 lan_scanner.py
cd /d "%~dp0"

echo ============================================
echo   局域网设备扫描器 - 一键打包为 EXE
echo ============================================
echo.

echo [1/3] 检查 Python 环境 ...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python！
    echo 请先到 https://www.python.org/downloads/ 安装 Python，
    echo 安装时务必勾选 "Add Python to PATH"。
    pause
    exit /b 1
)
python --version

echo.
echo [2/3] 安装 / 更新 PyInstaller ...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo [错误] PyInstaller 安装失败，请检查网络后重试。
    pause
    exit /b 1
)

echo.
echo [3/3] 开始打包 lan_scanner.exe （--onefile --windowed，含自定义图标）...
python -m PyInstaller --onefile --windowed --name lan_scanner --icon=app.ico --add-data "app.ico;." --hidden-import tkinter --collect-all tkinter lan_scanner.py
if errorlevel 1 (
    echo [错误] 打包失败，请查看上方日志。
    pause
    exit /b 1
)

echo.
echo ============================================
echo   打包完成！生成的文件位于： dist\lan_scanner.exe
echo ============================================
pause
