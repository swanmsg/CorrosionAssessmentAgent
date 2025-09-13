"""
数据收集节点
处理传感器数据采集和图像数据预处理
"""

import os
import cv2
import numpy as np
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models import (
    AgentState, SensorData, ImageData, SensorType, CorrosionDetection,
    RiskAssessment, CorrosionLevel, MaintenanceRecommendation, InspectionReport
)
from ..config import config
from ..utils.image_processor import ImageProcessor
from ..utils.sensor_reader import SensorReader
from ..utils.llm_service import llm_service

class DataCollectionNode:
    """数据收集节点"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.sensor_reader = SensorReader()
    
    def execute(self, state: AgentState) -> AgentState:
        """执行数据收集"""
        print("开始数据收集...")
        
        # 收集传感器数据
        state = self._collect_sensor_data(state)
        
        # 处理图像数据
        state = self._process_image_data(state)
        
        print(f"数据收集完成: {len(state.sensor_readings)} 个传感器读数, {len(state.processed_images)} 张图像")
        
        return state
    
    def _collect_sensor_data(self, state: AgentState) -> AgentState:
        """收集传感器数据"""
        try:
            # 模拟从各种传感器收集数据
            # 在实际应用中，这里会连接到真实的传感器接口
            
            sensor_readings = []
            
            # 厚度传感器数据
            thickness_data = self._generate_thickness_readings(state.inspection_area)
            sensor_readings.extend(thickness_data)
            
            # 环境传感器数据
            environmental_data = self._generate_environmental_readings(state.inspection_area)
            sensor_readings.extend(environmental_data)
            
            # 电化学传感器数据
            electrochemical_data = self._generate_electrochemical_readings(state.inspection_area)
            sensor_readings.extend(electrochemical_data)
            
            state.sensor_readings = sensor_readings
            
        except Exception as e:
            state.errors.append(f"传感器数据收集失败: {str(e)}")
        
        return state
    
    def _process_image_data(self, state: AgentState) -> AgentState:
        """处理图像数据"""
        try:
            processed_images = []
            
            for image_file in state.image_files:
                if os.path.exists(image_file):
                    # 处理单张图像
                    image_data = self._process_single_image(image_file, state.inspection_area)
                    if image_data:
                        processed_images.append(image_data)
                else:
                    state.warnings.append(f"图像文件不存在: {image_file}")
            
            # 如果没有提供图像文件，生成一些示例图像数据
            if not processed_images:
                sample_images = self._generate_sample_images(state.inspection_area)
                processed_images.extend(sample_images)
            
            state.processed_images = processed_images
            
        except Exception as e:
            state.errors.append(f"图像数据处理失败: {str(e)}")
        
        return state
    
    def _generate_thickness_readings(self, area: str) -> List[SensorData]:
        """生成厚度传感器读数"""
        readings = []
        base_thickness = 12.0  # 基础厚度 mm
        
        # 在检测区域生成多个测量点
        for i in range(5):
            # 模拟不同程度的腐蚀
            thickness_loss = np.random.uniform(0, 3.0)  # 0-3mm的厚度损失
            current_thickness = base_thickness - thickness_loss
            
            reading = SensorData(
                sensor_id=f"thickness_{area}_{i+1}",
                sensor_type=SensorType.THICKNESS,
                value=current_thickness,
                unit="mm",
                timestamp=datetime.now(),
                location={"x": i * 10, "y": 0, "z": 0},
                quality=np.random.uniform(0.8, 1.0)
            )
            readings.append(reading)
        
        return readings
    
    def _generate_environmental_readings(self, area: str) -> List[SensorData]:
        """生成环境传感器读数"""
        readings = []
        
        # 温度传感器
        temp_reading = SensorData(
            sensor_id=f"temp_{area}",
            sensor_type=SensorType.TEMPERATURE,
            value=np.random.uniform(15, 35),  # 15-35°C
            unit="°C",
            timestamp=datetime.now(),
            location={"x": 0, "y": 0, "z": 0},
            quality=0.95
        )
        readings.append(temp_reading)
        
        # 湿度传感器
        humidity_reading = SensorData(
            sensor_id=f"humidity_{area}",
            sensor_type=SensorType.HUMIDITY,
            value=np.random.uniform(60, 90),  # 60-90%
            unit="%RH",
            timestamp=datetime.now(),
            location={"x": 0, "y": 0, "z": 0},
            quality=0.92
        )
        readings.append(humidity_reading)
        
        # pH传感器
        ph_reading = SensorData(
            sensor_id=f"ph_{area}",
            sensor_type=SensorType.PH,
            value=np.random.uniform(7.5, 8.5),  # 海水pH
            unit="pH",
            timestamp=datetime.now(),
            location={"x": 0, "y": 0, "z": 0},
            quality=0.88
        )
        readings.append(ph_reading)
        
        return readings
    
    def _generate_electrochemical_readings(self, area: str) -> List[SensorData]:
        """生成电化学传感器读数"""
        readings = []
        
        # 电导率传感器
        conductivity_reading = SensorData(
            sensor_id=f"conductivity_{area}",
            sensor_type=SensorType.CONDUCTIVITY,
            value=np.random.uniform(50000, 55000),  # 海水电导率 μS/cm
            unit="μS/cm",
            timestamp=datetime.now(),
            location={"x": 0, "y": 0, "z": 0},
            quality=0.90
        )
        readings.append(conductivity_reading)
        
        return readings
    
    def _process_single_image(self, image_path: str, area: str) -> Optional[ImageData]:
        """处理单张图像"""
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # 获取图像信息
            height, width = image.shape[:2]
            
            # 图像预处理
            processed_image = self.image_processor.preprocess(image)
            
            # 保存处理后的图像
            processed_path = self._save_processed_image(processed_image, image_path, area)
            
            image_data = ImageData(
                image_id=f"img_{area}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                file_path=processed_path,
                timestamp=datetime.now(),
                location={"x": 0, "y": 0, "z": 0},
                resolution={"width": width, "height": height},
                metadata={
                    "original_path": image_path,
                    "file_size": os.path.getsize(image_path),
                    "processed": True
                }
            )
            
            return image_data
            
        except Exception as e:
            print(f"图像处理失败 {image_path}: {e}")
            return None
    
    def _save_processed_image(self, image: np.ndarray, original_path: str, area: str) -> str:
        """保存处理后的图像"""
        # 创建输出目录
        output_dir = Path(config.output_path) / "processed_images"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成输出文件名
        original_name = Path(original_path).stem
        output_path = output_dir / f"{original_name}_{area}_processed.jpg"
        
        # 保存图像
        cv2.imwrite(str(output_path), image)
        
        return str(output_path)
    
    def _generate_sample_images(self, area: str) -> List[ImageData]:
        """生成示例图像数据（用于演示）"""
        sample_images = []
        
        # 创建一些模拟的图像数据
        for i in range(3):
            # 生成模拟图像
            image = self._create_sample_corrosion_image()
            
            # 保存图像
            output_dir = Path(config.output_path) / "sample_images" 
            output_dir.mkdir(parents=True, exist_ok=True)
            image_path = output_dir / f"sample_{area}_{i+1}.jpg"
            
            cv2.imwrite(str(image_path), image)
            
            image_data = ImageData(
                image_id=f"sample_{area}_{i+1}",
                file_path=str(image_path),
                timestamp=datetime.now(),
                location={"x": i * 50, "y": 0, "z": 0},
                resolution={"width": 640, "height": 480},
                metadata={
                    "type": "sample",
                    "generated": True
                }
            )
            sample_images.append(image_data)
        
        return sample_images
    
    def _create_sample_corrosion_image(self) -> np.ndarray:
        """创建示例腐蚀图像"""
        # 创建640x480的基础图像（钢铁表面）
        image = np.random.randint(80, 120, (480, 640, 3), dtype=np.uint8)
        
        # 添加一些腐蚀特征
        # 添加铁锈色斑点
        for _ in range(np.random.randint(3, 8)):
            center = (np.random.randint(50, 590), np.random.randint(50, 430))
            radius = np.random.randint(10, 30)
            color = (20, 50, 180)  # 橙红色（BGR格式）
            cv2.circle(image, center, radius, color, -1)
        
        # 添加一些表面纹理
        noise = np.random.randint(-20, 20, image.shape, dtype=np.int16)
        image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        return image


class CorrosionAnalysisNode:
    """腐蚀分析节点"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
    
    def execute(self, state: AgentState) -> AgentState:
        """执行腐蚀分析"""
        print("开始腐蚀分析...")
        
        detections = []
        
        # 分析每张图像
        for image_data in state.processed_images:
            detection = self._analyze_image(image_data, state.inspection_area)
            if detection:
                detections.append(detection)
        
        # 结合传感器数据进行分析
        enhanced_detections = self._enhance_with_sensor_data(detections, state.sensor_readings)
        
        # 使用LLM进行增强分析
        llm_analysis = self._perform_llm_analysis(enhanced_detections, state.sensor_readings)
        
        # 将LLM分析结果添加到状态中
        if not hasattr(state, 'llm_analysis'):
            state.llm_analysis = {}
        state.llm_analysis.update(llm_analysis)
        
        state.corrosion_detections = enhanced_detections
        
        print(f"腐蚀分析完成: 检测到 {len(detections)} 个腐蚀点")
        if llm_analysis.get('technical_insights'):
            print(f"🤖 LLM分析: {llm_analysis['technical_insights'][:100]}...")
        
        return state
    
    def _analyze_image(self, image_data: ImageData, area: str) -> Optional[CorrosionDetection]:
        """分析单张图像"""
        try:
            # 读取图像
            import cv2
            image = cv2.imread(image_data.file_path)
            if image is None:
                return None
            
            # 检测腐蚀特征
            bounding_boxes = self.image_processor.detect_corrosion_features(image)
            
            if not bounding_boxes:
                return None
            
            # 计算腐蚀面积和深度
            corrosion_area = self.image_processor.calculate_corrosion_area(image, bounding_boxes)
            corrosion_depth = self.image_processor.estimate_corrosion_depth(image, bounding_boxes)
            
            # 确定腐蚀类型
            corrosion_type = self._classify_corrosion_type(image, bounding_boxes)
            
            # 计算置信度
            confidence = self._calculate_confidence(bounding_boxes, corrosion_area)
            
            detection = CorrosionDetection(
                detection_id=f"detection_{image_data.image_id}",
                image_id=image_data.image_id,
                corrosion_area=corrosion_area,
                corrosion_depth=corrosion_depth,
                corrosion_type=corrosion_type,
                confidence=confidence,
                bounding_boxes=[{"x": x, "y": y, "w": w, "h": h} for x, y, w, h in bounding_boxes],
                timestamp=datetime.now()
            )
            
            return detection
            
        except Exception as e:
            print(f"图像分析失败 {image_data.file_path}: {e}")
            return None
    
    def _classify_corrosion_type(self, image: np.ndarray, bounding_boxes: List) -> str:
        """分类腐蚀类型"""
        # 简化的腐蚀类型分类
        if len(bounding_boxes) == 1:
            return "局部腐蚀"
        elif len(bounding_boxes) > 3:
            return "点蚀"
        else:
            return "均匀腐蚀"
    
    def _calculate_confidence(self, bounding_boxes: List, area: float) -> float:
        """计算检测置信度"""
        # 基于检测区域数量和面积的置信度计算
        base_confidence = 0.7
        
        # 检测到的区域越多，置信度稍微降低
        region_factor = max(0.1, 1.0 - len(bounding_boxes) * 0.05)
        
        # 面积因子
        area_factor = min(1.0, area / 1000.0)  # 归一化到1000平方毫米
        
        confidence = base_confidence * region_factor * (0.5 + 0.5 * area_factor)
        return min(0.95, max(0.3, confidence))
    
    def _enhance_with_sensor_data(self, detections: List[CorrosionDetection], 
                                sensor_readings: List[SensorData]) -> List[CorrosionDetection]:
        """使用传感器数据增强检测结果"""
        # 获取厚度传感器数据
        thickness_readings = [r for r in sensor_readings if r.sensor_type == SensorType.THICKNESS]
        
        if not thickness_readings:
            return detections
        
        # 使用厚度传感器数据增强检测结果
        enhanced_detections = []
        for detection in detections:
            # 计算平均厚度损失
            avg_thickness = np.mean([r.value for r in thickness_readings])
            base_thickness = 12.0  # 基本厚度 mm
            thickness_loss = base_thickness - avg_thickness
            
            # 调整腐蚀深度估计
            adjusted_depth = max(detection.corrosion_depth, thickness_loss * 0.8)
            
            # 创建增强的检测结果
            enhanced_detection = CorrosionDetection(
                detection_id=detection.detection_id,
                image_id=detection.image_id,
                corrosion_area=detection.corrosion_area,
                corrosion_depth=adjusted_depth,
                corrosion_type=detection.corrosion_type,
                confidence=min(0.95, detection.confidence + 0.05),  # 略微提高置信度
                bounding_boxes=detection.bounding_boxes,
                timestamp=detection.timestamp
            )
            enhanced_detections.append(enhanced_detection)
        
        return enhanced_detections
    
    def _perform_llm_analysis(self, detections: List[CorrosionDetection], 
                            sensor_readings: List[SensorData]) -> Dict[str, Any]:
        """使用LLM进行增强分析"""
        try:
            analysis_result = llm_service.analyze_corrosion_data(sensor_readings, detections)
            return analysis_result
        except Exception as e:
            print(f"⚠️ LLM分析失败: {e}")
            return {
                "severity_assessment": "基于传统方法的分析",
                "technical_insights": "使用传统图像处理和传感器数据分析"
            }


class RiskAssessmentNode:
    """风险评估节点"""
    
    def execute(self, state: AgentState) -> AgentState:
        """执行风险评估"""
        print("开始风险评估...")
        
        if not state.corrosion_detections:
            # 没有检测到腐蚀，风险较低
            risk_assessment = RiskAssessment(
                assessment_id=f"risk_{state.session_id}",
                corrosion_level=CorrosionLevel.LOW,
                risk_score=0.1,
                factors={"no_corrosion_detected": 1.0},
                recommendations=["继续定期监测", "保持当前维护计划"],
                urgency="低",
                timestamp=datetime.now()
            )
        else:
            risk_assessment = self._assess_risk(state.corrosion_detections, state.sensor_readings)
        
        state.risk_assessment = risk_assessment
        
        print(f"风险评估完成: 风险等级 {risk_assessment.corrosion_level.value}")
        
        return state
    
    def _assess_risk(self, detections: List[CorrosionDetection], 
                    sensor_readings: List[SensorData]) -> RiskAssessment:
        """评估腐蚀风险"""
        # 计算各种风险因子
        factors = {}
        
        # 腐蚀面积因子
        total_area = sum(d.corrosion_area for d in detections)
        area_factor = min(1.0, total_area / 5000.0)  # 归一化到5000平方毫米
        factors["corrosion_area"] = area_factor
        
        # 腐蚀深度因子
        max_depth = max(d.corrosion_depth for d in detections)
        depth_factor = min(1.0, max_depth / 3.0)  # 归一化到3毫米
        factors["corrosion_depth"] = depth_factor
        
        # 腐蚀数量因子
        count_factor = min(1.0, len(detections) / 10.0)  # 归一化到10个检测点
        factors["corrosion_count"] = count_factor
        
        # 环境因子
        env_factor = self._calculate_environmental_factor(sensor_readings)
        factors["environmental"] = env_factor
        
        # 计算综合风险评分
        risk_score = (
            area_factor * 0.3 +
            depth_factor * 0.4 +
            count_factor * 0.2 +
            env_factor * 0.1
        )
        
        # 确定风险等级
        corrosion_level = self._determine_risk_level(risk_score)
        
        # 生成建议
        recommendations = self._generate_recommendations(corrosion_level, factors)
        
        # 使用LLM增强建议
        enhanced_recommendations = self._enhance_recommendations_with_llm(corrosion_level, risk_score, recommendations)
        
        # 确定紧急程度
        urgency = self._determine_urgency(corrosion_level, max_depth)
        
        return RiskAssessment(
            assessment_id=f"risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            corrosion_level=corrosion_level,
            risk_score=risk_score,
            factors=factors,
            recommendations=enhanced_recommendations,
            urgency=urgency,
            timestamp=datetime.now()
        )
    
    def _calculate_environmental_factor(self, sensor_readings: List[SensorData]) -> float:
        """计算环境因子"""
        if not sensor_readings:
            return 0.5  # 默认中等环境风险
        
        env_score = 0.0
        
        # 温度因子
        temp_readings = [r for r in sensor_readings if r.sensor_type == SensorType.TEMPERATURE]
        if temp_readings:
            avg_temp = np.mean([r.value for r in temp_readings])
            temp_score = min(1.0, (avg_temp - 15) / 20.0)  # 15-35°C范围
            env_score += temp_score * 0.3
        
        # 湿度因子
        humidity_readings = [r for r in sensor_readings if r.sensor_type == SensorType.HUMIDITY]
        if humidity_readings:
            avg_humidity = np.mean([r.value for r in humidity_readings])
            humidity_score = min(1.0, (avg_humidity - 60) / 30.0)  # 60-90%范围
            env_score += humidity_score * 0.4
        
        # pH因子
        ph_readings = [r for r in sensor_readings if r.sensor_type == SensorType.PH]
        if ph_readings:
            avg_ph = np.mean([r.value for r in ph_readings])
            ph_score = abs(avg_ph - 8.0) / 2.0  # 偏离中性pH 8.0的程度
            env_score += min(1.0, ph_score) * 0.3
        
        return min(1.0, env_score)
    
    def _determine_risk_level(self, risk_score: float) -> CorrosionLevel:
        """确定风险等级"""
        if risk_score < config.low_risk_threshold:
            return CorrosionLevel.LOW
        elif risk_score < config.medium_risk_threshold:
            return CorrosionLevel.MEDIUM
        elif risk_score < config.high_risk_threshold:
            return CorrosionLevel.HIGH
        else:
            return CorrosionLevel.CRITICAL
    
    def _generate_recommendations(self, level: CorrosionLevel, factors: Dict[str, float]) -> List[str]:
        """生成维护建议"""
        recommendations = []
        
        if level == CorrosionLevel.LOW:
            recommendations.extend([
                "继续按现有计划进行定期检测",
                "保持良好的防腐涂层维护",
                "监控环境条件变化"
            ])
        elif level == CorrosionLevel.MEDIUM:
            recommendations.extend([
                "增加检测频率至每3个月一次",
                "对检测到的腐蚀区域进行局部处理",
                "检查并更新防腐措施",
                "评估环境控制系统"
            ])
        elif level == CorrosionLevel.HIGH:
            recommendations.extend([
                "立即对严重腐蚀区域进行维修",
                "每月进行详细检测",
                "更换或加强防腐涂层",
                "考虑增加阴极保护措施",
                "制定详细的维修计划"
            ])
        else:  # CRITICAL
            recommendations.extend([
                "紧急停止相关设备运行",
                "立即安排专业维修团队",
                "每周进行安全检测",
                "重新评估整体结构安全性",
                "考虑部分结构更换"
            ])
        
        return recommendations
    
    def _determine_urgency(self, level: CorrosionLevel, max_depth: float) -> str:
        """确定紧急程度"""
        if level == CorrosionLevel.CRITICAL or max_depth > 2.0:
            return "紧急"
        elif level == CorrosionLevel.HIGH or max_depth > 1.0:
            return "高"
        elif level == CorrosionLevel.MEDIUM:
            return "中等"
        else:
            return "低"
    
    def _enhance_recommendations_with_llm(self, level: CorrosionLevel, risk_score: float, 
                                         base_recommendations: List[str]) -> List[str]:
        """使用LLM增强维护建议"""
        try:
            # 创建临时风险评估对象用于LLM调用
            temp_assessment = RiskAssessment(
                assessment_id="temp",
                corrosion_level=level,
                risk_score=risk_score,
                factors={"estimated": risk_score},  # 添加必需的factors字段
                recommendations=base_recommendations,
                urgency="中等",
                timestamp=datetime.now()
            )
            
            enhanced_recommendations = llm_service.generate_maintenance_insights(temp_assessment)
            
            # 如果LLM生成了新建议，使用增强建议；否则使用基础建议
            if enhanced_recommendations and len(enhanced_recommendations) > 0:
                print(f"🤖 LLM增强维护建议: {len(enhanced_recommendations)}条")
                return enhanced_recommendations
            else:
                return base_recommendations
                
        except Exception as e:
            print(f"⚠️ LLM建议增强失败: {e}")
            return base_recommendations


class ReportGenerationNode:
    """报告生成节点"""
    
    def execute(self, state: AgentState) -> AgentState:
        """生成检测报告"""
        print("开始生成报告...")
        
        # 生成维护建议
        maintenance_recommendations = self._generate_maintenance_recommendations(state)
        
        # 生成摘要
        summary = self._generate_summary(state)
        
        # 使用LLM增强摘要
        enhanced_summary = self._generate_enhanced_summary(state, summary)
        
        # 确定下次检测时间
        next_inspection = self._calculate_next_inspection_date(state.risk_assessment)
        
        # 创建最终报告
        report = InspectionReport(
            report_id=f"report_{state.session_id}",
            timestamp=datetime.now(),
            inspector="Corrosion Detection Agent",
            platform_id=state.platform_id,
            area_inspected=state.inspection_area,
            sensor_data=state.sensor_readings,
            image_data=state.processed_images,
            corrosion_detections=state.corrosion_detections,
            risk_assessment=state.risk_assessment,
            maintenance_recommendations=maintenance_recommendations,
            summary=enhanced_summary,
            next_inspection_date=next_inspection
        )
        
        state.final_report = report
        
        # 保存报告到文件
        self._save_report(report)
        
        print(f"报告生成完成: {report.report_id}")
        
        return state
    
    def _generate_maintenance_recommendations(self, state: AgentState) -> List[MaintenanceRecommendation]:
        """生成维护建议"""
        recommendations = []
        
        if not state.risk_assessment:
            return recommendations
        
        level = state.risk_assessment.corrosion_level
        
        if level == CorrosionLevel.LOW:
            rec = MaintenanceRecommendation(
                recommendation_id="maint_001",
                priority=2,
                action_type="预防性维护",
                description="继续定期检测和防腐涂层维护",
                estimated_cost=5000.0,
                estimated_duration=8,
                required_resources=["检测设备", "防腐材料"]
            )
            recommendations.append(rec)
        
        elif level in [CorrosionLevel.MEDIUM, CorrosionLevel.HIGH]:
            rec1 = MaintenanceRecommendation(
                recommendation_id="maint_002",
                priority=3,
                action_type="修复性维护",
                description="对腐蚀区域进行局部修复和重新涂装",
                estimated_cost=15000.0,
                estimated_duration=24,
                required_resources=["维修工具", "防腐涂料", "专业人员"]
            )
            recommendations.append(rec1)
            
            if level == CorrosionLevel.HIGH:
                rec2 = MaintenanceRecommendation(
                    recommendation_id="maint_003",
                    priority=4,
                    action_type="结构加固",
                    description="对受损严重区域进行结构评估和加固",
                    estimated_cost=50000.0,
                    estimated_duration=72,
                    required_resources=["结构工程师", "加固材料", "专业设备"]
                )
                recommendations.append(rec2)
        
        elif level == CorrosionLevel.CRITICAL:
            rec = MaintenanceRecommendation(
                recommendation_id="maint_004",
                priority=5,
                action_type="紧急维修",
                description="立即停止设备运行，进行紧急维修或更换",
                estimated_cost=100000.0,
                estimated_duration=120,
                required_resources=["紧急维修团队", "替换部件", "重型设备"]
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_summary(self, state: AgentState) -> str:
        """生成检测摘要"""
        summary_parts = []
        
        summary_parts.append(f"检测区域: {state.inspection_area}")
        summary_parts.append(f"检测时间: {state.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 传感器数据摘要
        summary_parts.append(f"传感器数据: 收集了 {len(state.sensor_readings)} 个传感器读数")
        
        # 图像数据摘要
        summary_parts.append(f"图像数据: 处理了 {len(state.processed_images)} 张图像")
        
        # 腐蚀检测摘要
        if state.corrosion_detections:
            total_area = sum(d.corrosion_area for d in state.corrosion_detections)
            max_depth = max(d.corrosion_depth for d in state.corrosion_detections)
            summary_parts.append(f"腐蚀检测: 发现 {len(state.corrosion_detections)} 个腐蚀点")
            summary_parts.append(f"总腐蚀面积: {total_area:.2f} 平方毫米")
            summary_parts.append(f"最大腐蚀深度: {max_depth:.2f} 毫米")
        else:
            summary_parts.append("腐蚀检测: 未发现明显腐蚀")
        
        # 风险评估摘要
        if state.risk_assessment:
            summary_parts.append(f"风险等级: {state.risk_assessment.corrosion_level.value}")
            summary_parts.append(f"风险评分: {state.risk_assessment.risk_score:.2f}")
            summary_parts.append(f"紧急程度: {state.risk_assessment.urgency}")
        
        return "\n".join(summary_parts)
    
    def _generate_enhanced_summary(self, state: AgentState, base_summary: str) -> str:
        """使用LLM生成增强的报告摘要"""
        try:
            enhanced_summary = llm_service.generate_enhanced_report_summary(
                state.sensor_readings,
                state.corrosion_detections,
                state.risk_assessment,
                state.platform_id,
                state.inspection_area
            )
            
            if enhanced_summary and len(enhanced_summary.strip()) > 50:
                print(f"🤖 LLM生成增强摘要: {len(enhanced_summary)}字")
                return enhanced_summary
            else:
                return base_summary
                
        except Exception as e:
            print(f"⚠️ LLM摘要增强失败: {e}")
            return base_summary
    
    def _calculate_next_inspection_date(self, risk_assessment: Optional[RiskAssessment]) -> datetime:
        """计算下次检测日期"""
        from dateutil.relativedelta import relativedelta
        
        current_date = datetime.now()
        
        if not risk_assessment:
            return current_date + relativedelta(months=6)
        
        level = risk_assessment.corrosion_level
        
        if level == CorrosionLevel.LOW:
            return current_date + relativedelta(months=6)
        elif level == CorrosionLevel.MEDIUM:
            return current_date + relativedelta(months=3)
        elif level == CorrosionLevel.HIGH:
            return current_date + relativedelta(months=1)
        else:  # CRITICAL
            return current_date + relativedelta(weeks=1)
    
    def _save_report(self, report: InspectionReport):
        """保存报告到文件"""
        try:
            # 创建输出目录
            output_dir = Path(config.output_path) / "reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存JSON格式报告
            json_file = output_dir / f"{report.report_id}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report.dict(), f, ensure_ascii=False, indent=2, default=str)
            
            print(f"报告已保存到: {json_file}")
            
        except Exception as e:
            print(f"保存报告失败: {e}")