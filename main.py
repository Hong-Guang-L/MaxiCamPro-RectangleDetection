"""
================================================================================
文件名称：main.py
项目名称：2025 年电赛 E 题 - 基于 MaxiCamPro 的矩形识别系统
版本：v2.0.0
作者：电赛团队
日期：2025 年
描述：
    本程序实现基于 MaxiCamPro 平台的矩形目标识别与定位功能。
    主要功能包括：
    1. 实时摄像头图像采集与处理
    2. 多条件融合的矩形检测算法
    3. 透视变换与坐标映射
    4. 触摸屏交互与参数调节
    5. UART 串口数据输出
================================================================================
"""

from maix import image
from maix import display
from maix import app
from maix import time
from maix import camera
from maix import touchscreen
import cv2
import numpy as np
import math
import gc
import os
from uart_lib import SimpleUART
from uart_lib import micu_printf
from uart_lib import bind_variable
from uart_lib import VariableContainer
from uart_lib import clear_variable_bindings


# ============================================================================
# 第一章：配置参数区
# 说明：所有可调节参数集中在此区域，便于调试和优化
# ============================================================================

class DetectionConfig:
    """矩形检测配置参数类"""
    
    # --------------------------- 矩形检测核心参数 ---------------------------
    MIN_CONTOUR_AREA = 500       # 最小轮廓面积（像素），过滤小目标噪声
    MAX_CONTOUR_AREA = 55000     # 最大轮廓面积（像素），过滤大目标干扰
    TARGET_SIDES = 4             # 目标边数（矩形为 4 条边）
    BINARY_THRESHOLD = 66        # 二值化阈值（0-255），用于图像分割
    
    # --------------------------- 几何形状过滤参数 ---------------------------
    # 宽高比过滤（宽/高）
    MIN_ASPECT_RATIO = 0.6       # 最小宽高比（高不超过宽的 1.67 倍）
    MAX_ASPECT_RATIO = 1.7       # 最大宽高比（宽不超过高的 1.7 倍）
    
    # 角度过滤（单位：度）
    MIN_ANGLE = 75               # 最小直角角度（理想矩形为 90°）
    MAX_ANGLE = 105              # 最大直角角度（允许±15°偏差）
    
    # 对边长度一致性参数（比例）
    MIN_OPPOSITE_RATIO = 0.6     # 最小对边比例（允许±40% 偏差）
    MAX_OPPOSITE_RATIO = 1.4     # 最大对边比例
    
    # --------------------------- 透视变换与圆形参数 ---------------------------
    CORRECTED_WIDTH = 200        # 校正后矩形宽度（像素）
    CORRECTED_HEIGHT = 150       # 校正后矩形高度（像素）
    CORRECTED_CENTER = (CORRECTED_WIDTH // 2, CORRECTED_HEIGHT // 2)  # 预定义校正中心
    CIRCLE_RADIUS = 50           # 圆形轨迹半径（像素）
    CIRCLE_NUM_POINTS = 12       # 圆形轨迹点数量
    FALLBACK_CIRCLE_RADIUS = 30  # 无透视变换时的备用半径（像素）
    
    # --------------------------- 触摸按键参数 ---------------------------
    TOUCH_DEBOUNCE = 0.3         # 触摸防抖动时间（秒）
    
    # --------------------------- 屏幕配置（适配不同分辨率） ---------------------------
    SCREEN_WIDTH = 320            # 屏幕宽度
    SCREEN_HEIGHT = 240           # 屏幕高度
    
    # 目标点标记坐标
    TARGET_POINT_X = 166          # 目标点 X 坐标
    TARGET_POINT_Y = 110          # 目标点 Y 坐标
    
    # 虚拟按键定义（格式：[比例_x, 比例_y, 比例_w, 比例_h, 文本, 动作]）
    # 比例范围 0.0-1.0，用于动态计算实际坐标
    BUTTONS_RELATIVE = [
        [0.06, 0.33, 0.14, 0.08, "Center", "center"],    # [x_ratio, y_ratio, w_ratio, h_ratio, text, action]
        [0.36, 0.33, 0.16, 0.08, "Circle", "circle"],
        [0.56, 0.33, 0.08, 0.08, "T-", "thresh_down"],
        [0.66, 0.33, 0.08, 0.08, "T+", "thresh_up"]
    ]
    
    # 触摸响应区域（比例坐标）
    TOUCH_AREAS_RELATIVE = [
        [0.13, 0.72, 0.28, 0.11],    # Center 响应区
        [0.72, 0.69, 0.31, 0.11],    # Circle 响应区
        [0.56, 0.69, 0.16, 0.11],    # T- 响应区
        [0.66, 0.69, 0.16, 0.11]     # T+ 响应区
    ]
    
    @staticmethod
    def calculate_absolute_buttons(screen_width, screen_height):
        """
        根据屏幕尺寸计算绝对按钮坐标
        
        参数:
            screen_width (int): 屏幕宽度
            screen_height (int): 屏幕高度
            
        返回:
            list: 绝对坐标的按钮列表
        """
        absolute_buttons = []
        for btn in DetectionConfig.BUTTONS_RELATIVE:
            x_ratio, y_ratio, w_ratio, h_ratio, text, action = btn
            x = int(x_ratio * screen_width)
            y = int(y_ratio * screen_height)
            w = int(w_ratio * screen_width)
            h = int(h_ratio * screen_height)
            absolute_buttons.append([x, y, w, h, text, action])
        return absolute_buttons
    
    @staticmethod
    def calculate_absolute_touch_areas(screen_width, screen_height):
        """
        根据屏幕尺寸计算绝对触摸区域坐标
        
        参数:
            screen_width (int): 屏幕宽度
            screen_height (int): 屏幕高度
            
        返回:
            list: 绝对坐标的触摸区域列表
        """
        absolute_areas = []
        for area in DetectionConfig.TOUCH_AREAS_RELATIVE:
            x_ratio, y_ratio, w_ratio, h_ratio = area
            x = int(x_ratio * screen_width)
            y = int(y_ratio * screen_height)
            w = int(w_ratio * screen_width)
            h = int(h_ratio * screen_height)
            absolute_areas.append([x, y, w, h])
        return absolute_areas
    
    # --------------------------- UART 串口配置 ---------------------------
    # 使用环境变量配置，如果未设置则使用默认值
    UART_DEVICE = os.environ.get('UART_DEVICE', '/dev/ttyS0')    # 串口设备路径
    UART_BAUDRATE = 115200                                        # 波特率
    UART_FRAME_HEADER = "$$"                                       # 帧头
    UART_FRAME_TAIL = "##"                                         # 帧尾
    
    @staticmethod
    def validate_uart_device_path(path):
        """
        验证串口设备路径的合法性
        
        参数:
            path (str): 设备路径
            
        返回:
            tuple: (is_valid, cleaned_path)
                is_valid (bool): 路径是否合法
                cleaned_path (str): 清理后的路径
        """
        if not path:
            return False, '/dev/ttyS0'
        
        # 检查路径遍历攻击
        if '..' in path:
            return False, '/dev/ttyS0'
        
        # 基本路径验证
        import re
        # 允许的路径模式（Linux 串口设备路径或 Windows COM 端口）
        linux_pattern = r'^/dev/tty(S|USB|ACM)\d+$'
        windows_pattern = r'^COM\d+$'
        
        if re.match(linux_pattern, path) or re.match(windows_pattern, path):
            return True, path
        
        # 如果不是标准格式但也没有安全问题，也允许使用
        return True, path



# ============================================================================
# 第二章：工具函数模块
# 说明：提供几何计算、坐标变换等基础工具函数
# ============================================================================

class GeometryUtils:
    """几何计算工具类"""
    
    @staticmethod
    def generate_circle_points(center, radius, num_points):
        """
        生成圆形轨迹点坐标
        
        参数:
            center (tuple): 圆心坐标 (x, y)
            radius (int): 圆半径（像素）
            num_points (int): 圆周上的点数
            
        返回:
            list: 圆形轨迹点坐标列表 [(x1,y1), (x2,y2), ...]
        """
        circle_points = []
        cx, cy = center
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))
            circle_points.append((x, y))
        return circle_points
    
    @staticmethod
    def calculate_edge_length(p1, p2):
        """
        计算两点间欧几里得距离
        
        参数:
            p1, p2 (np.array): 二维点坐标
            
        返回:
            float: 边的长度
        """
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    
    @staticmethod
    def calculate_angle(p_prev, p_curr, p_next):
        """
        计算三个点形成的夹角（单位：度）
        
        参数:
            p_prev, p_curr, p_next (np.array): 三个连续顶点
            
        返回:
            float: 夹角角度（0-180 度）
        """
        v1 = [p_curr[0] - p_prev[0], p_curr[1] - p_prev[1]]
        v2 = [p_next[0] - p_curr[0], p_next[1] - p_curr[1]]
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        det = v1[0] * v2[1] - v1[1] * v2[0]
        angle = abs(math.degrees(math.atan2(det, dot)))
        return angle


class PerspectiveTransform:
    """透视变换工具类"""
    
    @staticmethod
    def transform(pts, target_width, target_height):
        """
        计算四边形的透视变换矩阵
        
        参数:
            pts (np.array): 四边形四个顶点 (4,2)
            target_width (int): 目标宽度
            target_height (int): 目标高度
            
        返回:
            tuple: (变换矩阵 M, 逆变换矩阵 M_inv, 排序后的源顶点)
        """
        # 顶点排序：左上、右上、右下、左下
        s = pts.sum(axis=1)
        tl = pts[np.argmin(s)]  # 左上角
        br = pts[np.argmax(s)]  # 右下角
        
        diff = np.diff(pts, axis=1)
        tr = pts[np.argmin(diff)]  # 右上角
        bl = pts[np.argmax(diff)]  # 左下角
        
        src_pts = np.array([tl, tr, br, bl], dtype=np.float32)
        
        # 目标顶点坐标
        dst_pts = np.array([
            [0, 0], 
            [target_width-1, 0],
            [target_width-1, target_height-1], 
            [0, target_height-1]
        ], dtype=np.float32)
        
        # 计算透视变换矩阵
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        ret, M_inv = cv2.invert(M)
        
        # 检查逆矩阵计算是否成功
        if ret == 0:
            M_inv = None
        
        return M, M_inv, src_pts


# ============================================================================
# 第三章：矩形检测器模块
# 说明：实现多层级过滤的矩形检测算法
# ============================================================================

class RectangleDetector:
    """矩形检测器类 - 实现多条件融合的矩形识别"""
    
    def __init__(self, config=None):
        """
        初始化检测器
        
        参数:
            config: 配置参数类实例，None 则使用默认配置
        """
        self.config = config if config else DetectionConfig()
        self.kernel = np.ones((3, 3), np.uint8)  # 形态学核（3x3 才有效果）
    
    def detect(self, img, threshold):
        """
        执行矩形检测
        
        参数:
            img (np.array): 输入图像（BGR 格式）
            threshold (int): 二值化阈值
            
        返回:
            list: 检测到的矩形列表 [(approx, area), ...]
        """
        # 1. 图像预处理
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
        # 2. 形态学优化：闭运算填充孔洞，开运算去除噪点
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, self.kernel, iterations=1)
        
        # 3. 查找轮廓
        contours, _ = cv2.findContours(processed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # 4. 多条件过滤矩形
        quads = []
        for cnt in contours:
            result = self._validate_contour(cnt)
            if result is not None:
                quads.append(result)
        
        # 5. 保留面积最大的矩形
        if quads:
            largest_quad = max(quads, key=lambda x: x[1])  # 修正：用 max 选最大面积
            return [largest_quad]
        
        return []
    
    def _validate_contour(self, contour):
        """
        验证轮廓是否为有效矩形（多级过滤）
        
        参数:
            contour: 输入轮廓
            
        返回:
            tuple: (approx, area) 或 None
        """
        # 第一级：面积过滤
        area = cv2.contourArea(contour)
        if not (self.config.MIN_CONTOUR_AREA < area < self.config.MAX_CONTOUR_AREA):
            return None
        
        # 第二级：多边形逼近与边数过滤
        epsilon = 0.03 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) != self.config.TARGET_SIDES:
            return None
        
        # 第三级：宽高比过滤
        x, y, w, h = cv2.boundingRect(approx)
        if h <= 0:
            return None
        aspect_ratio = w / h
        if not (self.config.MIN_ASPECT_RATIO <= aspect_ratio <= self.config.MAX_ASPECT_RATIO):
            return None
        
        # 第四级：规则性校验（凸性、角度、对边比例）
        if not self._is_regular_rectangle(approx):
            return None
        
        return (approx, area)
    
    def _is_regular_rectangle(self, approx):
        """
        判断四边形是否为规则矩形
        
        参数:
            approx: 四边形顶点逼近
            
        返回:
            bool: True 表示规则矩形
        """
        # 1. 凸性检查
        if not cv2.isContourConvex(approx):
            return False
        
        # 2. 提取四个顶点
        pts = approx.reshape(4, 2).astype(np.float32)
        
        # 3. 校验对边长度
        edge_lengths = [
            GeometryUtils.calculate_edge_length(pts[i], pts[(i+1)%4]) 
            for i in range(4)
        ]
        top, right, bottom, left = edge_lengths
        
        if not (self.config.MIN_OPPOSITE_RATIO <= top/bottom <= self.config.MAX_OPPOSITE_RATIO and 
                self.config.MIN_OPPOSITE_RATIO <= left/right <= self.config.MAX_OPPOSITE_RATIO):
            return False
        
        # 4. 校验四个角的角度
        for i in range(4):
            angle = GeometryUtils.calculate_angle(pts[i], pts[(i+1)%4], pts[(i+2)%4])
            if not (self.config.MIN_ANGLE <= angle <= self.config.MAX_ANGLE):
                return False
        
        return True


# ============================================================================
# 第四章：虚拟按键模块
# 说明：实现触摸屏交互界面
# ============================================================================

class VirtualButtons:
    """虚拟按键类 - 实现触摸屏交互界面"""
    
    def __init__(self, config=None):
        """
        初始化虚拟按键布局
        
        参数:
            config: 配置参数类实例，None 则使用默认配置
        """
        self.config = config if config else DetectionConfig()
        
        # 根据屏幕尺寸动态计算绝对坐标
        self.buttons = self.config.calculate_absolute_buttons(
            self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT
        )
        
        # 根据屏幕尺寸动态计算触摸区域
        self.touch_areas = self.config.calculate_absolute_touch_areas(
            self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT
        )
        
        self.last_touch_time = 0
        self.touch_debounce = self.config.TOUCH_DEBOUNCE
    
    def check_touch(self, touch_x, touch_y):
        """
        检测触摸点是否命中按键
        
        参数:
            touch_x, touch_y (int): 触摸坐标
            
        返回:
            str: 命中按键的 action，未命中返回 None
        """
        current_time = time.time()
        
        # 防抖动检查
        if current_time - self.last_touch_time < self.touch_debounce:
            return None
        
        # 遍历触摸区域
        for i, touch_area in enumerate(self.touch_areas):
            area_x, area_y, area_w, area_h = touch_area
            if area_x <= touch_x <= area_x + area_w and area_y <= touch_y <= area_y + area_h:
                self.last_touch_time = current_time
                return self.buttons[i][5]
        
        return None
    
    def draw_buttons(self, img, current_mode, threshold):
        """
        在图像上绘制虚拟按键界面
        
        参数:
            img (np.array): 输入图像
            current_mode (str): 当前模式 ("center" 或 "circle")
            threshold (int): 当前阈值
        """
        for button in self.buttons:
            x, y, w, h, text, action = button
            
            # 根据状态设置颜色
            if (action == "center" and current_mode == "center") or \
               (action == "circle" and current_mode == "circle"):
                color = (0, 255, 255)  # 黄色：激活状态
                thickness = 3
            elif action in ["thresh_up", "thresh_down"]:
                color = (0, 255, 0)    # 绿色：调节按钮
                thickness = 2
            else:
                color = (255, 255, 255)  # 白色：普通状态
                thickness = 2
            
            # 绘制按键矩形框
            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
            
            # 绘制按键文本
            text_x = x + (w - len(text) * 4) // 2
            text_y = y + (h + 6) // 2
            cv2.putText(img, text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # 显示当前阈值
        cv2.putText(img, f"Thresh: {threshold}", (180, 170),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)


# ============================================================================
# 第五章：设备管理模块
# 说明：管理摄像头、显示屏、触摸屏等硬件设备
# ============================================================================

class DeviceManager:
    """设备管理类 - 管理所有硬件设备"""
    
    def __init__(self):
        """初始化设备管理器"""
        self.display = None
        self.camera = None
        self.touchscreen = None
        self.uart = None
    
    def init_display(self):
        """初始化显示屏"""
        self.display = display.Display()
        print("Display initialized")
    
    def init_camera(self, width=320, height=240):
        """
        初始化摄像头
        
        参数:
            width (int): 图像宽度
            height (int): 图像高度
        """
        self.camera = camera.Camera(width, height, image.Format.FMT_BGR888)
        print(f"Camera initialized ({width}x{height})")
    
    def init_touchscreen(self):
        """
        初始化触摸屏
        
        返回:
            touchscreen: 触摸屏对象，失败返回 None
        """
        try:
            self.touchscreen = touchscreen.TouchScreen()
            print("TouchScreen initialized successfully")
            return self.touchscreen
        except Exception as e:
            print(f"TouchScreen init failed: {e}")
            return None
    
    def init_uart(self, config=None):
        """
        初始化 UART 串口
        
        参数:
            config: 配置参数类实例，None 则使用默认配置
            
        返回:
            bool: 初始化是否成功
        """
        config = config if config else DetectionConfig()
        self.uart = SimpleUART()
        if self.uart.init(config.UART_DEVICE, config.UART_BAUDRATE, set_as_global=True):
            print("串口初始化成功")
            self.uart.set_frame(config.UART_FRAME_HEADER, config.UART_FRAME_TAIL, True)
            return True
        else:
            print("串口初始化失败")
            return False
    
    def capture_frame(self):
        """
        捕获一帧图像
        
        返回:
            np.array: BGR 格式图像，失败返回 None
        """
        if self.camera is None:
            return None
        
        img = self.camera.read()
        if img is None:
            return None
        
        return image.image2cv(img, ensure_bgr=False, copy=False)
    
    def show_frame(self, img):
        """
        显示图像到屏幕
        
        参数:
            img (np.array): 要显示的图像
        """
        if self.display is None:
            return
        
        img_show = image.cv2image(img, bgr=True, copy=False)
        self.display.show(img_show)
    
    def get_touch_data(self):
        """
        读取触摸屏数据
        
        返回:
            tuple: (x, y, pressed) 或 (None, None, None)
        """
        if self.touchscreen is None:
            return (None, None, None)
        
        try:
            if self.touchscreen.available():
                touch_data = self.touchscreen.read()
                if len(touch_data) >= 3:
                    return (touch_data[0], touch_data[1], touch_data[2])
        except Exception as e:
            print(f"Touch read error: {e}")
        
        return (None, None, None)


# ============================================================================
# 第六章：数据输出模块
# 说明：处理串口数据格式和输出
# ============================================================================

class DataOutput:
    """数据输出类 - 处理串口通信数据格式"""
    
    @staticmethod
    def send_center_point(point):
        """
        发送中心点坐标
        
        参数:
            point (tuple): 中心点坐标 (x, y)
        """
        if point:
            cx, cy = point
            micu_printf(f"red:({cx},{cy})")
        else:
            micu_printf("red:(0,0)")
    
    @staticmethod
    def send_circle_points(points):
        """
        发送圆形轨迹点
        
        参数:
            points (list): 圆形轨迹点列表
        """
        if points:
            circle_data = f"C,{len(points)}"
            for (x, y) in points:
                circle_data += f",{x},{y}"
            micu_printf(circle_data)
        else:
            micu_printf("C,0")


# ============================================================================
# 第七章：主程序
# 说明：系统主循环，协调各模块工作
# ============================================================================

class MainApplication:
    """主应用类 - 协调所有模块"""
    
    def __init__(self):
        """初始化应用"""
        self.config = DetectionConfig()
        self.devices = DeviceManager()
        self.detector = RectangleDetector(self.config)
        self.buttons = VirtualButtons(self.config)
        self.data_output = DataOutput()
        
        self.current_mode = "center"
        self.last_touch_pos = (0, 0)
        self.binary_threshold = self.config.BINARY_THRESHOLD
        
        self.fps = 0
        self.last_time = 0
        self.frame_count = 0
        
        # 预分配输出图像缓冲区，避免每次循环都创建新对象
        self.output_buffer = None
        
        # 透视变换矩阵缓存（用于性能优化）
        self.perspective_cache = {
            'last_pts_hash': None,
            'cached_M': None,
            'cached_M_inv': None,
            'cached_src_pts': None
        }
    
    def _hash_pts(self, pts):
        """
        计算顶点的哈希值，用于缓存比较
        
        参数:
            pts (np.array): 四边形顶点 (4,2)
            
        返回:
            int: 哈希值
        """
        return hash(tuple(pts.flatten().astype(int)))
    
    def init(self):
        """初始化所有设备"""
        self.devices.init_display()
        self.devices.init_camera(320, 240)
        self.devices.init_touchscreen()
        
        # 验证并清理串口设备路径
        is_valid, cleaned_path = self.config.validate_uart_device_path(self.config.UART_DEVICE)
        if not is_valid:
            print(f"警告：串口设备路径 '{self.config.UART_DEVICE}' 不合法，使用默认值 '{cleaned_path}'")
            self.config.UART_DEVICE = cleaned_path
        
        if not self.devices.init_uart(self.config):
            print("UART 初始化失败，退出程序")
            return False
        
        return True
    
    def process_touch(self):
        """处理触摸屏输入"""
        current_time = time.time()
        
        if (current_time - self.buttons.last_touch_time) > self.buttons.touch_debounce:
            touch_x, touch_y, pressed = self.devices.get_touch_data()
            
            if touch_x is not None:
                self.last_touch_pos = (touch_x, touch_y)
                
                if pressed:
                    action = self.buttons.check_touch(touch_x, touch_y)
                    if action:
                        self.buttons.last_touch_time = current_time
                        self._handle_button_action(action)
    
    def _handle_button_action(self, action):
        """
        处理按键动作
        
        参数:
            action (str): 按键动作 ID
        """
        if action == "center":
            self.current_mode = "center"
            print("切换到中心点模式")
        elif action == "circle":
            self.current_mode = "circle"
            print("切换到圆形模式")
        elif action == "thresh_up":
            self.binary_threshold = min(255, self.binary_threshold + 3)
            print(f"阈值增加到：{self.binary_threshold}")
        elif action == "thresh_down":
            self.binary_threshold = max(1, self.binary_threshold - 3)
            print(f"阈值减少到：{self.binary_threshold}")
    
    def calculate_fps(self):
        """计算并更新 FPS"""
        self.frame_count += 1
        current_time_ms = time.ticks_ms()
        
        if current_time_ms - self.last_time > 0:
            self.fps = 1000.0 / (current_time_ms - self.last_time)
        
        self.last_time = current_time_ms
    
    def process_frame(self, img):
        """
        处理单帧图像
        
        参数:
            img (np.array): 输入图像
            
        返回:
            np.array: 处理后的输出图像
        """
        # 复用或重新分配输出图像缓冲区
        if self.output_buffer is None or self.output_buffer.shape != img.shape:
            self.output_buffer = img.copy()
        else:
            np.copyto(self.output_buffer, img)
        
        output = self.output_buffer
        
        # 1. 矩形检测
        quads = self.detector.detect(img, self.binary_threshold)
        
        # 2. 处理检测到的矩形
        center_points = []
        all_circle_points = []
        
        for approx, area in quads:
            pts = approx.reshape(4, 2).astype(np.float32)
            cv2.drawContours(output, [approx], -1, (0, 255, 0), 2)
            
            # 检查缓存：如果顶点变化不大，使用缓存的透视变换矩阵
            current_hash = self._hash_pts(pts)
            use_cache = False
            
            if self.perspective_cache['last_pts_hash'] == current_hash:
                M = self.perspective_cache['cached_M']
                M_inv = self.perspective_cache['cached_M_inv']
                src_pts = self.perspective_cache['cached_src_pts']
                use_cache = True
            
            if not use_cache:
                # 计算新的透视变换矩阵
                M, M_inv, src_pts = PerspectiveTransform.transform(
                    pts, DetectionConfig.CORRECTED_WIDTH, DetectionConfig.CORRECTED_HEIGHT
                )
                # 更新缓存
                self.perspective_cache['last_pts_hash'] = current_hash
                self.perspective_cache['cached_M'] = M
                self.perspective_cache['cached_M_inv'] = M_inv
                self.perspective_cache['cached_src_pts'] = src_pts
            
            if M_inv is not None:
                # 使用预定义的校正中心常量
                center_np = np.array([[DetectionConfig.CORRECTED_CENTER]], dtype=np.float32)
                original_center = cv2.perspectiveTransform(center_np, M_inv)[0][0]
                cx, cy = int(original_center[0]), int(original_center[1])
            else:
                cx = int(np.mean(pts[:, 0]))
                cy = int(np.mean(pts[:, 1]))
            
            # 绘制中心点
            cv2.circle(output, (cx, cy), 5, (255, 0, 0), -1)
            center_points.append((cx, cy))
            
            # 圆形模式处理
            if self.current_mode == "circle":
                circle_pts = self._generate_circle_points(pts, M_inv, (cx, cy))
                all_circle_points.extend(circle_pts)
                for (x, y) in circle_pts:
                    cv2.circle(output, (x, y), 2, (0, 0, 255), -1)
        
        # 3. 串口发送数据
        if self.current_mode == "center":
            self.data_output.send_center_point(center_points[0] if center_points else None)
        elif self.current_mode == "circle":
            self.data_output.send_circle_points(all_circle_points)
        
        # 4. 绘制 UI 元素
        self._draw_ui(output)
        
        return output
    
    def _generate_circle_points(self, pts, M_inv, center):
        """
        生成圆形轨迹点
        
        参数:
            pts: 矩形顶点
            M_inv: 逆透视变换矩阵
            center: 中心点坐标
            
        返回:
            list: 原始坐标系下的圆形轨迹点
        """
        if M_inv is not None:
            corrected_circle = GeometryUtils.generate_circle_points(
                DetectionConfig.CORRECTED_CENTER, DetectionConfig.CIRCLE_RADIUS, 
                DetectionConfig.CIRCLE_NUM_POINTS
            )
            corrected_points_np = np.array([corrected_circle], dtype=np.float32)
            original_points = cv2.perspectiveTransform(corrected_points_np, M_inv)[0]
            return [(int(x), int(y)) for x, y in original_points]
        else:
            return GeometryUtils.generate_circle_points(
                center, 
                DetectionConfig.FALLBACK_CIRCLE_RADIUS, 
                DetectionConfig.CIRCLE_NUM_POINTS
            )
    
    def _draw_ui(self, img):
        """
        绘制用户界面元素
        
        参数:
            img (np.array): 输出图像
        """
        # 绘制目标点标记
        target_x, target_y = self.config.TARGET_POINT_X, self.config.TARGET_POINT_Y
        cross_size = 5
        cv2.line(img, (target_x - cross_size, target_y), 
                (target_x + cross_size, target_y), (255, 0, 255), 2)
        cv2.line(img, (target_x, target_y - cross_size), 
                (target_x, target_y + cross_size), (255, 0, 255), 2)
        cv2.putText(img, f"({target_x},{target_y})", (target_x + 8, target_y - 8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 255), 1)
        
        # 绘制虚拟按键
        self.buttons.draw_buttons(img, self.current_mode, self.binary_threshold)
        
        # 显示统计信息
        cv2.putText(img, f"FPS: {self.fps:.1f}", (10, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        mode_text = f"Mode: {self.current_mode.upper()}"
        cv2.putText(img, mode_text, (10, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        cv2.putText(img, f"Touch: {self.last_touch_pos}", (10, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 0), 1)
    
    def run(self):
        """运行主循环"""
        print("=" * 80)
        print("融合版 jiguangcar 程序启动...")
        print("配置参数加载完成，可在代码开头调整过滤条件")
        print("=" * 80)
        
        if not self.init():
            return
        
        while not app.need_exit():
            # 每隔一段时间手动触发垃圾回收（避免完全禁用导致内存问题）
            if self.frame_count % 300 == 0:
                gc.collect()
            
            # 计算 FPS
            self.calculate_fps()
            
            # 处理触摸输入
            self.process_touch()
            
            # 捕获并处理图像
            img = self.devices.capture_frame()
            if img is None:
                continue
            
            # 处理帧
            output = self.process_frame(img)
            
            # 显示
            self.devices.show_frame(output)


# ============================================================================
# 程序入口
# ============================================================================

if __name__ == "__main__":
    app_instance = MainApplication()
    app_instance.run()
