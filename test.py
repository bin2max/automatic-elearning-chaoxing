#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超星自动化学习程序测试脚本
"""

import sys
import os

def test_imports():
    """测试导入功能"""
    print("🔍 测试模块导入...")
    
    try:
        import selenium
        print("✅ selenium 导入成功")
    except ImportError as e:
        print(f"❌ selenium 导入失败: {e}")
        return False
    
    try:
        import webdriver_manager
        print("✅ webdriver_manager 导入成功")
    except ImportError as e:
        print(f"❌ webdriver_manager 导入失败: {e}")
        return False
    
    try:
        from config import Config
        print("✅ config 模块导入成功")
    except ImportError as e:
        print(f"❌ config 模块导入失败: {e}")
        return False
    
    try:
        from chaoxing_auto_learner import ChaoxingAutoLearner
        print("✅ 主程序模块导入成功")
    except ImportError as e:
        print(f"❌ 主程序模块导入失败: {e}")
        return False
    
    return True

def test_config():
    """测试配置"""
    print("\n🔍 测试配置...")
    
    try:
        from config import Config
        
        # 检查必要配置
        required_configs = [
            'USERNAME', 'PASSWORD', 'COURSE_URL', 
            'BROWSER_HEADLESS', 'IMPLICIT_WAIT', 'PAGE_LOAD_TIMEOUT'
        ]
        
        for config_name in required_configs:
            if hasattr(Config, config_name):
                value = getattr(Config, config_name)
                if value is not None:
                    print(f"✅ {config_name}: {value if config_name != 'PASSWORD' else '***'}")
                else:
                    print(f"❌ {config_name}: 未设置")
                    return False
            else:
                print(f"❌ {config_name}: 配置缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_browser_setup():
    """测试浏览器设置（不启动浏览器）"""
    print("\n🔍 测试浏览器设置...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        # 创建Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 获取ChromeDriver路径
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver路径: {driver_path}")
        
        # 创建Service对象
        service = Service(driver_path)
        print("✅ Service对象创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 浏览器设置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("🧪 超星自动化学习程序测试")
    print("=" * 50)
    
    tests = [
        ("模块导入测试", test_imports),
        ("配置测试", test_config),
        ("浏览器设置测试", test_browser_setup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} 通过")
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 出错: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！程序可以正常运行")
        return True
    else:
        print("⚠️  部分测试失败，请检查配置和依赖")
        return False

if __name__ == "__main__":
    success = main()
    input("\n按回车键退出...")
    sys.exit(0 if success else 1) 