import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def random_sleep(min_seconds=1, max_seconds=3):
    """随机等待时间，模拟人类行为"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def human_like_typing(element, text):
    """模拟人类输入，逐字符输入"""
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

def scroll_to_element(driver, element):
    """滚动到元素位置"""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)

def wait_for_page_load(driver, timeout=30):
    """等待页面加载完成"""
    try:
        # 等待页面加载状态
        driver.execute_script("return document.readyState") == "complete"
        time.sleep(2)
        return True
    except Exception:
        return False

def check_element_exists(driver, selector, timeout=5):
    """检查元素是否存在"""
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        return element is not None
    except:
        return False

def take_screenshot(driver, filename="screenshot.png"):
    """截图功能"""
    try:
        driver.save_screenshot(filename)
        print(f"截图已保存: {filename}")
        return True
    except Exception as e:
        print(f"截图失败: {e}")
        return False

def handle_popup(driver):
    """处理可能的弹窗"""
    try:
        # 查找并关闭可能的弹窗
        popup_selectors = [
            ".close", ".popup-close", ".modal-close", 
            "button[aria-label='Close']", ".btn-close"
        ]
        
        for selector in popup_selectors:
            try:
                popup = driver.find_element_by_css_selector(selector)
                if popup.is_displayed():
                    popup.click()
                    time.sleep(1)
                    break
            except:
                continue
                
    except Exception as e:
        print(f"处理弹窗时出错: {e}")

def retry_operation(operation, max_retries=3, delay=2):
    """重试操作"""
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"操作失败，{delay}秒后重试... (尝试 {attempt + 1}/{max_retries})")
            time.sleep(delay)
            delay *= 2  # 指数退避

def handle_face_recognition_popup(driver, close_selector="a.popClose.fr"):
    """处理人脸识别弹窗"""
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # 等待关闭按钮出现
        wait = WebDriverWait(driver, 5)
        close_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, close_selector))
        )
        
        # 点击关闭按钮
        close_button.click()
        print("已关闭人脸识别弹窗")
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"处理人脸识别弹窗时出错: {e}")
        return False 