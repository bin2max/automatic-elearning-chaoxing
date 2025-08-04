#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面调试脚本 - 帮助诊断元素查找问题
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

class PageDebugger:
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
    
    def debug_catalog(self):
        """调试课程目录"""
        try:
            self.logger.info("开始调试课程目录...")
            
            # 导航到目录
            catalog_tab = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, Config.SELECTORS["catalog_item"]))
            )
            catalog_tab.click()
            time.sleep(3)
            
            # 方法1: 使用XPath查找未完成课程
            self.logger.info("\n=== 方法1: XPath查找未完成课程 ===")
            xpath_selector = "//span[@class='catalog_points_yi prevTips']/preceding-sibling::span[@class='posCatalog_name'][1]"
            uncompleted_elements = self.driver.find_elements(By.XPATH, xpath_selector)
            self.logger.info(f"XPath找到 {len(uncompleted_elements)} 个未完成课程")
            
            for i, element in enumerate(uncompleted_elements[:5]):  # 只显示前5个
                try:
                    course_text = element.text.strip()
                    course_title = element.get_attribute("title")
                    onclick = element.get_attribute("onclick")
                    
                    # 获取章节编号
                    chapter_number = ""
                    try:
                        sbar_element = element.find_element(By.CSS_SELECTOR, "em.posCatalog_sbar")
                        chapter_number = sbar_element.text.strip()
                    except:
                        pass
                    
                    self.logger.info(f"  未完成课程 {i+1}:")
                    self.logger.info(f"    章节编号: {chapter_number}")
                    self.logger.info(f"    文本: {course_text}")
                    self.logger.info(f"    标题: {course_title}")
                    self.logger.info(f"    点击事件: {onclick}")
                    
                except Exception as e:
                    self.logger.error(f"  调试未完成课程 {i+1} 时出错: {e}")
            
            # 方法2: 查找所有课程并检查状态
            self.logger.info("\n=== 方法2: 查找所有课程 ===")
            all_courses = self.driver.find_elements(By.CSS_SELECTOR, Config.SELECTORS["course"])
            self.logger.info(f"找到 {len(all_courses)} 个课程")
            
            completed_count = 0
            uncompleted_count = 0
            
            for i, course in enumerate(all_courses[:10]):  # 只检查前10个
                try:
                    course_text = course.text.strip()
                    course_title = course.get_attribute("title")
                    
                    # 检查完成状态
                    completed_icons = course.find_elements(By.CSS_SELECTOR, Config.SELECTORS["completed_icon"])
                    pending_tasks = course.find_elements(By.CSS_SELECTOR, Config.SELECTORS["pending_task"])
                    
                    # 检查后面是否有待完成任务点
                    has_pending_task = self.driver.execute_script("""
                        var element = arguments[0];
                        var nextSibling = element.nextElementSibling;
                        return nextSibling && nextSibling.className.includes('catalog_points_yi prevTips');
                    """, course)
                    
                    if completed_icons:
                        status = "已完成"
                        completed_count += 1
                    elif has_pending_task:
                        status = "未完成(方法2)"
                        uncompleted_count += 1
                    elif pending_tasks:
                        status = "未完成(方法1)"
                        uncompleted_count += 1
                    else:
                        status = "状态不明确"
                    
                    self.logger.info(f"  课程 {i+1}: {course_title or course_text} - {status}")
                    
                except Exception as e:
                    self.logger.error(f"  调试课程 {i+1} 时出错: {e}")
            
            self.logger.info(f"\n统计结果:")
            self.logger.info(f"  已完成课程: {completed_count} 个")
            self.logger.info(f"  未完成课程: {uncompleted_count} 个")
            self.logger.info(f"  XPath找到未完成课程: {len(uncompleted_elements)} 个")
            
            # 额外调试：查找所有catalog_points_yi prevTips元素
            self.logger.info("\n=== 额外调试: 查找所有catalog_points_yi prevTips元素 ===")
            pending_elements = self.driver.find_elements(By.CSS_SELECTOR, "span.catalog_points_yi.prevTips")
            self.logger.info(f"找到 {len(pending_elements)} 个catalog_points_yi prevTips元素")
            
            for i, pending in enumerate(pending_elements[:5]):  # 只显示前5个
                try:
                    pending_text = pending.text.strip()
                    pending_class = pending.get_attribute("class")
                    self.logger.info(f"  待完成任务点 {i+1}:")
                    self.logger.info(f"    文本: {pending_text}")
                    self.logger.info(f"    类名: {pending_class}")
                    
                    # 查找前面的课程元素
                    try:
                        prev_course = pending.find_element(By.XPATH, "./preceding-sibling::span[@class='posCatalog_name'][1]")
                        course_text = prev_course.text.strip()
                        course_title = prev_course.get_attribute("title")
                        self.logger.info(f"    对应课程: {course_title or course_text}")
                    except:
                        self.logger.info(f"    未找到对应课程")
                        
                except Exception as e:
                    self.logger.error(f"  调试待完成任务点 {i+1} 时出错: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"调试课程目录失败: {e}")
            return False
    
    def take_screenshot(self, filename="debug_screenshot.png"):
        """截图"""
        try:
            self.driver.save_screenshot(filename)
            self.logger.info(f"截图已保存: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            return False
    
    def run(self):
        """运行调试"""
        try:
            self.logger.info("开始页面调试...")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.debug_catalog():
                return False
            
            # 截图
            self.take_screenshot()
            
            self.logger.info("调试完成！")
            return True
            
        except Exception as e:
            self.logger.error(f"调试过程出错: {e}")
            return False
        
        finally:
            if self.driver:
                input("按回车键关闭浏览器...")
                self.driver.quit()

if __name__ == "__main__":
    debugger = PageDebugger()
    debugger.run() 