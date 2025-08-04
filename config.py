# 配置文件
class Config:
    # 登录信息
    USERNAME = "13*********"   #填入自己的账号
    PASSWORD = "********"   #填入自己的密码
    
    # 课程主页URL
    COURSE_URL = "https://mooc1.chaoxing.com/*******"   #填入自己的课程主页URL
    
    # 浏览器配置
    BROWSER_HEADLESS = False  # 设置为True可以无头模式运行
    IMPLICIT_WAIT = 10
    PAGE_LOAD_TIMEOUT = 15
    
    # 学习配置
    PLAYBACK_SPEED = "2x"  # 播放速度
    VIDEO_WAIT_TIME = 18  # 视频加载等待时间（秒）
    FACE_RECOGNITION_WAIT = 10  # 人脸识别弹窗稳定等待时间（秒）
    ELEMENT_WAIT_TIME = 3  # 元素等待时间（秒）
    FACE_RECOGNITION_TIMEOUT = 3600  # 人脸识别弹窗等待超时时间（秒）
    PAGE_LOAD_WAIT = 5  # 页面加载等待时间（秒）
    PLAY_BUTTON_WAIT = 15  # 播放按钮等待时间（秒）
    PLAYBACK_SPEED_WAIT = 20  # 播放速度设置前等待时间（秒）
    
    # 选择器配置
    SELECTORS = {
        "login_username": "#phone",
        "login_password": "#pwd",
        "login_button": "#loginBtn",
        "catalog_item": "li#tit1",
        "chapter": "div.posCatalog_select.firstLayer",
        "section": "span.posCatalog_name",
        "course": "span.posCatalog_name",
        "completed_icon": "span.icon_Completed",
        "pending_task": "span.catalog_points_yi",
                       "play_button": ".fullScreenContainer button.vjs-big-play-button",
               "playback_rate": "div.vjs-playback-rate-value",
               "face_recognition": "div.maskDiv1.chapterVideoFaceQrMaskDiv",
               "face_close_button": "a.popClose.fr",
               "chapter_number": "em.posCatalog_sbar",
               "fullscreen_container": ".fullScreenContainer"
    } 