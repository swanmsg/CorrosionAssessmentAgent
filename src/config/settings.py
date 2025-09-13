"""
配置管理模块
处理环境变量和应用配置
"""

import os
from typing import Optional
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class CorrosionAgentConfig(BaseSettings):
    """腐蚀检测Agent配置类"""
    
    # 阿里百炼API配置
    dashscope_api_key: str = Field(..., env="DASHSCOPE_API_KEY")
    qwen_model: str = Field("qwen-plus", env="QWEN_MODEL")
    
    # 可选的OpenAI配置（向后兼容）
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4", env="OPENAI_MODEL")
    
    # 模型路径配置
    corrosion_model_path: str = Field("data/models/corrosion_detector.pth", env="CORROSION_MODEL_PATH")
    image_model_path: str = Field("data/models/image_classifier.pth", env="IMAGE_MODEL_PATH")
    
    # 数据路径配置
    data_root_path: str = Field("data/", env="DATA_ROOT_PATH")
    sample_data_path: str = Field("data/sample/", env="SAMPLE_DATA_PATH")
    output_path: str = Field("outputs/", env="OUTPUT_PATH")
    
    # 日志配置
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/corrosion_agent.log", env="LOG_FILE")
    
    # Agent配置
    max_iterations: int = Field(10, env="MAX_ITERATIONS")
    timeout_seconds: int = Field(300, env="TIMEOUT_SECONDS")
    
    # 传感器配置
    sensor_polling_interval: int = Field(60, env="SENSOR_POLLING_INTERVAL")
    image_capture_interval: int = Field(300, env="IMAGE_CAPTURE_INTERVAL")
    
    # 风险阈值配置
    low_risk_threshold: float = Field(0.3, env="LOW_RISK_THRESHOLD")
    medium_risk_threshold: float = Field(0.6, env="MEDIUM_RISK_THRESHOLD")
    high_risk_threshold: float = Field(0.8, env="HIGH_RISK_THRESHOLD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.data_root_path,
            self.sample_data_path,
            self.output_path,
            os.path.dirname(self.log_file)
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_model_path(self, model_type: str) -> str:
        """获取模型文件路径"""
        if model_type == "corrosion":
            return self.corrosion_model_path
        elif model_type == "image":
            return self.image_model_path
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def get_risk_level(self, score: float) -> str:
        """根据分数确定风险等级"""
        if score < self.low_risk_threshold:
            return "LOW"
        elif score < self.medium_risk_threshold:
            return "MEDIUM"
        elif score < self.high_risk_threshold:
            return "HIGH"
        else:
            return "CRITICAL"

# 全局配置实例
config = CorrosionAgentConfig()

# 确保目录存在
config.ensure_directories()