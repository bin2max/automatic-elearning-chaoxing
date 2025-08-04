#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromeDriver下载和安装脚本
"""

import os
import sys
import requests
import zipfile
import subprocess
import platform
from pathlib import Path

def get_chrome_version():
    """获取Chrome浏览器版本"""
    try:
        if platform.system() == "Windows":
            # Windows系统
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
        elif platform.system() == "Darwin":
            # macOS系统
            process = subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], stdout=subprocess.PIPE)
            output = process.communicate()[0].decode('utf-8')
            return output.strip().split()[-1]
        else:
            # Linux系统
            process = subprocess.Popen(['google-chrome', '--version'], stdout=subprocess.PIPE)
            output = process.communicate()[0].decode('utf-8')
            return output.strip().split()[-1]
    except Exception as e:
        print(f"获取Chrome版本失败: {e}")
        return None

def get_chromedriver_version(chrome_version):
    """根据Chrome版本获取对应的ChromeDriver版本"""
    try:
        # 提取主版本号
        major_version = chrome_version.split('.')[0]
        
        # 获取ChromeDriver版本信息
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(f"无法获取ChromeDriver版本，HTTP状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"获取ChromeDriver版本失败: {e}")
        return None

def download_chromedriver(version):
    """下载ChromeDriver"""
    try:
        # 确定系统架构
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "windows":
            if "64" in machine or "x86_64" in machine:
                platform_name = "win64"
            else:
                platform_name = "win32"
        elif system == "darwin":
            if "arm" in machine:
                platform_name = "mac_arm64"
            else:
                platform_name = "mac64"
        else:  # Linux
            if "64" in machine or "x86_64" in machine:
                platform_name = "linux64"
            else:
                platform_name = "linux32"
        
        # 构建下载URL
        url = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_{platform_name}.zip"
        
        print(f"正在下载ChromeDriver {version} for {platform_name}...")
        print(f"下载地址: {url}")
        
        # 下载文件
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # 保存文件
        zip_path = "chromedriver.zip"
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("下载完成，正在解压...")
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # 删除zip文件
        os.remove(zip_path)
        
        # 设置执行权限（Linux/macOS）
        if system != "windows":
            os.chmod("chromedriver", 0o755)
        
        print("ChromeDriver安装完成！")
        return True
        
    except Exception as e:
        print(f"下载ChromeDriver失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🔧 ChromeDriver下载和安装工具")
    print("=" * 50)
    
    # 获取Chrome版本
    print("\n🔍 检测Chrome浏览器版本...")
    chrome_version = get_chrome_version()
    
    if not chrome_version:
        print("❌ 无法检测到Chrome浏览器版本")
        print("请确保已安装Chrome浏览器")
        return False
    
    print(f"✅ 检测到Chrome版本: {chrome_version}")
    
    # 获取ChromeDriver版本
    print("\n🔍 获取对应的ChromeDriver版本...")
    driver_version = get_chromedriver_version(chrome_version)
    
    if not driver_version:
        print("❌ 无法获取对应的ChromeDriver版本")
        print("请手动下载ChromeDriver: https://chromedriver.chromium.org/")
        return False
    
    print(f"✅ 对应的ChromeDriver版本: {driver_version}")
    
    # 检查是否已存在ChromeDriver
    if os.path.exists("chromedriver") or os.path.exists("chromedriver.exe"):
        print("\n⚠️  检测到已存在的ChromeDriver")
        choice = input("是否重新下载? (y/N): ").strip().lower()
        if choice not in ['y', 'yes', '是']:
            print("跳过下载")
            return True
    
    # 下载ChromeDriver
    print("\n📥 开始下载ChromeDriver...")
    if download_chromedriver(driver_version):
        print("\n🎉 ChromeDriver安装成功！")
        print("现在可以运行超星自动化学习程序了")
        return True
    else:
        print("\n❌ ChromeDriver安装失败")
        return False

if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  操作被用户中断")
        sys.exit(1) 