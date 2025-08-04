#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XPath测试脚本 - 验证课程选择器是否正确
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

class XPathTester:
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
    
    def test_xpath(self):
        """测试XPath选择器"""
        try:
            self.logger.info("开始测试XPath选择器...")
            
            # 导航到目录
            catalog_tab = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, Config.SELECTORS["catalog_item"]))
            )
            catalog_tab.click()
            time.sleep(3)
            
            # 测试1: 查找所有catalog_points_yi prevTips元素
            self.logger.info("\n=== 测试1: 查找catalog_points_yi prevTips元素 ===")
            pending_elements = self.driver.find_elements(By.CSS_SELECTOR, "span.catalog_points_yi.prevTips")
            self.logger.info(f"找到 {len(pending_elements)} 个catalog_points_yi prevTips元素")
            
            if len(pending_elements) == 0:
                self.logger.warning("未找到任何catalog_points_yi prevTips元素，尝试其他选择器...")
                
                # 尝试不同的选择器
                selectors = [
                    "span.catalog_points_yi",
                    "span[class*='catalog_points_yi']",
                    ".catalog_points_yi",
                    "span.prevTips"
                ]
                
                for selector in selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"选择器 '{selector}' 找到 {len(elements)} 个元素")
                    if len(elements) > 0:
                        self.logger.info(f"第一个元素的类名: {elements[0].get_attribute('class')}")
            
            # 测试2: 使用XPath查找未完成课程
            self.logger.info("\n=== 测试2: 使用XPath查找未完成课程 ===")
            xpath_selector = "//span[@class='catalog_points_yi prevTips']/preceding-sibling::span[@class='posCatalog_name'][1]"
            uncompleted_elements = self.driver.find_elements(By.XPATH, xpath_selector)
            self.logger.info(f"XPath找到 {len(uncompleted_elements)} 个未完成课程")
            
            # 测试3: 如果XPath失败，尝试其他方法
            if len(uncompleted_elements) == 0:
                self.logger.info("\n=== 测试3: 尝试其他XPath方法 ===")
                
                # 方法3.1: 查找所有posCatalog_name元素
                all_courses = self.driver.find_elements(By.CSS_SELECTOR, "span.posCatalog_name")
                self.logger.info(f"找到 {len(all_courses)} 个posCatalog_name元素")
                
                # 方法3.2: 查找所有catalog_points_yi元素（不限制类名）
                all_pending = self.driver.find_elements(By.CSS_SELECTOR, "span[class*='catalog_points_yi']")
                self.logger.info(f"找到 {len(all_pending)} 个包含catalog_points_yi的元素")
                
                for i, pending in enumerate(all_pending[:3]):
                    try:
                        class_name = pending.get_attribute("class")
                        text = pending.text.strip()
                        self.logger.info(f"  元素 {i+1}: 类名='{class_name}', 文本='{text}'")
                    except:
                        pass
            
            # 测试4: 手动检查页面结构
            self.logger.info("\n=== 测试4: 检查页面结构 ===")
            page_source = self.driver.page_source
            
            # 查找包含catalog_points_yi的片段
            if "catalog_points_yi" in page_source:
                self.logger.info("页面中包含catalog_points_yi")
                # 查找包含catalog_points_yi的行
                lines = page_source.split('\n')
                for i, line in enumerate(lines):
                    if "catalog_points_yi" in line and "posCatalog_name" in line:
                        self.logger.info(f"找到相关行 {i+1}: {line.strip()}")
                        break
            else:
                self.logger.warning("页面中不包含catalog_points_yi")
            
            return True
            
        except Exception as e:
            self.logger.error(f"测试XPath失败: {e}")
            return False
    
    def run(self):
        """运行测试"""
        try:
            self.logger.info("开始XPath测试...")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.test_xpath():
                return False
            
            self.logger.info("XPath测试完成！")
            return True
            
        except Exception as e:
            self.logger.error(f"测试过程出错: {e}")
            return False
        
        finally:
            if self.driver:
                input("按回车键关闭浏览器...")
                self.driver.quit()

if __name__ == "__main__":
    tester = XPathTester()
    tester.run() 