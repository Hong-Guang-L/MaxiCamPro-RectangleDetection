# __init__.py - MICU UART 通信库模块初始化文件

"""
================================================================================
MICU UART 通信库 - 直接缓冲区刷新模式
版本：v2.4.0
作者：MICU 团队

模块功能概述:
    本模块提供简单高效的 UART 串口通信功能，专为 MaxiCamPro 平台设计。
    
主要特性:
    1. 直接缓冲区刷新机制，避免数据累积
    2. 支持全局帧头帧尾设置，便于数据解析
    3. 提供 micu_printf 函数用于 UART 调试输出
    4. 数据提取与变量绑定系统
    5. 键值对 (key=value) 解析功能
    6. 简化的配置管理
    7. 纯 ASCII/英文支持
    8. 线程安全设计

使用示例:
    # 初始化串口
    uart = SimpleUART()
    uart.init("/dev/ttyS0", 115200, set_as_global=True)
    
    # 设置帧格式
    uart.set_frame("$$", "##", True)
    
    # 发送数据
    uart.send("Hello World")
    
    # 使用 micu_printf 输出
    micu_printf("坐标：(%d, %d)", 100, 200)
    
    # 绑定变量自动解析
    bind_variable('x', variable_container, 'int')
================================================================================
"""

from .simple_uart import SimpleUART
from .utils import (
    # UART 工具函数
    micu_printf, 
    set_global_uart, 
    get_global_uart, 
    Timer, 
    get_timestamp,
    
    # 变量绑定与数据解析
    bind_variable, 
    get_variable_bindings, 
    clear_variable_bindings,
    parse_key_value_pairs, 
    apply_parsed_data, 
    extract_and_apply_data,
    VariableContainer, 
    safe_decode
)
from .config import config

# 版本信息
__version__ = "2.4.0"
__author__ = "MICU Team"

# 公共接口导出列表
# 使用 __all__ 明确指定模块的公共 API
__all__ = [
    # 核心类
    'SimpleUART',
    
    # 工具函数 - UART 通信
    'micu_printf',
    'set_global_uart', 
    'get_global_uart',
    'Timer',
    'get_timestamp',
    'safe_decode',
    
    # 数据提取与变量绑定
    'bind_variable',
    'get_variable_bindings',
    'clear_variable_bindings',
    'parse_key_value_pairs',
    'apply_parsed_data',
    'extract_and_apply_data',
    'VariableContainer',
    
    # 配置管理
    'config',
] 
