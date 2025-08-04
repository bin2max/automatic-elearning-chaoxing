#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嵌套iframe测试脚本 - 专门测试嵌套iframe的处理
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

class NestedIframeTester:
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
    
    def test_nested_iframe(self):
        """测试嵌套iframe"""
        try:
            self.logger.info("开始测试嵌套iframe...")
            
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
            
            self.logger.info(f"测试课程: {course_title}")
            
            # 获取onclick事件
            onclick = test_course.get_attribute("onclick")
            self.logger.info(f"onclick事件: {onclick}")
            
            # 执行onclick事件
            if onclick:
                self.logger.info("执行onclick事件...")
                self.driver.execute_script(onclick)
                time.sleep(10)
                
                # 测试嵌套iframe处理
                return self.analyze_nested_iframes()
            
            return False
            
        except Exception as e:
            self.logger.error(f"测试嵌套iframe失败: {e}")
            return False
    
    def analyze_nested_iframes(self):
        """分析嵌套iframe"""
        try:
            self.logger.info("\n=== 分析嵌套iframe ===")
            
            # 1. 检查主文档中的iframe
            self.logger.info("\n1. 检查主文档中的iframe:")
            main_iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            self.logger.info(f"主文档中找到 {len(main_iframes)} 个iframe")
            
            for i, iframe in enumerate(main_iframes):
                iframe_id = iframe.get_attribute("id")
                iframe_name = iframe.get_attribute("name")
                iframe_src = iframe.get_attribute("src")
                iframe_class = iframe.get_attribute("class")
                
                self.logger.info(f"  iframe {i+1}: id='{iframe_id}', name='{iframe_name}', class='{iframe_class}', src='{iframe_src}'")
            
            # 2. 查找主iframe（id为"iframe"）
            main_iframe = None
            for iframe in main_iframes:
                if iframe.get_attribute("id") == "iframe":
                    main_iframe = iframe
                    break
            
            if main_iframe:
                self.logger.info("\n2. 切换到主iframe...")
                self.driver.switch_to.frame(main_iframe)
                time.sleep(3)
                
                # 3. 检查主iframe中的嵌套iframe
                self.logger.info("\n3. 检查主iframe中的嵌套iframe:")
                nested_iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                self.logger.info(f"主iframe中找到 {len(nested_iframes)} 个嵌套iframe")
                
                for i, nested_iframe in enumerate(nested_iframes):
                    nested_id = nested_iframe.get_attribute("id")
                    nested_name = nested_iframe.get_attribute("name")
                    nested_src = nested_iframe.get_attribute("src")
                    nested_class = nested_iframe.get_attribute("class")
                    
                    self.logger.info(f"  嵌套iframe {i+1}: id='{nested_id}', name='{nested_name}', class='{nested_class}', src='{nested_src}'")
                    
                    # 检查是否是视频iframe
                    if "ans-insertvideo-online" in (nested_class or ""):
                        self.logger.info(f"  ✅ 找到视频iframe: {nested_class}")
                        
                        # 切换到视频iframe
                        try:
                            self.logger.info(f"  切换到视频iframe {i+1}...")
                            self.driver.switch_to.frame(nested_iframe)
                            time.sleep(3)
                            
                            # 在视频iframe中查找播放按钮
                            play_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".vjs-big-play-button")
                            self.logger.info(f"  在视频iframe中找到 {len(play_buttons)} 个播放按钮")
                            
                            if len(play_buttons) > 0:
                                for j, button in enumerate(play_buttons):
                                    class_name = button.get_attribute("class")
                                    title = button.get_attribute("title")
                                    is_displayed = button.is_displayed()
                                    is_enabled = button.is_enabled()
                                    
                                    self.logger.info(f"    播放按钮 {j+1}: class='{class_name}', title='{title}', 可见={is_displayed}, 启用={is_enabled}")
                                    
                                    if is_displayed and is_enabled:
                                        self.logger.info("    ✅ 找到可用的播放按钮！")
                                        
                                        # 尝试点击播放按钮
                                        try:
                                            self.logger.info("    尝试点击播放按钮...")
                                            button.click()
                                            self.logger.info("    ✅ 播放按钮点击成功！")
                                            return True
                                        except Exception as e:
                                            self.logger.error(f"    播放按钮点击失败: {e}")
                            
                            # 切回主iframe
                            self.driver.switch_to.parent_frame()
                            
                        except Exception as e:
                            self.logger.error(f"  处理视频iframe {i+1} 失败: {e}")
                            # 确保切回主iframe
                            try:
                                self.driver.switch_to.parent_frame()
                            except:
                                pass
                
                # 切回主文档
                self.driver.switch_to.default_content()
            else:
                self.logger.warning("未找到主iframe（id='iframe'）")
            
            # 4. 备用方案：检查所有iframe
            self.logger.info("\n4. 备用方案：检查所有iframe...")
            for i, iframe in enumerate(main_iframes):
                try:
                    self.logger.info(f"  检查iframe {i+1}...")
                    self.driver.switch_to.frame(iframe)
                    time.sleep(2)
                    
                    # 在当前iframe中查找播放按钮
                    play_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".vjs-big-play-button")
                    if len(play_buttons) > 0:
                        self.logger.info(f"  ✅ 在iframe {i+1} 中找到 {len(play_buttons)} 个播放按钮")
                        
                        for j, button in enumerate(play_buttons):
                            class_name = button.get_attribute("class")
                            title = button.get_attribute("title")
                            is_displayed = button.is_displayed()
                            is_enabled = button.is_enabled()
                            
                            self.logger.info(f"    播放按钮 {j+1}: class='{class_name}', title='{title}', 可见={is_displayed}, 启用={is_enabled}")
                    
                    # 切回主文档
                    self.driver.switch_to.default_content()
                    
                except Exception as e:
                    self.logger.error(f"  检查iframe {i+1} 失败: {e}")
                    self.driver.switch_to.default_content()
            
            return False
            
        except Exception as e:
            self.logger.error(f"分析嵌套iframe失败: {e}")
            return False
    
    def run(self):
        """运行测试"""
        try:
            self.logger.info("开始嵌套iframe测试...")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.test_nested_iframe():
                return False
            
            self.logger.info("嵌套iframe测试完成！")
            return True
            
        except Exception as e:
            self.logger.error(f"测试过程出错: {e}")
            return False
        
        finally:
            if self.driver:
                input("按回车键关闭浏览器...")
                self.driver.quit()

if __name__ == "__main__":
    tester = NestedIframeTester()
    tester.run() 