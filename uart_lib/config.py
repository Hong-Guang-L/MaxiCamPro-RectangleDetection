# config.py - 配置管理模块

"""
================================================================================
配置管理模块
功能：集中管理系统所有配置参数

设计原则:
    1. 单一职责：只负责配置管理
    2. 全局唯一：使用单例模式
    3. 易于扩展：支持动态添加配置项
================================================================================
"""


class Config:
    """
    系统配置管理类
    
    职责:
        - 管理 UART 设备配置
        - 管理缓冲区配置
        - 管理刷新模式配置
        - 管理数据帧格式配置
    
    使用示例:
        config = Config()
        config.set_frame_format("$$", "##", True)
        print(config.get_frame_config())
    """
    
    def __init__(self):
        """初始化配置参数"""
        
        # --------------------------- UART 设备配置 ---------------------------
        self.uart_device = "/dev/ttyS0"      # 默认 UART 设备路径
        self.uart_baudrate = 115200          # 默认波特率
        
        # --------------------------- 缓冲区配置 ---------------------------
        self.max_buffer_size = 1024          # 最大缓冲区大小（字节）
        
        # --------------------------- 刷新模式配置 ---------------------------
        self.refresh_interval = 500          # 定时器刷新间隔（毫秒）
        
        # --------------------------- 数据帧格式配置 ---------------------------
        # 帧格式用于标识完整数据包的边界
        # 例如："$$data##" 表示一个完整数据帧
        self.frame_config = {
            "header": "$$",      # 默认帧头标识
            "tail": "##",        # 默认帧尾标识
            "enabled": True      # 是否启用帧检测
        }
    
    def set_frame_format(self, header="$$", tail="##", enabled=True):
        """
        设置数据帧格式
        
        参数:
            header (str): 帧头标识字符串
            tail (str): 帧尾标识字符串
            enabled (bool): 是否启用帧检测
        
        使用示例:
            # 设置帧格式为 $$...##
            config.set_frame_format("$$", "##", True)
            
            # 禁用帧格式（按行处理）
            config.set_frame_format(enabled=False)
        """
        self.frame_config["header"] = header
        self.frame_config["tail"] = tail
        self.frame_config["enabled"] = enabled
    
    def get_frame_config(self):
        """
        获取帧格式配置
        
        返回:
            dict: 帧格式配置字典的副本
                  {"header": str, "tail": str, "enabled": bool}
        """
        return self.frame_config.copy()
    
    def update_config(self, **kwargs):
        """
        批量更新配置参数
        
        参数:
            **kwargs: 任意配置参数键值对
        
        使用示例:
            config.update_config(
                uart_baudrate=9600,
                max_buffer_size=2048
            )
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


# ============================================================================
# 全局配置实例
# 说明：使用单例模式，整个系统共享同一个配置对象
# ============================================================================
config = Config()
