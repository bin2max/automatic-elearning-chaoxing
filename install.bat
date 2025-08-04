@echo off
chcp 65001 >nul
title 超星自动化学习程序 - 安装脚本

echo.
echo ================================================
echo        🎓 超星自动化学习程序安装向导
echo ================================================
echo.

:: 检查Python版本
echo 🔍 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo.
    echo 请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请勾选"Add Python to PATH"选项
    pause
    exit /b 1
)

python --version
echo ✅ Python已安装
echo.

:: 检查pip
echo 🔍 检查pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: pip未安装或不可用
    pause
    exit /b 1
)

echo ✅ pip可用
echo.

:: 升级pip
echo 🔄 升级pip到最新版本...
python -m pip install --upgrade pip
echo.

:: 安装依赖
echo 📦 安装项目依赖...
echo 这可能需要几分钟时间，请耐心等待...
echo.

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ 依赖安装失败
    echo 请检查网络连接或手动运行: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ✅ 依赖安装完成
echo.

:: 运行测试
echo 🧪 运行程序测试...
python test.py
if errorlevel 1 (
    echo.
    echo ⚠️  测试发现问题，但程序可能仍可运行
    echo 建议查看测试输出并解决问题
)

echo.
echo ================================================
echo 🎉 安装完成！
echo ================================================
echo.
echo 现在您可以：
echo 1. 双击 run.bat 运行程序
echo 2. 或在命令行运行: python run.py
echo 3. 或运行: python test.py 进行测试
echo.
echo 祝您学习愉快！🎓
echo.
pause 