@echo off
chcp 65001 >nul
title ChromeDriver下载工具

echo.
echo ================================================
echo        🔧 ChromeDriver下载和安装工具
echo ================================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查requests模块
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo ❌ 缺少requests模块，正在安装...
    pip install requests
    if errorlevel 1 (
        echo ❌ requests安装失败
        pause
        exit /b 1
    )
)

echo ✅ 环境检查通过
echo.

:: 运行下载脚本
echo 🚀 开始下载ChromeDriver...
python download_chromedriver.py

echo.
echo 下载完成，按任意键退出...
pause >nul 