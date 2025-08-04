@echo off
chcp 65001 >nul
title 超星自动化学习程序

echo.
echo ================================================
echo            🎓 超星自动化学习程序
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

:: 检查依赖是否安装
echo 正在检查依赖...
python -c "import selenium, webdriver_manager" >nul 2>&1
if errorlevel 1 (
    echo ❌ 缺少依赖，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo ✅ 依赖检查通过
echo.

:: 运行程序
echo 🚀 启动自动化学习程序...
python run.py

echo.
echo 程序已结束，按任意键退出...
pause >nul 