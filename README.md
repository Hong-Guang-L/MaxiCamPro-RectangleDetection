# 基于 MaxiCamPro 的矩形识别系统

<div align="center">

![MaxiCamPro](https://img.shields.io/badge/Platform-MaxiCamPro-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

**2025 年全国大学生电子设计竞赛 E 题 满分解决方案**

[项目演示](#演示效果) | [快速开始](#快速开始) | [技术文档](#技术文档) | [API 文档](#api-文档)

</div>

---

## 📋 目录

- [项目简介](#-项目简介)
- [核心特性](#-核心特性)
- [系统架构](#-系统架构)
- [演示效果](#-演示效果)
- [快速开始](#-快速开始)
- [技术文档](#-技术文档)
- [API 文档](#-api-文档)
- [性能测试](#-性能测试)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)
- [致谢](#-致谢)
- [许可证](#-许可证)

---

## 🎯 项目简介

本项目是一个基于 **MaxiCamPro 智能摄像头平台**的实时矩形识别与定位系统，在 2025 年全国大学生电子设计竞赛 E 题中取得优异成绩。

### 核心功能

✅ **实时矩形检测** - 30+ FPS 高速处理  
✅ **精确中心点定位** - 透视变换消除畸变  
✅ **触摸屏交互** - 实时调节参数  
✅ **串口通信** - 发送坐标数据至下位机  
✅ **双模式输出** - 中心点/圆形轨迹可选  

### 应用场景

- 🤖 机器人视觉引导
- 🎯 目标定位与跟踪
- 🏭 工业零件检测
- 📦 包裹分拣系统
- 🚗 自动驾驶辅助

---

## ✨ 核心特性

### 1. 多层级过滤算法

通过**四级过滤机制**确保检测准确性：

```
面积过滤 → 边数过滤 → 宽高比过滤 → 规则性验证
```

每级过滤都剔除不符合条件的轮廓，最终保留最可靠的矩形目标。

### 2. 透视变换校正

针对摄像头斜拍产生的透视畸变，使用**透视变换矩阵**将倾斜矩形校正为正视图，精确计算几何中心。

### 3. 实时参数调节

提供触摸屏虚拟按键，可实时调节：
- 二值化阈值（1-255）
- 输出模式（中心点/圆形）

### 4. 模块化设计

采用**面向对象**的模块化架构，代码清晰、易于维护和扩展：

```
MainApplication (主应用)
├── DeviceManager (设备管理)
├── RectangleDetector (矩形检测器)
├── VirtualButtons (虚拟按键)
├── GeometryUtils (几何工具)
└── DataOutput (数据输出)
```

---

## 🏗️ 系统架构

### 硬件平台

| 组件 | 规格 |
|------|------|
| 主控制器 | MaxiCamPro |
| 摄像头 | 320x240 BGR888 |
| 显示屏 | LCD 触摸屏 |
| 通信接口 | UART (115200) |

### 软件架构图

```
┌─────────────────────────────────────────┐
│         主应用层 MainApplication        │
│  - 主循环控制                            │
│  - 任务协调                              │
├─────────────────────────────────────────┤
│         功能层 Functional Layer          │
│  ┌──────────┬──────────┬──────────┐    │
│  │ 设备管理 │ 矩形检测 │ 虚拟按键 │    │
│  │  Device  │ Detector │ Buttons  │    │
│  └──────────┴──────────┴──────────┘    │
├─────────────────────────────────────────┤
│         工具层 Utility Layer             │
│  ┌──────────┬──────────┬──────────┐    │
│  │ 几何计算 │ 透视变换 │ 数据输出 │    │
│  │ Geometry │Transform │  Output  │    │
│  └──────────┴──────────┴──────────┘    │
└─────────────────────────────────────────┘
```

### 数据流

```
摄像头采集 (320x240)
    ↓
图像预处理 (灰度化 → 二值化 → 形态学)
    ↓
轮廓提取 (findContours)
    ↓
多级过滤 (面积 → 边数 → 宽高比 → 规则性)
    ↓
透视变换 (计算校正矩阵)
    ↓
坐标映射 (中心点/圆形轨迹)
    ↓
串口发送 ($$red:(x,y)##)
```

---

## 🎬 演示效果

### 场景 1：正面识别

```
距离：50cm
角度：0°（正面）
识别结果：✅ 成功
中心点：(166, 110)
FPS: 42
```

### 场景 2：倾斜识别

```
距离：60cm
角度：45°
识别结果：✅ 成功
中心点：(158, 115)
透视变换：已启用
FPS: 38
```

### 触摸屏界面

```
┌──────────────────────────────────────┐
│  [Center]  [Circle]  [T-]  [T+]     │
│    中心点    圆形     阈值减  阈值加  │
└──────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- MaxiCamPro 固件版本：v1.0.0+
- Python 3.7+
- OpenCV 4.x
- NumPy

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/Hong-Guang-L/MaxiCamPro-RectangleDetection.git
cd MaxiCamPro-RectangleDetection
```

#### 2. 导入到 MaxiCamPro IDE

- 打开 MaxiCamPro IDE
- 选择 `File` → `Open Folder`
- 选择项目目录

#### 3. 配置参数（可选）

编辑 `main.py` 文件开头的配置参数：

```python
class DetectionConfig:
    MIN_CONTOUR_AREA = 500       # 最小轮廓面积
    MAX_CONTOUR_AREA = 55000     # 最大轮廓面积
    BINARY_THRESHOLD = 66        # 二值化阈值
    MIN_ASPECT_RATIO = 0.6       # 最小宽高比
    MAX_ASPECT_RATIO = 1.7       # 最大宽高比
```

#### 4. 运行程序

- 连接 MaxiCamPro 设备
- 点击 `Run` 或按下 `F5`
- 观察屏幕输出

### 使用说明

#### 触摸操作

| 按键 | 功能 | 说明 |
|------|------|------|
| **Center** | 中心点模式 | 发送矩形中心坐标 |
| **Circle** | 圆形模式 | 发送圆形轨迹点 |
| **T-** | 降低阈值 | 减少二值化阈值 |
| **T+** | 提高阈值 | 增加二值化阈值 |

#### 串口数据格式

**中心点模式**：
```
$$red:(166,110)##
```

**圆形模式**：
```
$$C,12,x1,y1,x2,y2,...,x12,y12##
```

---

## 📚 技术文档

### 核心算法

#### 1. 图像预处理

```python
# 灰度化
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 二值化
_, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

# 形态学优化
processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel, iterations=1)
```

#### 2. 四级过滤

```python
# 第一级：面积过滤
if not (MIN_CONTOUR_AREA < area < MAX_CONTOUR_AREA):
    continue

# 第二级：边数过滤
epsilon = 0.03 * cv2.arcLength(cnt, True)
approx = cv2.approxPolyDP(cnt, epsilon, True)
if len(approx) != 4:
    continue

# 第三级：宽高比过滤
aspect_ratio = w / h
if not (MIN_ASPECT_RATIO <= aspect_ratio <= MAX_ASPECT_RATIO):
    continue

# 第四级：规则性验证
if not is_regular_rectangle(approx):
    continue
```

#### 3. 透视变换

```python
# 计算变换矩阵
M, M_inv, src_pts = perspective_transform(pts, 200, 150)

# 映射中心点回原图
corrected_center = (100, 75)
original_center = cv2.perspectiveTransform(
    np.array([[corrected_center]], dtype=np.float32), 
    M_inv
)[0][0]
```

### 参数调优指南

| 问题 | 解决方案 |
|------|---------|
| 检测不稳定 | 提高 `BINARY_THRESHOLD` |
| 误检小目标 | 增大 `MIN_CONTOUR_AREA` |
| 漏检小矩形 | 减小 `MIN_CONTOUR_AREA` |
| 倾斜识别差 | 放宽 `MIN_ANGLE` 和 `MAX_ANGLE` |
| 噪声干扰 | 增加形态学迭代次数 |

---

## 📖 API 文档

### RectangleDetector

矩形检测器类

#### 方法

##### `__init__(config=None)`

初始化检测器

**参数**：
- `config`: 配置参数类实例，None 则使用默认配置

##### `detect(img, threshold)`

执行矩形检测

**参数**：
- `img`: 输入图像（BGR 格式）
- `threshold`: 二值化阈值

**返回**：
- `list`: 检测到的矩形列表 `[(approx, area), ...]`

##### `_validate_contour(contour)`

验证轮廓是否为有效矩形

**参数**：
- `contour`: 输入轮廓

**返回**：
- `tuple`: `(approx, area)` 或 `None`

### DeviceManager

设备管理类

#### 方法

##### `init_camera(width=320, height=240)`

初始化摄像头

**参数**：
- `width`: 图像宽度
- `height`: 图像高度

##### `capture_frame()`

捕获一帧图像

**返回**：
- `np.array`: BGR 格式图像，失败返回 `None`

##### `show_frame(img)`

显示图像到屏幕

**参数**：
- `img`: 要显示的图像

### VirtualButtons

虚拟按键类

#### 方法

##### `check_touch(touch_x, touch_y)`

检测触摸点是否命中按键

**参数**：
- `touch_x`: 触摸 X 坐标
- `touch_y`: 触摸 Y 坐标

**返回**：
- `str`: 命中按键的 action，未命中返回 `None`

##### `draw_buttons(img, current_mode, threshold)`

在图像上绘制虚拟按键界面

**参数**：
- `img`: 输入图像
- `current_mode`: 当前模式 ("center" 或 "circle")
- `threshold`: 当前阈值

---

## 📊 性能测试

### 测试环境

- **距离**：20cm - 100cm
- **角度**：0° - 60°
- **光照**：室内自然光、LED 补光
- **目标尺寸**：5cm×5cm 至 20cm×20cm

### 测试结果

| 指标 | 数值 |
|------|------|
| **识别准确率** | 正面 98.5% / 倾斜 30° 95.2% |
| **中心点精度** | 平均误差 < 3 像素 |
| **处理速度** | 35-45 FPS |
| **响应时间** | 触摸延迟 < 100ms |

### 不同距离推荐参数

| 距离 | 阈值 | 最小面积 | 最大面积 |
|------|------|---------|---------|
| 20-40cm | 60-70 | 300 | 30000 |
| 40-70cm | 65-75 | 500 | 55000 |
| 70-100cm | 70-80 | 800 | 80000 |

---

## ❓ 常见问题

### Q1: 矩形检测不稳定怎么办？

**A**: 按以下顺序调整参数：
1. 提高 `BINARY_THRESHOLD`（增强对比度）
2. 增大 `MIN_CONTOUR_AREA`（过滤小噪声）
3. 收紧角度限制（`MIN_ANGLE` 和 `MAX_ANGLE`）

### Q2: 倾斜角度大时识别率下降？

**A**: 这是正常现象，可以：
1. 调整摄像头角度（建议<45°）
2. 放宽角度限制（`MIN_ANGLE=60`, `MAX_ANGLE=120`）
3. 增加补光灯减少阴影

### Q3: 串口通信失败？

**A**: 检查以下几点：
1. 确认串口设备路径（`/dev/ttyS0`）
2. 确认波特率一致（115200）
3. 检查帧格式（`$$` 和 `##`）

### Q4: 如何识别多个矩形？

**A**: 当前版本只保留面积最大的矩形。如需识别多个，修改 `detect` 方法：

```python
# 修改前：只保留最大的
return [max(quads, key=lambda x: x[1])]

# 修改后：返回所有检测到的
return quads
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 贡献步骤

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 编码规范
- 函数必须包含文档字符串
- 添加必要的单元测试

---

## 🙏 致谢

感谢以下组织和个人的支持：

- 2025 年全国大学生电子设计竞赛组委会
- 指导老师
- MaxiCamPro 开发团队
- 所有贡献者

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 📖 技术博客

详细的技术博客已发表至 CSDN：

**[基于 MaxiCamPro 的矩形识别系统实战详解](#)**

博客内容包括：
- 算法原理深度剖析
- 代码实现详解
- 性能优化技巧
- 实战经验分享

欢迎阅读、评论和收藏！

---

## 📬 联系方式

- **项目仓库**: https://github.com/Hong-Guang-L/MaxiCamPro-RectangleDetection
- **问题反馈**: https://github.com/Hong-Guang-L/MaxiCamPro-RectangleDetection/issues
- **作者主页**: https://github.com/Hong-Guang-L

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐Star 支持一下！**

Made with ❤️ by 电赛团队

</div>
