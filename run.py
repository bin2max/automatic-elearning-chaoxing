#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超星自动化学习程序启动脚本
"""

import sys
import os
from chaoxing_auto_learner import ChaoxingAutoLearner

def main():
    """主函数"""
    print("=" * 50)
    print("🎓 超星自动化学习程序")
    print("=" * 50)
    print()
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    
    # 检查依赖
    try:
        import selenium
        import webdriver_manager
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    # 确认用户信息
    print("\n📋 当前配置:")
    from config import Config
    print(f"   用户名: {Config.USERNAME}")
    print(f"   课程URL: {Config.COURSE_URL[:50]}...")
    print(f"   播放速度: {Config.PLAYBACK_SPEED}")
    print(f"   无头模式: {'是' if Config.BROWSER_HEADLESS else '否'}")
    
    # 用户确认
    print("\n⚠️  重要提醒:")
    print("   1. 请确保网络连接稳定")
    print("   2. 程序运行期间请勿手动操作浏览器")
    print("   3. 如遇到验证码需要手动处理")
    print("   4. 请遵守学校的学习规定")
    
    confirm = input("\n是否继续运行程序? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("程序已取消")
        return False
    
    print("\n🚀 开始运行自动化学习程序...")
    print("-" * 50)
    
    # 运行主程序
    try:
        learner = ChaoxingAutoLearner()
        success = learner.run()
        
        if success:
            print("\n✅ 程序运行完成！")
        else:
            print("\n❌ 程序运行失败，请查看日志文件")
            
        return success
        
    except KeyboardInterrupt:
        print("\n\n⏹️  程序被用户中断")
        return False
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        return False

if __name__ == "__main__":
    success = main()
    input("\n按回车键退出...")
    sys.exit(0 if success else 1) 