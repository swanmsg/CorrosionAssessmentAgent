"""
数据模型定义
定义腐蚀检测系统中使用的各种数据结构
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
import numpy as np

class CorrosionLevel(str, Enum):
    """腐蚀等级枚举"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SensorType(str, Enum):
    """传感器类型枚举"""
    THICKNESS = "thickness"
    CONDUCTIVITY = "conductivity"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PH = "ph"
    PRESSURE = "pressure"

class SensorData(BaseModel):
    """传感器数据模型"""
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime
    location: Dict[str, float] = Field(description="坐标位置 {x, y, z}")
    quality: float = Field(ge=0.0, le=1.0, description="数据质量评分")

class ImageData(BaseModel):
    """图像数据模型"""
    image_id: str
    file_path: str
    timestamp: datetime
    location: Dict[str, float]
    resolution: Dict[str, int] = Field(description="图像分辨率 {width, height}")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CorrosionDetection(BaseModel):
    """腐蚀检测结果模型"""
    detection_id: str
    image_id: Optional[str] = None
    corrosion_area: float = Field(description="腐蚀面积(平方毫米)")
    corrosion_depth: float = Field(description="腐蚀深度(毫米)")
    corrosion_type: str = Field(description="腐蚀类型")
    confidence: float = Field(ge=0.0, le=1.0, description="检测置信度")
    bounding_boxes: List[Dict[str, int]] = Field(default_factory=list)
    timestamp: datetime

class RiskAssessment(BaseModel):
    """风险评估结果模型"""
    assessment_id: str
    corrosion_level: CorrosionLevel
    risk_score: float = Field(ge=0.0, le=1.0, description="风险评分")
    factors: Dict[str, float] = Field(description="影响因素权重")
    recommendations: List[str] = Field(default_factory=list)
    urgency: str = Field(description="紧急程度")
    timestamp: datetime

class MaintenanceRecommendation(BaseModel):
    """维护建议模型"""
    recommendation_id: str
    priority: int = Field(ge=1, le=5, description="优先级(1-5)")
    action_type: str = Field(description="维护动作类型")
    description: str
    estimated_cost: Optional[float] = None
    estimated_duration: Optional[int] = None  # 小时
    required_resources: List[str] = Field(default_factory=list)

class InspectionReport(BaseModel):
    """检测报告模型"""
    report_id: str
    timestamp: datetime
    inspector: str
    platform_id: str
    area_inspected: str
    
    # 检测数据
    sensor_data: List[SensorData] = Field(default_factory=list)
    image_data: List[ImageData] = Field(default_factory=list)
    
    # 分析结果
    corrosion_detections: List[CorrosionDetection] = Field(default_factory=list)
    risk_assessment: Optional[RiskAssessment] = None
    
    # 建议和总结
    maintenance_recommendations: List[MaintenanceRecommendation] = Field(default_factory=list)
    summary: str = ""
    next_inspection_date: Optional[datetime] = None

class AgentState(BaseModel):
    """Agent状态模型"""
    session_id: str
    current_step: str
    platform_id: str
    inspection_area: str
    
    # 输入数据
    sensor_readings: List[SensorData] = Field(default_factory=list)
    image_files: List[str] = Field(default_factory=list)
    
    # 处理过程数据
    processed_images: List[ImageData] = Field(default_factory=list)
    corrosion_detections: List[CorrosionDetection] = Field(default_factory=list)
    risk_assessment: Optional[RiskAssessment] = None
    
    # 输出结果
    final_report: Optional[InspectionReport] = None
    
    # LLM增强分析结果
    llm_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # 元数据
    start_time: datetime
    last_update: datetime
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True

class AnalysisContext(BaseModel):
    """分析上下文模型"""
    environmental_conditions: Dict[str, float] = Field(default_factory=dict)
    material_properties: Dict[str, Any] = Field(default_factory=dict)
    historical_data: List[Dict[str, Any]] = Field(default_factory=list)
    maintenance_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True