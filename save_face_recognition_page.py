#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保存人脸识别弹窗页面源码
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import Config
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FaceRecognitionPageSaver:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        try:
            # 优先使用项目根目录的chromedriver.exe
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            chromedriver_path = os.path.join(current_dir, "chromedriver.exe")
            
            if os.path.exists(chromedriver_path):
                logger.info(f"使用本地ChromeDriver: {chromedriver_path}")
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(service=service)
            else:
                logger.info("本地ChromeDriver不存在，尝试使用webdriver-manager...")
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service)
            
            self.driver.implicitly_wait(Config.IMPLICIT_WAIT)
            self.wait = WebDriverWait(self.driver, Config.ELEMENT_WAIT_TIME)
            return True
        except Exception as e:
            logger.error(f"设置驱动失败: {e}")
            return False
    
    def login(self):
        try:
            logger.info("开始登录...")
            self.driver.get("https://passport2.chaoxing.com/login")
            time.sleep(3)
            
            username_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, Config.SELECTORS["login_username"])))
            username_input.send_keys(Config.USERNAME)
            
            password_input = self.driver.find_element(By.CSS_SELECTOR, Config.SELECTORS["login_password"])
            password_input.send_keys(Config.PASSWORD)
            
            login_button = self.driver.find_element(By.CSS_SELECTOR, Config.SELECTORS["login_button"])
            login_button.click()
            time.sleep(5)
            
            logger.info("登录成功")
            return True
        except Exception as e:
            logger.error(f"登录失败: {e}")
            return False
    
    def navigate_to_course(self):
        try:
            logger.info("导航到课程页面...")
            self.driver.get(Config.COURSE_URL)
            time.sleep(5)
            logger.info("已进入课程页面")
            return True
        except Exception as e:
            logger.error(f"导航失败: {e}")
            return False
    
    def wait_for_face_recognition_popup(self):
        try:
            logger.info("等待人脸识别弹窗出现...")
            logger.info("请手动触发人脸识别弹窗，然后按回车键继续...")
            input("按回车键继续...")
            
            face_popups = self.driver.find_elements(By.CSS_SELECTOR, ".faceCollectQrPopVideo, .maskDiv1.chapterVideoFaceQrMaskDiv")
            if len(face_popups) > 0:
                logger.info(f"检测到 {len(face_popups)} 个人脸识别弹窗")
                return True
            else:
                logger.warning("未检测到人脸识别弹窗")
                return False
        except Exception as e:
            logger.error(f"等待弹窗失败: {e}")
            return False
    
    def save_page_source(self):
        try:
            logger.info("保存页面源码...")
            
            save_dir = "face_recognition_pages"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 保存主文档源码
            main_source = self.driver.page_source
            main_file = os.path.join(save_dir, "face_recognition_main_document.html")
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(main_source)
            logger.info(f"主文档源码已保存到: {main_file}")
            
            # 保存iframe源码
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            logger.info(f"找到 {len(iframes)} 个iframe")
            
            for i, iframe in enumerate(iframes):
                try:
                    iframe_id = iframe.get_attribute("id")
                    iframe_name = iframe.get_attribute("name")
                    
                    self.driver.switch_to.frame(iframe)
                    time.sleep(2)
                    
                    iframe_source = self.driver.page_source
                    iframe_file = os.path.join(save_dir, f"face_recognition_iframe_{i+1}_{iframe_id or iframe_name or 'unnamed'}.html")
                    with open(iframe_file, 'w', encoding='utf-8') as f:
                        f.write(iframe_source)
                    logger.info(f"iframe {i+1} 源码已保存到: {iframe_file}")
                    
                    self.driver.switch_to.default_content()
                except Exception as e:
                    logger.error(f"保存iframe {i+1} 失败: {e}")
                    self.driver.switch_to.default_content()
            
            return True
        except Exception as e:
            logger.error(f"保存源码失败: {e}")
            return False
    
    def analyze_face_recognition_elements(self):
        try:
            logger.info("分析人脸识别相关元素...")
            
            selectors = [
                ".faceCollectQrPopVideo",
                ".maskDiv1.chapterVideoFaceQrMaskDiv", 
                ".maskDiv1",
                ".chapterVideoFaceQrMaskDiv",
                ".popDiv1.wid640",
                ".popClose.fr",
                "a.popClose.fr",
                ".face-div",
                ".faceCheckFailPopVideo"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > 0:
                        logger.info(f"选择器 '{selector}' 找到 {len(elements)} 个元素")
                        for i, element in enumerate(elements):
                            try:
                                tag_name = element.tag_name
                                class_name = element.get_attribute("class")
                                id_name = element.get_attribute("id")
                                is_displayed = element.is_displayed()
                                logger.info(f"  元素 {i+1}: tag='{tag_name}', class='{class_name}', id='{id_name}', 可见={is_displayed}")
                            except:
                                pass
                    else:
                        logger.info(f"选择器 '{selector}' 未找到元素")
                except Exception as e:
                    logger.warning(f"选择器 '{selector}' 查询失败: {e}")
            
            return True
        except Exception as e:
            logger.error(f"分析元素失败: {e}")
            return False
    
    def run(self):
        try:
            logger.info("开始保存人脸识别弹窗页面源码...")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.navigate_to_course():
                return False
            
            if not self.wait_for_face_recognition_popup():
                logger.warning("未检测到人脸识别弹窗，但仍会保存页面源码")
            
            self.analyze_face_recognition_elements()
            
            if not self.save_page_source():
                return False
            
            logger.info("人脸识别弹窗页面源码保存完成！")
            return True
            
        except Exception as e:
            logger.error(f"程序运行失败: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    saver = FaceRecognitionPageSaver()
    saver.run() 