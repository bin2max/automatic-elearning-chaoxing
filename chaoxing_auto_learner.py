import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chaoxing_auto_learner.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ChaoxingAutoLearner:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        try:
            chrome_options = Options()
            if Config.BROWSER_HEADLESS:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 尝试多种方式获取ChromeDriver
            driver_path = None
            try:
                # 方法1: 优先使用项目根目录的chromedriver.exe
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                chromedriver_path = os.path.join(current_dir, "chromedriver.exe")
                
                if os.path.exists(chromedriver_path):
                    self.logger.info(f"使用本地ChromeDriver: {chromedriver_path}")
                    service = Service(chromedriver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver_path = chromedriver_path
                else:
                    self.logger.info("本地ChromeDriver不存在，尝试其他方法...")
                    # 方法2: 使用webdriver-manager自动下载
                    driver_path = ChromeDriverManager().install()
                    self.logger.info(f"使用webdriver-manager下载的驱动: {driver_path}")
            except Exception as e1:
                self.logger.warning(f"本地ChromeDriver和webdriver-manager都失败: {e1}")
                try:
                    # 方法3: 尝试使用系统PATH中的chromedriver
                    from selenium.webdriver.chrome.service import Service as ChromeService
                    service = ChromeService()
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.logger.info("使用系统PATH中的ChromeDriver")
                except Exception as e2:
                    self.logger.warning(f"系统PATH中的ChromeDriver不可用: {e2}")
                    try:
                        # 方法4: 尝试使用Chrome for Testing
                        from webdriver_manager.chrome import ChromeDriverManager
                        driver_path = ChromeDriverManager(chrome_type="chromium").install()
                        self.logger.info(f"使用Chrome for Testing驱动: {driver_path}")
                    except Exception as e3:
                        self.logger.error(f"所有ChromeDriver获取方法都失败: {e3}")
                        raise Exception("无法获取ChromeDriver，请手动下载并安装")
            
            if driver_path:
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.implicitly_wait(Config.IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
            self.wait = WebDriverWait(self.driver, Config.IMPLICIT_WAIT)
            
            self.logger.info("浏览器驱动设置成功")
            return True
            
        except Exception as e:
            self.logger.error(f"设置浏览器驱动失败: {e}")
            self.logger.error("请尝试以下解决方案:")
            self.logger.error("1. 手动下载ChromeDriver: https://chromedriver.chromium.org/")
            self.logger.error("2. 将ChromeDriver放在项目目录或系统PATH中")
            self.logger.error("3. 或者降级Chrome浏览器版本")
            return False
    
    def login(self):
        """登录超星平台"""
        try:
            self.logger.info("开始登录超星平台...")
            self.driver.get(Config.COURSE_URL)
            
            # 等待登录页面加载
            time.sleep(3)
            
            # 检查是否需要登录
            try:
                username_input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, Config.SELECTORS["login_username"]))
                )
                
                # 输入用户名和密码
                username_input.clear()
                username_input.send_keys(Config.USERNAME)
                
                password_input = self.driver.find_element(By.CSS_SELECTOR, Config.SELECTORS["login_password"])
                password_input.clear()
                password_input.send_keys(Config.PASSWORD)
                
                # 点击登录按钮
                login_button = self.driver.find_element(By.CSS_SELECTOR, Config.SELECTORS["login_button"])
                login_button.click()
                
                self.logger.info("登录信息已提交，等待页面跳转...")
                time.sleep(5)
                
            except TimeoutException:
                self.logger.info("未发现登录页面，可能已经登录或页面结构不同")
            
            self.logger.info("登录流程完成")
            return True
            
        except Exception as e:
            self.logger.error(f"登录失败: {e}")
            return False
    
    def navigate_to_catalog(self):
        """导航到课程目录"""
        try:
            self.logger.info("导航到课程目录...")
            
            # 确保在主文档中查找目录按钮
            try:
                # 检查是否在iframe中
                current_frame = self.driver.execute_script("return window.frameElement;")
                if current_frame:
                    self.logger.info("当前在iframe中，切回主文档导航到目录...")
                    self.driver.switch_to.default_content()
                    time.sleep(1)
            except:
                pass
            
            # 等待页面加载
            time.sleep(2)
            
            # 点击目录标签
            catalog_tab = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, Config.SELECTORS["catalog_item"]))
            )
            catalog_tab.click()
            
            time.sleep(3)
            self.logger.info("已进入课程目录")
            return True
            
        except Exception as e:
            self.logger.error(f"导航到目录失败: {e}")
            return False
    
    def retry_operation(self, operation, max_retries=3, operation_name="操作"):
        """重试操作，处理stale element等问题"""
        for attempt in range(max_retries):
            try:
                return operation()
            except StaleElementReferenceException as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"{operation_name}失败，元素已过期: {e}")
                    raise e
                self.logger.warning(f"{operation_name}遇到stale element，重试中... (尝试 {attempt + 1}/{max_retries})")
                time.sleep(2)
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"{operation_name}失败: {e}")
                    raise e
                self.logger.warning(f"{operation_name}失败，重试中... (尝试 {attempt + 1}/{max_retries})")
                time.sleep(2)
    
    def get_uncompleted_courses(self):
        """获取未完成的课程列表"""
        try:
            self.logger.info("获取未完成的课程列表...")
            uncompleted_courses = []
            
            # 等待页面完全加载
            time.sleep(2)
            
            # 直接查找所有带有待完成任务点的课程
            # 使用XPath查找：catalog_points_yi prevTips元素前面的posCatalog_name元素
            xpath_selector = "//span[@class='catalog_points_yi prevTips']/preceding-sibling::span[@class='posCatalog_name'][1]"
            
            try:
                uncompleted_elements = self.driver.find_elements(By.XPATH, xpath_selector)
                self.logger.info(f"使用XPath找到 {len(uncompleted_elements)} 个未完成课程")
                
                for i, element in enumerate(uncompleted_elements):
                    try:
                        # 获取课程信息
                        course_title = element.get_attribute("title")
                        course_text = element.text.strip()
                        onclick = element.get_attribute("onclick")
                        
                        # 获取章节编号
                        chapter_number = ""
                        try:
                            sbar_element = element.find_element(By.CSS_SELECTOR, "em.posCatalog_sbar")
                            chapter_number = sbar_element.text.strip()
                        except:
                            pass
                        
                        uncompleted_courses.append({
                            'element': element,
                            'title': course_title or course_text,
                            'onclick': onclick,
                            'chapter_number': chapter_number,
                            'index': i
                        })
                        
                        self.logger.info(f"发现未完成课程 {i+1}: {course_title or course_text} ({chapter_number})")
                        
                    except Exception as e:
                        self.logger.warning(f"处理未完成课程 {i} 时出错: {e}")
                        continue
                
            except Exception as e:
                self.logger.warning(f"XPath查找失败，尝试备用方法: {e}")
                
                # 备用方法：查找所有课程，然后检查后面的元素
                all_courses = self.driver.find_elements(By.CSS_SELECTOR, Config.SELECTORS["course"])
                self.logger.info(f"备用方法找到 {len(all_courses)} 个课程")
                
                for i, course in enumerate(all_courses):
                    try:
                        # 检查课程后面是否有待完成任务点
                        # 使用JavaScript查找下一个兄弟元素
                        has_pending_task = self.driver.execute_script("""
                            var element = arguments[0];
                            var nextSibling = element.nextElementSibling;
                            return nextSibling && nextSibling.className.includes('catalog_points_yi prevTips');
                        """, course)
                        
                        if has_pending_task:
                            course_title = course.get_attribute("title")
                            course_text = course.text.strip()
                            onclick = course.get_attribute("onclick")
                            
                            # 获取章节编号
                            chapter_number = ""
                            try:
                                sbar_element = course.find_element(By.CSS_SELECTOR, "em.posCatalog_sbar")
                                chapter_number = sbar_element.text.strip()
                            except:
                                pass
                            
                            uncompleted_courses.append({
                                'element': course,
                                'title': course_title or course_text,
                                'onclick': onclick,
                                'chapter_number': chapter_number,
                                'index': i
                            })
                            
                            self.logger.info(f"发现未完成课程 {len(uncompleted_courses)}: {course_title or course_text} ({chapter_number})")
                            
                    except Exception as e:
                        self.logger.warning(f"检查课程 {i} 时出错: {e}")
                        continue
            
            self.logger.info(f"共发现 {len(uncompleted_courses)} 个未完成课程")
            return uncompleted_courses
            
        except Exception as e:
            self.logger.error(f"获取未完成课程列表失败: {e}")
            return []
    
    def study_course(self, course_info):
        """学习指定课程"""
        try:
            course_title = course_info['title']
            chapter_number = course_info.get('chapter_number', '')
            course_index = course_info.get('index', 0)
            
            self.logger.info(f"开始学习课程: {course_title} ({chapter_number})")
            
            # 重新导航到目录
            if not self.navigate_to_catalog():
                self.logger.error("无法导航到目录")
                return False
            
            # 重新获取课程元素
            try:
                # 使用XPath重新查找该课程
                xpath_selector = "//span[@class='catalog_points_yi prevTips']/preceding-sibling::span[@class='posCatalog_name'][1]"
                uncompleted_elements = self.driver.find_elements(By.XPATH, xpath_selector)
                
                if course_index >= len(uncompleted_elements):
                    self.logger.error(f"课程索引超出范围: {course_index}")
                    return False
                
                course_element = uncompleted_elements[course_index]
                
                # 滚动到课程位置并等待
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", course_element)
                time.sleep(3)
                
                # 获取onclick事件内容
                onclick = course_info.get('onclick', '')
                self.logger.info(f"课程onclick事件: {onclick}")
                
                # 尝试多种点击方法
                click_success = False
                
                # 方法1: 使用onclick事件（最可靠）
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
                        self.driver.execute_script("arguments[0].click();", course_element)
                        click_success = True
                        self.logger.info("方法2: JavaScript点击成功")
                    except Exception as e:
                        self.logger.warning(f"方法2失败: {e}")
                
                # 方法3: 直接点击（最后尝试）
                if not click_success:
                    try:
                        self.logger.info("尝试方法3: 直接点击")
                        # 确保元素在视图中
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", course_element)
                        time.sleep(2)
                        
                        # 等待元素可交互
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, f"({xpath_selector})[{course_index + 1}]"))
                        )
                        
                        course_element.click()
                        click_success = True
                        self.logger.info("方法3: 直接点击成功")
                    except Exception as e:
                        self.logger.warning(f"方法3失败: {e}")
                
                if not click_success:
                    self.logger.error("所有点击方法都失败")
                    return False
                
                self.logger.info("已点击课程，等待页面加载...")
                time.sleep(Config.VIDEO_WAIT_TIME)
                
            except Exception as e:
                self.logger.error(f"重新获取课程元素失败: {e}")
                # 尝试备用方法：通过onclick直接执行
                try:
                    onclick = course_info.get('onclick', '')
                    if onclick:
                        self.logger.info("尝试通过onclick执行课程...")
                        self.driver.execute_script(onclick)
                        time.sleep(Config.VIDEO_WAIT_TIME)
                    else:
                        return False
                except Exception as e2:
                    self.logger.error(f"onclick执行也失败: {e2}")
                    return False
            
            # 等待视频播放器加载
            try:
                self.logger.info("等待视频播放器加载...")
                
                # 检查并切换到iframe
                iframe_found = self.switch_to_video_iframe()
                if not iframe_found:
                    self.logger.warning("未找到视频iframe，继续在主文档中查找")
                
                # 增加等待时间，确保视频播放器完全加载
                time.sleep(5)
                
                # 在视频iframe中查找播放按钮（与测试程序保持一致）
                play_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".vjs-big-play-button")
                self.logger.info(f"找到 {len(play_buttons)} 个播放按钮")
                
                if len(play_buttons) > 0:
                    # 找到可用的播放按钮
                    for i, button in enumerate(play_buttons):
                        class_name = button.get_attribute("class")
                        title = button.get_attribute("title")
                        is_displayed = button.is_displayed()
                        is_enabled = button.is_enabled()
                        
                        self.logger.info(f"播放按钮 {i+1}: class='{class_name}', title='{title}', 可见={is_displayed}, 启用={is_enabled}")
                        
                        if is_displayed and is_enabled:
                            self.logger.info("✅ 找到可用的播放按钮！")
                            
                            # 尝试点击播放按钮
                            try:
                                self.logger.info("尝试点击播放按钮...")
                                button.click()
                                self.logger.info("✅ 播放按钮点击成功！")
                                
                                # 设置播放速度为2x
                                time.sleep(Config.PLAYBACK_SPEED_WAIT)
                                self.set_playback_speed()
                                
                                # 等待学习完成（多种判断方式）
                                self.logger.info("🎯 开始等待课程完成检测...")
                                completion_result = self.wait_for_course_completion()
                                
                                if completion_result:
                                    self.logger.info(f"✅ 课程 {course_title} 学习完成")
                                else:
                                    self.logger.warning(f"⚠️ 课程 {course_title} 可能未完成，但继续下一个课程")
                                
                                # 切回主文档，准备下一个课程
                                self.driver.switch_to.default_content()
                                return completion_result
                                
                            except Exception as e:
                                self.logger.error(f"播放按钮点击失败: {e}")
                                continue
                    
                    self.logger.error("所有播放按钮都无法点击")
                    return False
                else:
                    self.logger.error("未找到播放按钮，开始调试...")
                    self.debug_play_button()
                    return False
                
            except TimeoutException:
                self.logger.warning(f"课程 {course_title} 可能已经完成或无法播放")
                return True
                
        except Exception as e:
            self.logger.error(f"学习课程 {course_title} 失败: {e}")
            return False
    
    def set_playback_speed(self):
        """设置播放速度为2x"""
        try:
            # 确保在主文档中查找播放速度控制
            self.logger.info("设置播放速度...")
            
            # 如果当前在iframe中，需要切回主文档
            try:
                # 检查是否在iframe中
                current_frame = self.driver.execute_script("return window.frameElement;")
                if current_frame:
                    self.logger.info("当前在iframe中，切回主文档设置播放速度...")
                    self.driver.switch_to.default_content()
                    time.sleep(1)
            except:
                pass
            
            # 查找播放速度控制
            playback_rate_elements = self.driver.find_elements(By.CSS_SELECTOR, Config.SELECTORS["playback_rate"])
            
            if len(playback_rate_elements) == 0:
                self.logger.warning("在主文档中未找到播放速度控制元素")
                return False
            
            for element in playback_rate_elements:
                try:
                    current_speed = element.text.strip()
                    self.logger.info(f"当前播放速度: {current_speed}")
                    
                    if current_speed != Config.PLAYBACK_SPEED:
                        # 点击播放速度控制
                        element.click()
                        time.sleep(1)
                        
                        # 查找并点击2x选项
                        speed_options = self.driver.find_elements(By.CSS_SELECTOR, ".vjs-playback-rate .vjs-menu-item")
                        for option in speed_options:
                            if Config.PLAYBACK_SPEED in option.text:
                                option.click()
                                self.logger.info(f"播放速度已设置为 {Config.PLAYBACK_SPEED}")
                                return True
                        
                        self.logger.warning("未找到2x播放速度选项")
                    else:
                        self.logger.info(f"播放速度已经是 {Config.PLAYBACK_SPEED}")
                        return True
                        
                except Exception as e:
                    self.logger.warning(f"处理播放速度元素时出错: {e}")
                    continue
            
            self.logger.warning("未找到可用的播放速度控制元素")
            return False
            
        except Exception as e:
            self.logger.warning(f"设置播放速度失败: {e}")
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
                        
                        # 检查是否是视频iframe - 扩展检查条件
                        if (nested_class and "ans-insertvideo-online" in nested_class) or \
                           (nested_src and ("video" in nested_src.lower() or "player" in nested_src.lower())):
                            self.logger.info(f"找到视频iframe {i+1}，切换到视频iframe...")
                            self.driver.switch_to.frame(nested_iframe)
                            time.sleep(2)
                            
                            # 在视频iframe中查找视频元素
                            video_elements = self.driver.find_elements(By.CSS_SELECTOR, "video, .video-js, .fullScreenContainer")
                            if len(video_elements) > 0:
                                self.logger.info(f"在视频iframe中找到 {len(video_elements)} 个视频元素")
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
            
            # 备用方案：检查所有iframe，更仔细地查找视频元素
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
                    
                    # 在iframe中查找视频相关元素 - 更全面的检查
                    video_selectors = [
                        "video",  # HTML5 video元素
                        ".video-js",  # Video.js播放器
                        ".fullScreenContainer",  # 全屏容器
                        ".vjs-big-play-button",  # 播放按钮
                        "[class*='video']",  # 包含video的class
                        "[class*='player']",  # 包含player的class
                        "[class*='vjs']"  # Video.js相关元素
                    ]
                    
                    video_elements = []
                    for selector in video_selectors:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        video_elements.extend(elements)
                    
                    if len(video_elements) > 0:
                        self.logger.info(f"在iframe {i+1} 中找到 {len(video_elements)} 个视频相关元素")
                        # 进一步验证：检查是否有真正的视频元素
                        for element in video_elements:
                            tag_name = element.tag_name.lower()
                            class_name = element.get_attribute("class") or ""
                            if tag_name == "video" or "video" in class_name or "player" in class_name:
                                self.logger.info(f"确认找到视频元素: {tag_name}, class='{class_name}'")
                                return True
                        
                        # 如果没有确认的视频元素，切回主文档继续检查
                        self.driver.switch_to.default_content()
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
    
    def debug_play_button(self):
        """调试播放按钮"""
        try:
            self.logger.info("开始调试播放按钮...")
            
            # 检查当前是否在iframe中
            current_frame = "主文档"
            try:
                # 尝试获取当前iframe信息
                current_frame_element = self.driver.execute_script("return window.frameElement;")
                if current_frame_element:
                    iframe_id = current_frame_element.get_attribute("id")
                    iframe_name = current_frame_element.get_attribute("name")
                    current_frame = f"iframe: {iframe_id or iframe_name or 'unnamed'}"
                    self.logger.info(f"当前在 {current_frame} 中")
                else:
                    self.logger.info("当前在主文档中")
            except:
                self.logger.info("当前在主文档中")
            
            # 首先检查fullScreenContainer是否存在
            try:
                fullscreen_container = self.driver.find_element(By.CSS_SELECTOR, ".fullScreenContainer")
                self.logger.info(f"在 {current_frame} 中找到fullScreenContainer元素")
                
                # 在fullScreenContainer内查找播放按钮
                container_selectors = [
                    ".fullScreenContainer button.vjs-big-play-button",
                    ".fullScreenContainer .vjs-big-play-button",
                    ".fullScreenContainer button[title*='播放']",
                    ".fullScreenContainer button[class*='play']",
                    ".fullScreenContainer .vjs-play-button"
                ]
                
                for i, selector in enumerate(container_selectors):
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        self.logger.info(f"fullScreenContainer内选择器 {i+1} '{selector}' 找到 {len(elements)} 个元素")
                        
                        if len(elements) > 0:
                            for j, element in enumerate(elements[:3]):  # 只显示前3个
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
                "button[aria-label*='播放']"
            ]
            
            for i, selector in enumerate(selectors):
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"选择器 {i+1} '{selector}' 找到 {len(elements)} 个元素")
                    
                    if len(elements) > 0:
                        for j, element in enumerate(elements[:3]):  # 只显示前3个
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
                                
                            except Exception as e:
                                self.logger.error(f"  获取元素 {j+1} 信息失败: {e}")
                                
                except Exception as e:
                    self.logger.error(f"选择器 {i+1} 执行失败: {e}")
            
            # 查找视频播放器容器
            video_containers = self.driver.find_elements(By.CSS_SELECTOR, ".video-js, .vjs-tech, video")
            self.logger.info(f"找到 {len(video_containers)} 个视频播放器容器")
            
            return True
            
        except Exception as e:
            self.logger.error(f"调试播放按钮失败: {e}")
            return False
    
    def wait_for_face_recognition(self):
        """等待人脸识别弹窗出现并处理"""
        try:
            self.logger.info("等待人脸识别弹窗...")
            
            # 确保在主文档中查找人脸识别弹窗
            try:
                # 检查是否在iframe中
                current_frame = self.driver.execute_script("return window.frameElement;")
                if current_frame:
                    self.logger.info("当前在iframe中，切回主文档等待人脸识别弹窗...")
                    self.driver.switch_to.default_content()
                    time.sleep(1)
            except:
                pass
            
            # 等待人脸识别弹窗出现
            face_recognition = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, Config.SELECTORS["face_recognition"]))
            )
            
            self.logger.info("检测到人脸识别弹窗，课程学习完成")
            time.sleep(Config.FACE_RECOGNITION_WAIT)
            
            # 尝试关闭人脸识别弹窗
            self.close_face_recognition_popup()
            
            return True
            
        except TimeoutException:
            self.logger.warning("未检测到人脸识别弹窗，可能课程已自动完成")
            return True
        except Exception as e:
            self.logger.error(f"等待人脸识别时出错: {e}")
            return False
    
    def wait_for_course_completion(self):
        """等待课程完成（多种判断方式）"""
        try:
            self.logger.info("🔍 开始课程完成检测流程...")
            self.logger.info(f"⏰ 总等待时间: {Config.FACE_RECOGNITION_TIMEOUT}秒")
            
            # 确保在主文档中查找完成标志
            try:
                # 检查是否在iframe中
                current_frame = self.driver.execute_script("return window.frameElement;")
                if current_frame:
                    self.logger.info("当前在iframe中，切回主文档检查课程完成状态...")
                    self.driver.switch_to.default_content()
                    time.sleep(1)
            except:
                pass
            
            # 开始持续监控课程完成状态
            start_time = time.time()
            check_interval = 30  # 每30秒检查一次
            last_check_time = 0
            last_video_status = "unknown"
            
            while time.time() - start_time < Config.FACE_RECOGNITION_TIMEOUT:
                current_time = time.time()
                elapsed_time = current_time - start_time
                
                # 每30秒检查一次视频状态
                if current_time - last_check_time >= check_interval:
                    self.logger.info(f"⏰ 已等待 {elapsed_time:.0f} 秒，检查课程状态...")
                    last_check_time = current_time
                    
                    # 检查视频播放状态
                    video_status = self.check_video_status()
                    last_video_status = video_status
                    
                    if video_status == "completed":
                        self.logger.info("✅ 检测到视频播放完成")
                        break
                    elif video_status == "playing":
                        self.logger.info("📺 视频正在播放中...")
                    elif video_status == "paused":
                        self.logger.info("⏸️ 视频已暂停")
                    else:
                        self.logger.info("❓ 视频状态未知")
                
                # 根据视频状态决定是否检查人脸识别弹窗
                if last_video_status == "playing":
                    # 视频正在播放，不检查弹窗，继续等待
                    self.logger.info("📺 视频正在播放中，不检查人脸识别弹窗...")
                    time.sleep(5)
                    continue
                elif last_video_status == "completed":
                    # 视频播放完成，检查人脸识别弹窗
                    self.logger.info("✅ 视频播放完成，检查人脸识别弹窗...")
                    if self.check_face_recognition_popup():
                        self.logger.info("✅ 检测到人脸识别弹窗，课程学习完成")
                        
                        # 短暂等待弹窗稳定
                        time.sleep(Config.FACE_RECOGNITION_WAIT)
                        
                        # 关闭人脸识别弹窗
                        if self.close_face_recognition_popup():
                            self.logger.info("✅ 人脸识别弹窗已关闭，准备学习下一个课程")
                            return True
                        else:
                            self.logger.error("❌ 关闭人脸识别弹窗失败，课程可能未真正完成")
                            # 继续等待，不要立即返回失败
                            self.logger.info("⏳ 继续等待，尝试其他方式关闭弹窗...")
                elif last_video_status == "paused":
                    # 视频已暂停，检查人脸识别弹窗
                    self.logger.info("⏸️ 视频已暂停，检查人脸识别弹窗...")
                    if self.check_face_recognition_popup():
                        self.logger.info("✅ 检测到人脸识别弹窗，课程学习完成")
                        
                        # 短暂等待弹窗稳定
                        time.sleep(Config.FACE_RECOGNITION_WAIT)
                        
                        # 关闭人脸识别弹窗
                        if self.close_face_recognition_popup():
                            self.logger.info("✅ 人脸识别弹窗已关闭，准备学习下一个课程")
                            return True
                        else:
                            self.logger.error("❌ 关闭人脸识别弹窗失败，课程可能未真正完成")
                            # 继续等待，不要立即返回失败
                            self.logger.info("⏳ 继续等待，尝试其他方式关闭弹窗...")
                else:
                    # 视频状态未知，谨慎检查弹窗
                    self.logger.info("❓ 视频状态未知，谨慎检查人脸识别弹窗...")
                    if self.check_face_recognition_popup():
                        self.logger.info("✅ 检测到人脸识别弹窗，课程学习完成")
                        
                        # 短暂等待弹窗稳定
                        time.sleep(Config.FACE_RECOGNITION_WAIT)
                        
                        # 关闭人脸识别弹窗
                        if self.close_face_recognition_popup():
                            self.logger.info("✅ 人脸识别弹窗已关闭，准备学习下一个课程")
                            return True
                        else:
                            self.logger.error("❌ 关闭人脸识别弹窗失败，课程可能未真正完成")
                            # 继续等待，不要立即返回失败
                            self.logger.info("⏳ 继续等待，尝试其他方式关闭弹窗...")
                
                time.sleep(5)  # 短暂等待后继续检查
            
            # 超时检查
            if time.time() - start_time >= Config.FACE_RECOGNITION_TIMEOUT:
                self.logger.warning(f"⏰ 等待超时 ({Config.FACE_RECOGNITION_TIMEOUT}秒)，课程可能已完成")
                return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"等待课程完成时发生错误: {e}")
            return False

    def check_video_status(self):
        """检查视频播放状态"""
        try:
            # 切换到视频iframe
            if not self.switch_to_video_iframe():
                return "unknown"
            
            # 查找视频元素
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, "video")
            if len(video_elements) == 0:
                return "unknown"
            
            for video in video_elements:
                try:
                    current_time = video.get_property("currentTime")
                    duration = video.get_property("duration")
                    paused = video.get_property("paused")
                    ended = video.get_property("ended")
                    
                    self.logger.info(f"视频状态: 当前时间={current_time:.1f}s, 总时长={duration:.1f}s, 暂停={paused}, 结束={ended}")
                    
                    if ended or (duration > 0 and current_time >= duration - 1):
                        return "completed"
                    elif paused:
                        return "paused"
                    else:
                        return "playing"
                        
                except Exception as e:
                    self.logger.warning(f"检查视频状态失败: {e}")
                    continue
            
            return "unknown"
            
        except Exception as e:
            self.logger.warning(f"检查视频状态时发生错误: {e}")
            return "unknown"

    def check_face_recognition_popup(self):
        """检查人脸识别弹窗是否存在"""
        try:
            # 确保在主文档中
            try:
                current_frame = self.driver.execute_script("return window.frameElement;")
                if current_frame:
                    self.driver.switch_to.default_content()
                    time.sleep(1)
            except:
                pass
            
            # 首先检查是否有视频正在播放 - 如果有，不检查弹窗
            try:
                # 尝试切换到视频iframe检查视频状态
                if self.switch_to_video_iframe():
                    video_elements = self.driver.find_elements(By.CSS_SELECTOR, "video")
                    for video in video_elements:
                        try:
                            paused = video.get_property("paused")
                            ended = video.get_property("ended")
                            current_time = video.get_property("currentTime")
                            duration = video.get_property("duration")
                            
                            # 如果视频正在播放且未结束，不检查弹窗
                            if not paused and not ended and current_time > 0 and duration > 0:
                                self.logger.info(f"检测到视频正在播放 (时间: {current_time:.1f}s/{duration:.1f}s)，跳过弹窗检查")
                                self.driver.switch_to.default_content()
                                return False
                        except:
                            continue
                    
                    # 切回主文档
                    self.driver.switch_to.default_content()
            except:
                pass
            
            # 优先检查弹窗元素是否真正可见
            selectors_to_check = [
                Config.SELECTORS["face_recognition"],  # 主选择器
                "div.maskDiv1",  # 简化选择器
                "[class*='chapterVideoFaceQrMaskDiv']",  # 包含选择器
                "[class*='maskDiv1']",  # 包含选择器2
                "div[class*='FaceQrMaskDiv']",  # 包含选择器3
                "div.popDiv1",  # 基于实际元素的class
                "[class*='faceCollectQrPopVideo']",  # 基于实际元素的class
                "[class*='faceRecognition_0']"  # 基于实际元素的class
            ]
            
            # 检查是否有可见的弹窗元素
            visible_popup_found = False
            for selector in selectors_to_check:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > 0:
                        for element in elements:
                            try:
                                if element.is_displayed():
                                    # 进一步检查：确保元素真正可见且不是隐藏的
                                    style = element.get_attribute("style") or ""
                                    if "display: none" not in style and "visibility: hidden" not in style:
                                        self.logger.info(f"✅ 找到可见的人脸识别弹窗: {selector}")
                                        visible_popup_found = True
                                        break
                            except:
                                continue
                    if visible_popup_found:
                        break
                except:
                    continue
            
            # 如果找到可见的弹窗元素，直接返回True
            if visible_popup_found:
                return True
            
            # 如果没有找到可见的弹窗元素，再检查页面文本（作为辅助验证）
            try:
                page_source = self.driver.page_source
                if any(text in page_source for text in ["人脸信息采集", "请使用手机APP采集人脸信息", "请扫描下方二维码"]):
                    self.logger.info("⚠️ 页面源码中包含人脸识别相关文本，但未找到可见的弹窗元素")
                    # 进一步检查：文本是否在隐藏的元素中
                    hidden_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[style*='display: none'], div[style*='display:none']")
                    for element in hidden_elements:
                        try:
                            element_text = element.text
                            if any(text in element_text for text in ["人脸信息采集", "请使用手机APP采集人脸信息"]):
                                self.logger.info("✅ 在隐藏元素中找到人脸识别文本，可能是隐藏的弹窗")
                                return True
                        except:
                            continue
                    
                    # 如果文本不在隐藏元素中，可能是残留，不认为是弹窗
                    self.logger.info("❌ 页面文本可能是残留，不认为是弹窗")
                    return False
            except:
                pass
            
            return False
            
        except Exception as e:
            self.logger.warning(f"检查人脸识别弹窗时发生错误: {e}")
            return False
    
    def close_face_recognition_popup(self):
        """关闭人脸识别弹窗"""
        try:
            self.logger.info("尝试关闭人脸识别弹窗...")
            
            # 方法1: 直接执行onclick事件（window.location.reload()）
            try:
                self.logger.info("尝试执行页面刷新...")
                self.driver.execute_script("window.location.reload();")
                self.logger.info("✅ 方法1: 执行页面刷新成功")
                time.sleep(5)
                self.wait_for_page_load()
                
                # 验证弹窗是否真正关闭
                if self.verify_popup_closed():
                    self.logger.info("✅ 验证成功：弹窗已真正关闭")
                    return True
                else:
                    self.logger.warning("⚠️ 验证失败：弹窗可能未关闭，尝试方法2...")
                    
            except Exception as e:
                self.logger.warning(f"方法1失败: {e}")
            
            # 方法2: 尝试查找其他关闭按钮选择器
            try:
                self.logger.info("尝试其他关闭按钮选择器...")
                alternative_selectors = [
                    "a.popClose.fr",
                    "a[onclick*='window.location.reload']",
                    "a[onclick*='reload']",
                    ".popClose",
                    "a.popClose"
                ]
                
                for selector in alternative_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                self.logger.info(f"找到可见的关闭按钮: {selector}")
                                element.click()
                                self.logger.info(f"✅ 方法2: 使用选择器 {selector} 点击成功")
                                time.sleep(3)
                                self.wait_for_page_load()
                                
                                # 验证弹窗是否真正关闭
                                if self.verify_popup_closed():
                                    self.logger.info("✅ 验证成功：弹窗已真正关闭")
                                    return True
                                else:
                                    self.logger.warning(f"⚠️ 验证失败：选择器 {selector} 点击后弹窗未关闭")
                                    break
                    except:
                        continue
                        
            except Exception as e:
                self.logger.warning(f"方法2失败: {e}")
            
            # 方法3: 尝试隐藏弹窗
            try:
                self.logger.info("尝试隐藏弹窗...")
                self.driver.execute_script("""
                    var elements = document.querySelectorAll('div[class*="maskDiv1"], div[class*="popDiv1"]');
                    for (var i = 0; i < elements.length; i++) {
                        elements[i].style.display = 'none';
                    }
                """)
                self.logger.info("✅ 方法3: 隐藏弹窗成功")
                
                # 验证弹窗是否真正隐藏
                if self.verify_popup_closed():
                    self.logger.info("✅ 验证成功：弹窗已真正隐藏")
                    return True
                else:
                    self.logger.warning("⚠️ 验证失败：弹窗可能未隐藏")
                    
            except Exception as e:
                self.logger.warning(f"方法3失败: {e}")
            
            # 方法4: 尝试导航到课程目录作为最后手段
            try:
                self.logger.info("尝试方法4: 导航到课程目录...")
                if self.navigate_to_catalog():
                    self.logger.info("✅ 方法4: 导航到课程目录成功，弹窗问题已解决")
                    return True
                else:
                    self.logger.warning("⚠️ 方法4: 导航到课程目录失败")
            except Exception as e:
                self.logger.warning(f"方法4失败: {e}")
            
            self.logger.error("❌ 所有关闭方法都失败")
            return False
            
        except Exception as e:
            self.logger.error(f"关闭人脸识别弹窗时出错: {e}")
            return False

    def verify_popup_closed(self):
        """验证弹窗是否真正关闭"""
        try:
            # 等待一下让页面稳定
            time.sleep(2)
            
            # 检查弹窗是否还存在且可见
            selectors_to_check = [
                Config.SELECTORS["face_recognition"],
                "div.maskDiv1",
                "[class*='chapterVideoFaceQrMaskDiv']",
                "[class*='maskDiv1']",
                "div[class*='FaceQrMaskDiv']",
                "div.popDiv1",
                "[class*='faceCollectQrPopVideo']",
                "[class*='faceRecognition_0']"
            ]
            
            for selector in selectors_to_check:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            self.logger.info(f"❌ 验证失败：弹窗仍然可见 ({selector})")
                            return False
                except:
                    continue
            
            # 检查页面文本是否还包含人脸识别相关内容
            try:
                page_source = self.driver.page_source
                if any(text in page_source for text in ["人脸信息采集", "请使用手机APP采集人脸信息", "请扫描下方二维码"]):
                    self.logger.info("❌ 验证失败：页面仍包含人脸识别相关文本")
                    return False
            except:
                pass
            
            self.logger.info("✅ 验证成功：弹窗已关闭")
            return True
            
        except Exception as e:
            self.logger.warning(f"验证弹窗关闭状态时出错: {e}")
            return False
    
    def wait_for_page_load(self):
        """等待页面加载完成"""
        try:
            # 等待页面加载状态
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)
            self.logger.info("页面加载完成")
        except Exception as e:
            self.logger.warning(f"等待页面加载时出错: {e}")
    
    def run(self):
        """运行自动化学习程序"""
        try:
            self.logger.info("开始运行超星自动化学习程序...")
            
            # 设置浏览器驱动
            if not self.setup_driver():
                return False
            
            # 登录
            if not self.login():
                return False
            
            # 导航到目录
            if not self.navigate_to_catalog():
                return False
            
            # 获取未完成课程
            uncompleted_courses = self.get_uncompleted_courses()
            
            if not uncompleted_courses:
                self.logger.info("所有课程已完成！")
                return True
            
            # 依次学习未完成课程
            for i, course_info in enumerate(uncompleted_courses, 1):
                self.logger.info(f"🎯 学习进度: {i}/{len(uncompleted_courses)} - {course_info['title']}")
                
                # 学习当前课程
                study_result = self.study_course(course_info)
                
                if study_result:
                    self.logger.info(f"✅ 课程 {course_info['title']} 学习完成")
                else:
                    self.logger.warning(f"⚠️ 课程 {course_info['title']} 学习失败，继续下一个")
                    continue
                
                # 学习完成后短暂等待，然后重新获取课程列表
                self.logger.info("⏳ 等待页面稳定，准备获取最新课程列表...")
                time.sleep(5)
                
                # 重新导航到目录并获取最新的未完成课程
                if not self.navigate_to_catalog():
                    self.logger.warning("⚠️ 重新导航到目录失败")
                    continue
                
                # 重新获取未完成课程列表
                remaining_courses = self.get_uncompleted_courses()
                if not remaining_courses:
                    self.logger.info("🎉 所有课程已完成！")
                    break
                else:
                    self.logger.info(f"📋 还有 {len(remaining_courses)} 个课程未完成")
            
            self.logger.info("所有课程学习完成！")
            return True
            
        except Exception as e:
            self.logger.error(f"程序运行出错: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("浏览器已关闭")

if __name__ == "__main__":
    learner = ChaoxingAutoLearner()
    learner.run() 