#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课程点击测试脚本 - 专门测试课程点击功能
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

class CourseClickTester:
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
    
    def test_course_click(self):
        """测试课程点击"""
        try:
            self.logger.info("开始测试课程点击...")
            
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
            
            # 测试前3个课程
            for i in range(min(3, len(uncompleted_elements))):
                try:
                    test_course = uncompleted_elements[i]
                    course_title = test_course.get_attribute("title") or test_course.text.strip()
                    
                    self.logger.info(f"\n=== 测试课程 {i+1}: {course_title} ===")
                    
                    # 获取课程信息
                    onclick = test_course.get_attribute("onclick")
                    self.logger.info(f"onclick事件: {onclick}")
                    
                    # 检查元素状态
                    is_displayed = test_course.is_displayed()
                    is_enabled = test_course.is_enabled()
                    self.logger.info(f"元素可见: {is_displayed}")
                    self.logger.info(f"元素启用: {is_enabled}")
                    
                    # 滚动到元素位置
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", test_course)
                    time.sleep(2)
                    
                    # 尝试点击
                    click_success = False
                    
                    # 方法1: onclick事件
                    if onclick:
                        try:
                            self.logger.info("尝试方法1: onclick事件")
                            self.driver.execute_script(onclick)
                            click_success = True
                            self.logger.info("✅ 方法1成功")
                        except Exception as e:
                            self.logger.warning(f"❌ 方法1失败: {e}")
                    
                    # 方法2: JavaScript点击
                    if not click_success:
                        try:
                            self.logger.info("尝试方法2: JavaScript点击")
                            self.driver.execute_script("arguments[0].click();", test_course)
                            click_success = True
                            self.logger.info("✅ 方法2成功")
                        except Exception as e:
                            self.logger.warning(f"❌ 方法2失败: {e}")
                    
                    # 方法3: 直接点击
                    if not click_success:
                        try:
                            self.logger.info("尝试方法3: 直接点击")
                            test_course.click()
                            click_success = True
                            self.logger.info("✅ 方法3成功")
                        except Exception as e:
                            self.logger.warning(f"❌ 方法3失败: {e}")
                    
                    if click_success:
                        self.logger.info("课程点击成功，等待页面加载...")
                        time.sleep(5)
                        
                        # 检查是否进入课程页面
                        try:
                            # 查找fullScreenContainer
                            fullscreen = self.driver.find_element(By.CSS_SELECTOR, ".fullScreenContainer")
                            self.logger.info("✅ 成功进入课程页面")
                            
                            # 返回目录继续测试下一个
                            self.driver.back()
                            time.sleep(3)
                            
                            # 重新导航到目录
                            catalog_tab = self.wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, Config.SELECTORS["catalog_item"]))
                            )
                            catalog_tab.click()
                            time.sleep(3)
                            
                            # 重新获取课程列表
                            uncompleted_elements = self.driver.find_elements(By.XPATH, xpath_selector)
                            
                        except:
                            self.logger.warning("❌ 可能未成功进入课程页面")
                    else:
                        self.logger.error("❌ 所有点击方法都失败")
                    
                except Exception as e:
                    self.logger.error(f"测试课程 {i+1} 时出错: {e}")
                    continue
            
            return True
            
        except Exception as e:
            self.logger.error(f"测试课程点击失败: {e}")
            return False
    
    def run(self):
        """运行测试"""
        try:
            self.logger.info("开始课程点击测试...")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.test_course_click():
                return False
            
            self.logger.info("课程点击测试完成！")
            return True
            
        except Exception as e:
            self.logger.error(f"测试过程出错: {e}")
            return False
        
        finally:
            if self.driver:
                input("按回车键关闭浏览器...")
                self.driver.quit()

if __name__ == "__main__":
    tester = CourseClickTester()
    tester.run() 