#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面元素分析脚本 - 分析页面结构和元素
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PageAnalyzer:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """设置浏览器驱动"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # 尝试获取ChromeDriver
            try:
                driver_path = ChromeDriverManager().install()
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                # 使用系统PATH中的ChromeDriver
                service = Service()
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 10)
            
            self.logger.info("浏览器驱动设置成功")
            return True
            
        except Exception as e:
            self.logger.error(f"设置浏览器驱动失败: {e}")
            return False
    
    def login(self):
        """登录超星平台"""
        try:
            self.logger.info("开始登录超星平台...")
            self.driver.get(Config.COURSE_URL)
            time.sleep(5)
            
            # 检查是否需要登录
            try:
                username_input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, Config.SELECTORS["login_username"]))
                )
                
                username_input.clear()
                username_input.send_keys(Config.USERNAME)
                
                password_input = self.driver.find_element(By.CSS_SELECTOR, Config.SELECTORS["login_password"])
                password_input.clear()
                password_input.send_keys(Config.PASSWORD)
                
                login_button = self.driver.find_element(By.CSS_SELECTOR, Config.SELECTORS["login_button"])
                login_button.click()
                
                self.logger.info("登录信息已提交，等待页面跳转...")
                time.sleep(8)
                
            except:
                self.logger.info("未发现登录页面，可能已经登录")
            
            return True
            
        except Exception as e:
            self.logger.error(f"登录失败: {e}")
            return False
    
    def analyze_page_structure(self):
        """分析页面结构"""
        try:
            self.logger.info("开始分析页面结构...")
            
            # 导航到目录
            catalog_tab = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, Config.SELECTORS["catalog_item"]))
            )
            catalog_tab.click()
            time.sleep(3)
            
            # 查找未完成课程
            xpath_selector = "//span[@class='catalog_points_yi prevTips']/preceding-sibling::span[@class='posCatalog_name'][1]"
            uncompleted_elements = self.driver.find_elements(By.XPATH, xpath_selector)
            
            if len(uncompleted_elements) == 0:
                self.logger.warning("未找到未完成课程")
                return False
            
            self.logger.info(f"找到 {len(uncompleted_elements)} 个未完成课程")
            
            # 点击第一个课程进行分析
            test_course = uncompleted_elements[0]
            course_title = test_course.get_attribute("title") or test_course.text.strip()
            
            self.logger.info(f"\n=== 分析课程: {course_title} ===")
            
            # 获取onclick事件
            onclick = test_course.get_attribute("onclick")
            self.logger.info(f"onclick事件: {onclick}")
            
            # 执行onclick事件
            if onclick:
                self.logger.info("执行onclick事件...")
                self.driver.execute_script(onclick)
                time.sleep(5)
                
                # 分析页面结构
                self.analyze_video_page()
            
            return True
            
        except Exception as e:
            self.logger.error(f"分析页面结构失败: {e}")
            return False
    
    def analyze_video_page(self):
        """分析视频页面结构"""
        try:
            self.logger.info("\n=== 分析视频页面结构 ===")
            
            # 1. 查找fullScreenContainer
            self.logger.info("\n1. 查找fullScreenContainer元素:")
            fullscreen_selectors = [
                ".fullScreenContainer",
                "#fullScreenContainer",
                "div.fullScreenContainer",
                "div[class*='fullScreen']"
            ]
            
            for i, selector in enumerate(fullscreen_selectors):
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"  选择器 {i+1} '{selector}' 找到 {len(elements)} 个元素")
                    
                    if len(elements) > 0:
                        for j, element in enumerate(elements):
                            class_name = element.get_attribute("class")
                            id_name = element.get_attribute("id")
                            self.logger.info(f"    元素 {j+1}: class='{class_name}', id='{id_name}'")
                            
                except Exception as e:
                    self.logger.error(f"  选择器 {i+1} 执行失败: {e}")
            
            # 2. 查找播放按钮
            self.logger.info("\n2. 查找播放按钮:")
            play_button_selectors = [
                "button.vjs-big-play-button",
                ".vjs-big-play-button",
                "button[title*='播放']",
                "button[title='播放视频']",
                ".fullScreenContainer button.vjs-big-play-button",
                ".fullScreenContainer .vjs-big-play-button"
            ]
            
            for i, selector in enumerate(play_button_selectors):
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"  选择器 {i+1} '{selector}' 找到 {len(elements)} 个元素")
                    
                    if len(elements) > 0:
                        for j, element in enumerate(elements):
                            class_name = element.get_attribute("class")
                            title = element.get_attribute("title")
                            is_displayed = element.is_displayed()
                            is_enabled = element.is_enabled()
                            self.logger.info(f"    元素 {j+1}: class='{class_name}', title='{title}', 可见={is_displayed}, 启用={is_enabled}")
                            
                except Exception as e:
                    self.logger.error(f"  选择器 {i+1} 执行失败: {e}")
            
            # 3. 查找视频播放器
            self.logger.info("\n3. 查找视频播放器:")
            video_selectors = [
                ".video-js",
                "video",
                ".vjs-tech",
                "#video"
            ]
            
            for i, selector in enumerate(video_selectors):
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"  选择器 {i+1} '{selector}' 找到 {len(elements)} 个元素")
                    
                    if len(elements) > 0:
                        for j, element in enumerate(elements):
                            class_name = element.get_attribute("class")
                            id_name = element.get_attribute("id")
                            src = element.get_attribute("src")
                            self.logger.info(f"    元素 {j+1}: class='{class_name}', id='{id_name}', src='{src}'")
                            
                except Exception as e:
                    self.logger.error(f"  选择器 {i+1} 执行失败: {e}")
            
            # 4. 分析页面HTML结构
            self.logger.info("\n4. 页面HTML结构分析:")
            try:
                page_source = self.driver.page_source
                
                # 查找包含fullScreenContainer的部分
                if "fullScreenContainer" in page_source:
                    self.logger.info("  ✅ 页面包含fullScreenContainer")
                    
                    # 查找包含vjs-big-play-button的部分
                    if "vjs-big-play-button" in page_source:
                        self.logger.info("  ✅ 页面包含vjs-big-play-button")
                    else:
                        self.logger.warning("  ❌ 页面不包含vjs-big-play-button")
                        
                else:
                    self.logger.warning("  ❌ 页面不包含fullScreenContainer")
                    
            except Exception as e:
                self.logger.error(f"  分析页面HTML失败: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"分析视频页面失败: {e}")
            return False
    
    def run(self):
        """运行分析"""
        try:
            self.logger.info("开始页面元素分析...")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.analyze_page_structure():
                return False
            
            self.logger.info("页面元素分析完成！")
            return True
            
        except Exception as e:
            self.logger.error(f"分析过程出错: {e}")
            return False
        
        finally:
            if self.driver:
                input("按回车键关闭浏览器...")
                self.driver.quit()

if __name__ == "__main__":
    analyzer = PageAnalyzer()
    analyzer.run() 