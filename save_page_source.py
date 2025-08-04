#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面源码保存脚本 - 保存页面源码供分析
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
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PageSourceSaver:
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
    
    def save_page_sources(self):
        """保存页面源码"""
        try:
            self.logger.info("开始保存页面源码...")
            
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
            
            self.logger.info(f"分析课程: {course_title}")
            
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
                
                # 保存主文档源码
                self.save_source("main_document.html", "主文档")
                
                # 检查iframe
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                self.logger.info(f"找到 {len(iframes)} 个iframe")
                
                for i, iframe in enumerate(iframes):
                    try:
                        iframe_src = iframe.get_attribute("src")
                        iframe_id = iframe.get_attribute("id")
                        iframe_name = iframe.get_attribute("name")
                        
                        self.logger.info(f"处理iframe {i+1}: id='{iframe_id}', name='{iframe_name}', src='{iframe_src}'")
                        
                        # 切换到iframe
                        self.driver.switch_to.frame(iframe)
                        time.sleep(2)
                        
                        # 保存iframe源码
                        filename = f"iframe_{i+1}_{iframe_id or iframe_name or 'unnamed'}.html"
                        self.save_source(filename, f"iframe {i+1}")
                        
                        # 切回主文档
                        self.driver.switch_to.default_content()
                        
                    except Exception as e:
                        self.logger.error(f"处理iframe {i+1} 失败: {e}")
                        self.driver.switch_to.default_content()
                
                # 等待更长时间后再次保存
                self.logger.info("等待30秒后再次保存...")
                time.sleep(30)
                
                filename = "main_document_30s_later.html"
                self.save_source(filename, "主文档(30秒后)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"保存页面源码失败: {e}")
            return False
    
    def save_source(self, filename, description):
        """保存源码到文件"""
        try:
            page_source = self.driver.page_source
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            # 创建保存目录
            save_dir = "page_sources"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            filepath = os.path.join(save_dir, filename)
            
            # 保存源码
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<!-- 页面信息 -->\n")
                f.write(f"<!-- URL: {current_url} -->\n")
                f.write(f"<!-- 标题: {page_title} -->\n")
                f.write(f"<!-- 描述: {description} -->\n")
                f.write(f"<!-- 保存时间: {time.strftime('%Y-%m-%d %H:%M:%S')} -->\n")
                f.write(f"<!-- 页面源码开始 -->\n")
                f.write(page_source)
                f.write(f"\n<!-- 页面源码结束 -->\n")
            
            self.logger.info(f"已保存 {description} 源码到: {filepath}")
            
            # 分析源码中的关键元素
            keywords = ["fullScreenContainer", "vjs-big-play-button", "video-js", "播放视频"]
            for keyword in keywords:
                count = page_source.count(keyword)
                if count > 0:
                    self.logger.info(f"  '{keyword}' 在 {description} 中出现 {count} 次")
            
            return True
            
        except Exception as e:
            self.logger.error(f"保存源码失败: {e}")
            return False
    
    def run(self):
        """运行保存"""
        try:
            self.logger.info("开始保存页面源码...")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.save_page_sources():
                return False
            
            self.logger.info("页面源码保存完成！")
            self.logger.info("源码文件保存在 'page_sources' 目录中")
            return True
            
        except Exception as e:
            self.logger.error(f"保存过程出错: {e}")
            return False
        
        finally:
            if self.driver:
                input("按回车键关闭浏览器...")
                self.driver.quit()

if __name__ == "__main__":
    saver = PageSourceSaver()
    saver.run() 