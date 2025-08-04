#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
播放按钮测试脚本 - 帮助诊断播放问题
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

class PlayButtonTester:
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
    
    def find_and_test_course(self):
        """查找并测试课程"""
        try:
            self.logger.info("开始查找未完成课程...")
            
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
            
            # 测试第一个课程
            test_course = uncompleted_elements[0]
            course_title = test_course.get_attribute("title") or test_course.text.strip()
            
            self.logger.info(f"测试课程: {course_title}")
            
            # 获取onclick事件
            onclick = test_course.get_attribute("onclick")
            self.logger.info(f"课程onclick事件: {onclick}")
            
            # 尝试多种点击方法
            click_success = False
            
            # 方法1: 使用onclick事件
            if onclick:
                try:
                    self.logger.info("尝试方法1: 执行onclick事件")
                    self.driver.execute_script(onclick)
                    click_success = True
                    self.logger.info("方法1: onclick事件执行成功")
                except Exception as e:
                    self.logger.warning(f"方法1失败: {e}")
            
            # 方法2: JavaScript点击
            if not click_success:
                try:
                    self.logger.info("尝试方法2: JavaScript点击")
                    self.driver.execute_script("arguments[0].click();", test_course)
                    click_success = True
                    self.logger.info("方法2: JavaScript点击成功")
                except Exception as e:
                    self.logger.warning(f"方法2失败: {e}")
            
            # 方法3: 直接点击
            if not click_success:
                try:
                    self.logger.info("尝试方法3: 直接点击")
                    test_course.click()
                    click_success = True
                    self.logger.info("方法3: 直接点击成功")
                except Exception as e:
                    self.logger.warning(f"方法3失败: {e}")
            
            if not click_success:
                self.logger.error("所有点击方法都失败")
                return False
            
            self.logger.info("已点击课程，等待页面加载...")
            time.sleep(Config.VIDEO_WAIT_TIME)
            
            # 测试播放按钮
            return self.test_play_button()
            
        except Exception as e:
            self.logger.error(f"查找课程失败: {e}")
            return False
    
    def test_play_button(self):
        """测试播放按钮"""
        try:
            self.logger.info("开始测试播放按钮...")
            
            # 等待视频播放器加载
            time.sleep(5)
            
            # 检查并切换到iframe
            iframe_found = self.switch_to_video_iframe()
            if not iframe_found:
                self.logger.warning("未找到视频iframe，继续在主文档中查找")
            
            # 首先检查fullScreenContainer是否存在
            try:
                fullscreen_container = self.driver.find_element(By.CSS_SELECTOR, ".fullScreenContainer")
                self.logger.info("找到fullScreenContainer元素")
                
                # 在fullScreenContainer内查找播放按钮
                container_selectors = [
                    ".fullScreenContainer button.vjs-big-play-button",
                    ".fullScreenContainer .vjs-big-play-button",
                    ".fullScreenContainer button[title*='播放']",
                    ".fullScreenContainer button[class*='play']",
                    ".fullScreenContainer .vjs-play-button",
                    ".fullScreenContainer button[title='播放视频']"
                ]
                
                for i, selector in enumerate(container_selectors):
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        self.logger.info(f"fullScreenContainer内选择器 {i+1} '{selector}' 找到 {len(elements)} 个元素")
                        
                        for j, element in enumerate(elements):
                            try:
                                class_name = element.get_attribute("class")
                                title = element.get_attribute("title")
                                text = element.text.strip()
                                is_displayed = element.is_displayed()
                                is_enabled = element.is_enabled()
                                
                                self.logger.info(f"  fullScreenContainer内元素 {j+1}:")
                                self.logger.info(f"    类名: {class_name}")
                                self.logger.info(f"    标题: {title}")
                                self.logger.info(f"    文本: {text}")
                                self.logger.info(f"    可见: {is_displayed}")
                                self.logger.info(f"    启用: {is_enabled}")
                                
                                if is_displayed and is_enabled:
                                    found_buttons.append({
                                        'element': element,
                                        'selector': selector,
                                        'index': j,
                                        'location': 'fullScreenContainer'
                                    })
                                    
                            except Exception as e:
                                self.logger.error(f"  获取fullScreenContainer内元素 {j+1} 信息失败: {e}")
                                
                    except Exception as e:
                        self.logger.error(f"fullScreenContainer内选择器 {i+1} 执行失败: {e}")
                        
            except:
                self.logger.warning("未找到fullScreenContainer元素")
            
            # 查找所有可能的播放按钮（全局）
            selectors = [
                "button.vjs-big-play-button",
                ".vjs-big-play-button",
                "button[title*='播放']",
                "button[class*='play']",
                ".vjs-play-button",
                "button[aria-label*='播放']",
                "button[title='播放视频']"
            ]
            
            found_buttons = []
            
            for i, selector in enumerate(selectors):
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"选择器 {i+1} '{selector}' 找到 {len(elements)} 个元素")
                    
                    for j, element in enumerate(elements):
                        try:
                            class_name = element.get_attribute("class")
                            title = element.get_attribute("title")
                            text = element.text.strip()
                            is_displayed = element.is_displayed()
                            is_enabled = element.is_enabled()
                            
                            self.logger.info(f"  元素 {j+1}:")
                            self.logger.info(f"    类名: {class_name}")
                            self.logger.info(f"    标题: {title}")
                            self.logger.info(f"    文本: {text}")
                            self.logger.info(f"    可见: {is_displayed}")
                            self.logger.info(f"    启用: {is_enabled}")
                            
                            if is_displayed and is_enabled:
                                found_buttons.append({
                                    'element': element,
                                    'selector': selector,
                                    'index': j
                                })
                                
                        except Exception as e:
                            self.logger.error(f"  获取元素 {j+1} 信息失败: {e}")
                            
                except Exception as e:
                    self.logger.error(f"选择器 {i+1} 执行失败: {e}")
            
            # 查找视频播放器容器
            video_containers = self.driver.find_elements(By.CSS_SELECTOR, ".video-js, .vjs-tech, video")
            self.logger.info(f"找到 {len(video_containers)} 个视频播放器容器")
            
            # 尝试点击找到的播放按钮
            if found_buttons:
                self.logger.info(f"找到 {len(found_buttons)} 个可用的播放按钮")
                
                for i, button_info in enumerate(found_buttons[:3]):  # 只测试前3个
                    try:
                        button = button_info['element']
                        selector = button_info['selector']
                        
                        self.logger.info(f"尝试点击播放按钮 {i+1} (选择器: {selector})")
                        
                        # 滚动到按钮位置
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        
                        # 点击按钮
                        button.click()
                        self.logger.info(f"成功点击播放按钮 {i+1}")
                        
                        # 等待一下看是否有反应
                        time.sleep(3)
                        
                        # 检查是否开始播放
                        try:
                            # 查找播放状态指示器
                            playing_indicators = self.driver.find_elements(By.CSS_SELECTOR, ".vjs-playing, .vjs-paused")
                            if playing_indicators:
                                self.logger.info("检测到播放状态变化")
                            else:
                                self.logger.info("未检测到播放状态变化")
                        except:
                            pass
                        
                        break
                        
                    except Exception as e:
                        self.logger.error(f"点击播放按钮 {i+1} 失败: {e}")
                        continue
            else:
                self.logger.warning("未找到可用的播放按钮")
            
            return True
            
        except Exception as e:
            self.logger.error(f"测试播放按钮失败: {e}")
            return False
    
    def switch_to_video_iframe(self):
        """切换到视频iframe"""
        try:
            self.logger.info("检查iframe...")
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            self.logger.info(f"找到 {len(iframes)} 个iframe")
            
            # 首先查找主要的iframe（通常是id为"iframe"的）
            main_iframe = None
            for iframe in iframes:
                iframe_id = iframe.get_attribute("id")
                if iframe_id == "iframe":
                    main_iframe = iframe
                    break
            
            if main_iframe:
                self.logger.info("找到主iframe，切换到主iframe...")
                self.driver.switch_to.frame(main_iframe)
                time.sleep(3)
                
                # 在主iframe中查找嵌套的视频iframe
                nested_iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                self.logger.info(f"在主iframe中找到 {len(nested_iframes)} 个嵌套iframe")
                
                for i, nested_iframe in enumerate(nested_iframes):
                    try:
                        nested_src = nested_iframe.get_attribute("src")
                        nested_class = nested_iframe.get_attribute("class")
                        self.logger.info(f"嵌套iframe {i+1}: class='{nested_class}', src='{nested_src}'")
                        
                        # 检查是否是视频iframe
                        if "ans-insertvideo-online" in (nested_class or ""):
                            self.logger.info(f"找到视频iframe {i+1}，切换到视频iframe...")
                            self.driver.switch_to.frame(nested_iframe)
                            time.sleep(2)
                            
                            # 在视频iframe中查找播放按钮
                            play_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".vjs-big-play-button")
                            if len(play_buttons) > 0:
                                self.logger.info(f"在视频iframe中找到 {len(play_buttons)} 个播放按钮")
                                return True
                            else:
                                # 切回主iframe
                                self.driver.switch_to.parent_frame()
                        
                    except Exception as e:
                        self.logger.error(f"处理嵌套iframe {i+1} 失败: {e}")
                        # 确保切回主iframe
                        try:
                            self.driver.switch_to.parent_frame()
                        except:
                            pass
                
                # 如果没找到视频iframe，切回主文档
                self.driver.switch_to.default_content()
            
            # 备用方案：检查所有iframe
            self.logger.info("使用备用方案检查所有iframe...")
            for i, iframe in enumerate(iframes):
                try:
                    iframe_src = iframe.get_attribute("src")
                    iframe_id = iframe.get_attribute("id")
                    iframe_name = iframe.get_attribute("name")
                    
                    self.logger.info(f"备用检查iframe {i+1}: id='{iframe_id}', name='{iframe_name}', src='{iframe_src}'")
                    
                    # 切换到iframe
                    self.driver.switch_to.frame(iframe)
                    time.sleep(2)
                    
                    # 在iframe中查找视频相关元素
                    video_elements = self.driver.find_elements(By.CSS_SELECTOR, ".vjs-big-play-button")
                    
                    if len(video_elements) > 0:
                        self.logger.info(f"在iframe {i+1} 中找到 {len(video_elements)} 个视频相关元素")
                        return True
                    else:
                        # 切回主文档
                        self.driver.switch_to.default_content()
                        
                except Exception as e:
                    self.logger.error(f"处理iframe {i+1} 失败: {e}")
                    self.driver.switch_to.default_content()
            
            self.logger.info("未找到包含视频元素的iframe")
            return False
            
        except Exception as e:
            self.logger.error(f"切换iframe失败: {e}")
            return False
    
    def run(self):
        """运行测试"""
        try:
            self.logger.info("开始播放按钮测试...")
            
            if not self.setup_driver():
                return False
            
            if not self.login():
                return False
            
            if not self.find_and_test_course():
                return False
            
            self.logger.info("播放按钮测试完成！")
            return True
            
        except Exception as e:
            self.logger.error(f"测试过程出错: {e}")
            return False
        
        finally:
            if self.driver:
                input("按回车键关闭浏览器...")
                self.driver.quit()

if __name__ == "__main__":
    tester = PlayButtonTester()
    tester.run() 