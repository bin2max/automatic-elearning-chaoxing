#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度分析脚本 - 诊断元素查找问题
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

class DeepAnalyzer:
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
    
    def deep_analyze(self):
        """深度分析页面"""
        try:
            self.logger.info("开始深度分析...")
            
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
            
            # 点击第一个课程
            test_course = uncompleted_elements[0]
            course_title = test_course.get_attribute("title") or test_course.text.strip()
            
            self.logger.info(f"\n=== 深度分析课程: {course_title} ===")
            
            # 获取onclick事件
            onclick = test_course.get_attribute("onclick")
            self.logger.info(f"onclick事件: {onclick}")
            
            # 执行onclick事件
            if onclick:
                self.logger.info("执行onclick事件...")
                self.driver.execute_script(onclick)
                
                # 等待页面加载
                self.logger.info("等待页面加载...")
                time.sleep(10)
                
                # 分析当前页面状态
                self.analyze_current_page()
            
            return True
            
        except Exception as e:
            self.logger.error(f"深度分析失败: {e}")
            return False
    
    def analyze_current_page(self):
        """分析当前页面状态"""
        try:
            self.logger.info("\n=== 分析当前页面状态 ===")
            
            # 1. 检查当前URL
            current_url = self.driver.current_url
            self.logger.info(f"当前URL: {current_url}")
            
            # 2. 检查页面标题
            page_title = self.driver.title
            self.logger.info(f"页面标题: {page_title}")
            
            # 3. 检查是否有iframe
            self.logger.info("\n3. 检查iframe:")
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            self.logger.info(f"找到 {len(iframes)} 个iframe")
            
            for i, iframe in enumerate(iframes):
                try:
                    iframe_src = iframe.get_attribute("src")
                    iframe_id = iframe.get_attribute("id")
                    iframe_name = iframe.get_attribute("name")
                    self.logger.info(f"  iframe {i+1}: id='{iframe_id}', name='{iframe_name}', src='{iframe_src}'")
                    
                    # 尝试切换到iframe
                    self.driver.switch_to.frame(iframe)
                    time.sleep(2)
                    
                    # 在iframe中查找元素
                    self.logger.info(f"  在iframe {i+1} 中查找元素:")
                    self.search_elements_in_frame(f"iframe {i+1}")
                    
                    # 切回主文档
                    self.driver.switch_to.default_content()
                    
                except Exception as e:
                    self.logger.error(f"  处理iframe {i+1} 失败: {e}")
                    self.driver.switch_to.default_content()
            
            # 4. 在主文档中查找元素
            self.logger.info("\n4. 在主文档中查找元素:")
            self.search_elements_in_frame("主文档")
            
            # 5. 检查页面源码
            self.logger.info("\n5. 检查页面源码:")
            page_source = self.driver.page_source
            
            # 查找关键字符串
            keywords = ["fullScreenContainer", "vjs-big-play-button", "video-js", "播放视频"]
            for keyword in keywords:
                count = page_source.count(keyword)
                self.logger.info(f"  '{keyword}' 在页面源码中出现 {count} 次")
            
            # 6. 等待更长时间后再次检查
            self.logger.info("\n6. 等待30秒后再次检查:")
            time.sleep(30)
            
            self.logger.info("30秒后再次查找元素:")
            self.search_elements_in_frame("主文档(30秒后)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"分析当前页面失败: {e}")
            return False
    
    def search_elements_in_frame(self, frame_name):
        """在指定框架中搜索元素"""
        try:
            # 查找fullScreenContainer
            fullscreen_selectors = [
                ".fullScreenContainer",
                "#fullScreenContainer",
                "div.fullScreenContainer",
                "div[class*='fullScreen']",
                "*[class*='fullScreen']"
            ]
            
            for i, selector in enumerate(fullscreen_selectors):
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > 0:
                        self.logger.info(f"    {frame_name} - 选择器 {i+1} '{selector}' 找到 {len(elements)} 个元素")
                        
                        for j, element in enumerate(elements):
                            class_name = element.get_attribute("class")
                            id_name = element.get_attribute("id")
                            self.logger.info(f"      元素 {j+1}: class='{class_name}', id='{id_name}'")
                            
                except Exception as e:
                    self.logger.error(f"    {frame_name} - 选择器 {i+1} 执行失败: {e}")
            
            # 查找播放按钮
            play_button_selectors = [
                "button.vjs-big-play-button",
                ".vjs-big-play-button",
                "button[title*='播放']",
                "button[title='播放视频']",
                "*[class*='vjs-big-play']",
                "*[title*='播放']"
            ]
            
            for i, selector in enumerate(play_button_selectors):
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > 0:
                        self.logger.info(f"    {frame_name} - 选择器 {i+1} '{selector}' 找到 {len(elements)} 个元素")
                        
                        for j, element in enumerate(elements):
                            class_name = element.get_attribute("class")
                            title = element.get_attribute("title")
                            is_displayed = element.is_displayed()
                            is_enabled = element.is_enabled()
                            self.logger.info(f"      元素 {j+1}: class='{class_name}', title='{title}', 可见={is_displayed}, 启用={is_enabled}")
                            
                except Exception as e:
                    self.logger.error(f"    {frame_name} - 选择器 {i+1} 执行失败: {e}")
            
            # 查找视频播放器
            video_selectors = [
                ".video-js",
                "video",
                ".vjs-tech",
                "#video",
                "*[class*='video']",
                "*[class*='vjs']"
            ]
            
            for i, selector in enumerate(video_selectors):
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > 0:
                        self.logger.info(f"    {frame_name} - 选择器 {i+1} '{selector}' 找到 {len(elements)} 个元素")
                        
                        for j, element in enumerate(elements):
                            class_name = element.get_attribute("class")
                            id_name = element.get_attribute("id")
                            src = element.get_attribute("src")
                            self.logger.info(f"      元素 {j+1}: class='{class_name}', id='{id_name}', src='{src}'")
                            
                except Exception as e:
                    self.logger.error(f"    {frame_name} - 选择器 {i+1} 执行失败: {e}")
            
        except Exception as e:
            self.logger.error(f"在{frame_name}中搜索元素失败: {e}")
    
    def run(self):
        """运行分析"""
        try:
            self.logger.info("开始深度分析...")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.deep_analyze():
                return False
            
            self.logger.info("深度分析完成！")
            return True
            
        except Exception as e:
            self.logger.error(f"分析过程出错: {e}")
            return False
        
        finally:
            if self.driver:
                input("按回车键关闭浏览器...")
                self.driver.quit()

if __name__ == "__main__":
    analyzer = DeepAnalyzer()
    analyzer.run() 