#!/usr/bin/env python3
"""
集成阿里百炼qwen-plus的腐蚀检测Agent演示
展示LLM增强的分析和报告生成功能
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# 简化的数据模型（与demo_simple.py相同）
class SensorType:
    THICKNESS = "thickness"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PH = "ph"

class CorrosionLevel:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SensorData:
    def __init__(self, sensor_id: str, sensor_type: str, value: float, unit: str, 
                 timestamp: datetime, location: Dict[str, float], quality: float):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.value = value
        self.unit = unit
        self.timestamp = timestamp
        self.location = location
        self.quality = quality

class CorrosionDetection:
    def __init__(self, detection_id: str, corrosion_area: float, corrosion_depth: float,
                 corrosion_type: str, confidence: float, timestamp: datetime):
        self.detection_id = detection_id
        self.corrosion_area = corrosion_area
        self.corrosion_depth = corrosion_depth
        self.corrosion_type = corrosion_type
        self.confidence = confidence
        self.timestamp = timestamp

class RiskAssessment:
    def __init__(self, assessment_id: str, corrosion_level: str, risk_score: float,
                 recommendations: List[str], urgency: str, timestamp: datetime):
        self.assessment_id = assessment_id
        self.corrosion_level = corrosion_level
        self.risk_score = risk_score
        self.recommendations = recommendations
        self.urgency = urgency
        self.timestamp = timestamp

class InspectionReport:
    def __init__(self, report_id: str, platform_id: str, area_inspected: str,
                 sensor_data: List[SensorData], corrosion_detections: List[CorrosionDetection],
                 risk_assessment: Optional[RiskAssessment], summary: str, timestamp: datetime,
                 llm_analysis: Optional[Dict[str, Any]] = None):
        self.report_id = report_id
        self.platform_id = platform_id
        self.area_inspected = area_inspected
        self.sensor_data = sensor_data
        self.corrosion_detections = corrosion_detections
        self.risk_assessment = risk_assessment
        self.summary = summary
        self.timestamp = timestamp
        self.llm_analysis = llm_analysis or {}

class AgentState:
    def __init__(self, session_id: str, platform_id: str, inspection_area: str):
        self.session_id = session_id
        self.platform_id = platform_id
        self.inspection_area = inspection_area
        self.current_step = "init"
        self.start_time = datetime.now()
        self.sensor_readings = []
        self.corrosion_detections = []
        self.risk_assessment = None
        self.final_report = None
        self.errors = []
        self.warnings = []
        self.llm_analysis = {}

# LLM服务模拟类
class MockQwenLLMService:
    """模拟的qwen-plus LLM服务（用于演示）"""
    
    def __init__(self):
        self.available = True
        print("🤖 初始化阿里百炼qwen-plus模型服务（演示模式）")
    
    def analyze_corrosion_data(self, sensor_data: List[SensorData], 
                              corrosion_detections: List[CorrosionDetection]) -> Dict[str, Any]:
        """模拟LLM腐蚀数据分析"""
        if not corrosion_detections:
            return {
                "severity_assessment": "未检测到明显腐蚀，结构状况良好",
                "root_causes": ["无明显腐蚀迹象"],
                "environmental_factors": "环境条件相对稳定",
                "trend_prediction": "预计短期内无重大变化",
                "technical_insights": "建议继续定期监测，保持现有防护措施"
            }
        
        total_area = sum(d.corrosion_area for d in corrosion_detections)
        max_depth = max(d.corrosion_depth for d in corrosion_detections)
        
        if total_area > 500:
            severity = "严重腐蚀，需要立即关注"
            causes = ["海洋环境长期侵蚀", "防腐层失效", "材料疲劳老化"]
            prediction = "腐蚀速度可能加快，存在结构风险"
        elif total_area > 200:
            severity = "中等程度腐蚀，需要及时处理"
            causes = ["局部防护不足", "环境因素影响", "维护周期偏长"]
            prediction = "如不及时处理，腐蚀可能扩散"
        else:
            severity = "轻微腐蚀，可控范围内"
            causes = ["正常环境磨损", "局部应力集中"]
            prediction = "腐蚀发展相对缓慢"
        
        return {
            "severity_assessment": severity,
            "root_causes": causes,
            "environmental_factors": "高盐雾、高湿度海洋环境加速腐蚀进程",
            "trend_prediction": prediction,
            "technical_insights": f"检测到{len(corrosion_detections)}个腐蚀点，总面积{total_area:.1f}mm²，最大深度{max_depth:.1f}mm。建议采用多层防护策略。"
        }
    
    def generate_enhanced_report_summary(self, sensor_data: List[SensorData],
                                       corrosion_detections: List[CorrosionDetection],
                                       risk_assessment: RiskAssessment,
                                       platform_id: str, inspection_area: str) -> str:
        """模拟LLM增强报告摘要生成"""
        current_date = datetime.now().strftime('%Y年%m月%d日')
        
        if not corrosion_detections:
            return f"""【检测概况】{current_date}对{platform_id}平台{inspection_area}完成全面腐蚀检测，采用多传感器融合技术收集了{len(sensor_data)}项关键指标数据。
【主要发现】检测结果显示该区域结构完整性良好，未发现明显腐蚀缺陷。各项传感器数据均在正常范围内，表明当前防护措施有效。
【风险评估】综合评估风险等级为{risk_assessment.corrosion_level}，风险评分{risk_assessment.risk_score:.2f}，整体安全状况稳定。
【关键建议】建议保持现有维护周期，继续执行定期监测方案，确保防腐系统的持续有效性。"""
        
        total_area = sum(d.corrosion_area for d in corrosion_detections)
        max_depth = max(d.corrosion_depth for d in corrosion_detections)
        
        urgency_desc = {
            "低": "无需立即行动",
            "中等": "建议在下个维护周期内处理", 
            "高": "需要优先安排维护",
            "紧急": "要求立即采取行动"
        }.get(risk_assessment.urgency, "需要关注")
        
        return f"""【检测概况】{current_date}对{platform_id}平台{inspection_area}进行了精密腐蚀检测，运用先进传感技术获取{len(sensor_data)}项实时数据，检测覆盖面积达到100%。
【主要发现】检测识别出{len(corrosion_detections)}处腐蚀点，累计影响面积{total_area:.1f}平方毫米，最深腐蚀达{max_depth:.1f}毫米。腐蚀模式主要表现为{'、'.join(set(d.corrosion_type for d in corrosion_detections))}。
【风险评估】基于多因子分析模型，评定风险等级为{risk_assessment.corrosion_level}，综合风险指数{risk_assessment.risk_score:.2f}，{urgency_desc}。
【关键建议】{risk_assessment.recommendations[0] if risk_assessment.recommendations else '继续监测'}。建议结合环境条件优化防护策略，确保平台长期安全运营。"""
    
    def generate_maintenance_insights(self, risk_assessment: RiskAssessment) -> List[str]:
        """模拟LLM维护洞察生成"""
        level = risk_assessment.corrosion_level
        score = risk_assessment.risk_score
        
        if level == "CRITICAL":
            return [
                "立即启动应急维修预案，48小时内完成受损区域临时防护",
                "组织专业团队进行结构安全评估，评估承载能力变化",
                "实施24小时连续监测，设置多点传感器实时跟踪",
                "紧急采购高性能防腐材料，准备大面积修复作业",
                "制定详细的分阶段维修计划，确保作业期间平台安全"
            ]
        elif level == "HIGH":
            return [
                "在下次停机窗口期内完成重点区域防腐层更新",
                "增加检测频率至每月一次，重点监控腐蚀发展速度",
                "评估并升级现有阴极保护系统，提高防护电流密度",
                "建立腐蚀数据库，跟踪历史变化趋势和效果评估",
                "培训维护人员掌握新型防腐技术和检测方法"
            ]
        elif level == "MEDIUM":
            return [
                "制定预防性维护计划，每季度进行局部防腐处理",
                "优化环境控制措施，降低腐蚀性介质浓度",
                "定期清洁表面积盐，保持防腐涂层良好状态",
                "建立备件库存管理，确保维修材料及时供应",
                "与设备厂商合作，获取最新防腐技术支持"
            ]
        else:  # LOW
            return [
                "保持现有维护周期，每半年进行全面检测评估",
                "完善日常巡检制度，及时发现潜在腐蚀风险点",
                "定期更新防腐涂料，延长防护系统使用寿命",
                "建立环境监测体系，掌握腐蚀影响因素变化",
                "开展预测性维护试点，探索智能化维护模式"
            ]

class EnhancedCorrosionAgent:
    """集成LLM功能的增强腐蚀检测Agent"""
    
    def __init__(self):
        print("🔧 初始化增强型腐蚀检测Agent...")
        self.llm_service = MockQwenLLMService()
    
    def run_inspection(self, platform_id: str, inspection_area: str) -> AgentState:
        """运行完整的检测流程"""
        print(f"🚀 开始智能腐蚀检测: 平台={platform_id}, 区域={inspection_area}")
        
        # 初始化状态
        state = AgentState(
            session_id=str(uuid.uuid4()),
            platform_id=platform_id,
            inspection_area=inspection_area
        )
        
        try:
            # 1. 数据收集
            state = self._data_collection(state)
            
            # 2. 腐蚀分析（含LLM增强）
            state = self._corrosion_analysis_with_llm(state)
            
            # 3. 风险评估（含LLM增强）
            state = self._risk_assessment_with_llm(state)
            
            # 4. 报告生成（含LLM增强）
            state = self._generate_enhanced_report(state)
            
            print(f"✅ 智能检测完成! 会话ID: {state.session_id}")
            
        except Exception as e:
            print(f"❌ 检测过程发生错误: {e}")
            state.errors.append(str(e))
        
        return state
    
    def _data_collection(self, state: AgentState) -> AgentState:
        """数据收集（与demo_simple相同）"""
        print("📊 开始数据收集...")
        state.current_step = "data_collection"
        
        import random
        
        # 厚度传感器数据
        for i in range(3):
            thickness_loss = random.uniform(0, 2.5)
            reading = SensorData(
                sensor_id=f"thickness_{state.inspection_area}_{i+1}",
                sensor_type=SensorType.THICKNESS,
                value=12.0 - thickness_loss,
                unit="mm",
                timestamp=datetime.now(),
                location={"x": i * 10, "y": 0, "z": 0},
                quality=random.uniform(0.85, 0.98)
            )
            state.sensor_readings.append(reading)
        
        # 环境传感器数据
        env_sensors = [
            (SensorType.TEMPERATURE, random.uniform(15, 35), "°C"),
            (SensorType.HUMIDITY, random.uniform(60, 90), "%RH"),
            (SensorType.PH, random.uniform(7.5, 8.5), "pH")
        ]
        
        for sensor_type, value, unit in env_sensors:
            reading = SensorData(
                sensor_id=f"{sensor_type}_{state.inspection_area}",
                sensor_type=sensor_type,
                value=value,
                unit=unit,
                timestamp=datetime.now(),
                location={"x": 0, "y": 0, "z": 0},
                quality=random.uniform(0.88, 0.96)
            )
            state.sensor_readings.append(reading)
        
        print(f"   ✓ 收集了 {len(state.sensor_readings)} 个传感器读数")
        return state
    
    def _corrosion_analysis_with_llm(self, state: AgentState) -> AgentState:
        """腐蚀分析（含LLM增强）"""
        print("🔍 开始智能腐蚀分析...")
        state.current_step = "corrosion_analysis"
        
        # 传统检测方法
        thickness_readings = [r for r in state.sensor_readings if r.sensor_type == SensorType.THICKNESS]
        
        import random
        num_corrosions = random.randint(0, 3)
        
        for i in range(num_corrosions):
            thickness_loss = 12.0 - min(r.value for r in thickness_readings)
            corrosion_area = random.uniform(50, 500)
            corrosion_depth = max(0.1, thickness_loss + random.uniform(-0.3, 0.5))
            
            if corrosion_area < 100:
                corrosion_type = "点腐蚀"
            elif corrosion_area > 300:
                corrosion_type = "大面积腐蚀"
            else:
                corrosion_type = "局部腐蚀"
            
            detection = CorrosionDetection(
                detection_id=f"detection_{state.inspection_area}_{i+1}",
                corrosion_area=corrosion_area,
                corrosion_depth=corrosion_depth,
                corrosion_type=corrosion_type,
                confidence=random.uniform(0.7, 0.95),
                timestamp=datetime.now()
            )
            state.corrosion_detections.append(detection)
        
        # LLM增强分析
        print("   🤖 启动qwen-plus智能分析...")
        state.llm_analysis = self.llm_service.analyze_corrosion_data(
            state.sensor_readings, 
            state.corrosion_detections
        )
        
        print(f"   ✓ 检测到 {len(state.corrosion_detections)} 个腐蚀点")
        print(f"   🤖 AI洞察: {state.llm_analysis.get('severity_assessment', 'N/A')}")
        
        return state
    
    def _risk_assessment_with_llm(self, state: AgentState) -> AgentState:
        """风险评估（含LLM增强）"""
        print("⚠️  开始智能风险评估...")
        state.current_step = "risk_assessment"
        
        if not state.corrosion_detections:
            state.risk_assessment = RiskAssessment(
                assessment_id=f"risk_{state.session_id}",
                corrosion_level=CorrosionLevel.LOW,
                risk_score=0.1,
                recommendations=["继续定期监测", "保持当前维护计划"],
                urgency="低",
                timestamp=datetime.now()
            )
        else:
            # 传统风险计算
            total_area = sum(d.corrosion_area for d in state.corrosion_detections)
            max_depth = max(d.corrosion_depth for d in state.corrosion_detections)
            
            area_factor = min(1.0, total_area / 1000.0)
            depth_factor = min(1.0, max_depth / 3.0)
            count_factor = min(1.0, len(state.corrosion_detections) / 5.0)
            
            risk_score = (area_factor * 0.4 + depth_factor * 0.5 + count_factor * 0.1)
            
            if risk_score < 0.3:
                level = CorrosionLevel.LOW
                urgency = "低"
            elif risk_score < 0.6:
                level = CorrosionLevel.MEDIUM
                urgency = "中等"
            elif risk_score < 0.8:
                level = CorrosionLevel.HIGH
                urgency = "高"
            else:
                level = CorrosionLevel.CRITICAL
                urgency = "紧急"
            
            # 生成基础建议
            base_recommendations = ["需要进一步分析", "制定维护计划"]
            
            # 创建临时风险评估用于LLM增强
            temp_assessment = RiskAssessment(
                assessment_id=f"risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                corrosion_level=level,
                risk_score=risk_score,
                recommendations=base_recommendations,
                urgency=urgency,
                timestamp=datetime.now()
            )
            
            # LLM增强维护建议
            print("   🤖 生成qwen-plus智能维护建议...")
            enhanced_recommendations = self.llm_service.generate_maintenance_insights(temp_assessment)
            
            state.risk_assessment = RiskAssessment(
                assessment_id=temp_assessment.assessment_id,
                corrosion_level=level,
                risk_score=risk_score,
                recommendations=enhanced_recommendations,
                urgency=urgency,
                timestamp=datetime.now()
            )
        
        print(f"   ✓ 风险等级: {state.risk_assessment.corrosion_level}")
        print(f"   ✓ 风险评分: {state.risk_assessment.risk_score:.2f}")
        print(f"   🤖 AI建议: {len(state.risk_assessment.recommendations)}条智能维护建议")
        
        return state
    
    def _generate_enhanced_report(self, state: AgentState) -> AgentState:
        """生成增强报告"""
        print("📄 开始生成智能报告...")
        state.current_step = "report_generation"
        
        # LLM增强摘要生成
        print("   🤖 qwen-plus生成专业摘要...")
        enhanced_summary = self.llm_service.generate_enhanced_report_summary(
            state.sensor_readings,
            state.corrosion_detections,
            state.risk_assessment,
            state.platform_id,
            state.inspection_area
        )
        
        # 创建报告
        state.final_report = InspectionReport(
            report_id=f"report_{state.session_id}",
            platform_id=state.platform_id,
            area_inspected=state.inspection_area,
            sensor_data=state.sensor_readings,
            corrosion_detections=state.corrosion_detections,
            risk_assessment=state.risk_assessment,
            summary=enhanced_summary,
            timestamp=datetime.now(),
            llm_analysis=state.llm_analysis
        )
        
        # 保存报告
        self._save_enhanced_report(state.final_report)
        
        print(f"   ✓ 智能报告ID: {state.final_report.report_id}")
        print(f"   🤖 包含AI分析洞察和专业建议")
        
        return state
    
    def _save_enhanced_report(self, report: InspectionReport):
        """保存增强报告"""
        try:
            output_dir = Path("outputs/reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 转换为字典格式，包含LLM分析
            report_dict = {
                "report_id": report.report_id,
                "timestamp": report.timestamp.isoformat(),
                "platform_id": report.platform_id,
                "area_inspected": report.area_inspected,
                "sensor_data": [
                    {
                        "sensor_id": s.sensor_id,
                        "sensor_type": s.sensor_type,
                        "value": s.value,
                        "unit": s.unit,
                        "location": s.location,
                        "quality": s.quality
                    } for s in report.sensor_data
                ],
                "corrosion_detections": [
                    {
                        "detection_id": d.detection_id,
                        "corrosion_area": d.corrosion_area,
                        "corrosion_depth": d.corrosion_depth,
                        "corrosion_type": d.corrosion_type,
                        "confidence": d.confidence
                    } for d in report.corrosion_detections
                ],
                "risk_assessment": {
                    "assessment_id": report.risk_assessment.assessment_id,
                    "corrosion_level": report.risk_assessment.corrosion_level,
                    "risk_score": report.risk_assessment.risk_score,
                    "recommendations": report.risk_assessment.recommendations,
                    "urgency": report.risk_assessment.urgency
                } if report.risk_assessment else None,
                "llm_analysis": report.llm_analysis,  # 新增LLM分析结果
                "summary": report.summary,
                "ai_enhanced": True  # 标记为AI增强报告
            }
            
            # 保存JSON文件
            json_file = output_dir / f"{report.report_id}_enhanced.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, ensure_ascii=False, indent=2)
            
            print(f"   ✓ 增强报告已保存到: {json_file}")
            
        except Exception as e:
            print(f"   ❌ 保存报告失败: {e}")

def main():
    """主函数"""
    print("🌊 海上石油平台腐蚀检测Agent - qwen-plus增强版")
    print("=" * 70)
    
    # 创建增强Agent实例
    agent = EnhancedCorrosionAgent()
    
    # 运行示例检测
    examples = [
        ("PLATFORM_001", "甲板区域A"),
        ("PLATFORM_002", "管道区域B"),
        ("PLATFORM_003", "储罐区域C")
    ]
    
    results = []
    
    for platform_id, area in examples:
        print(f"\\n{'='*70}")
        result = agent.run_inspection(platform_id, area)
        results.append(result)
        
        # 显示增强结果摘要
        if result.final_report:
            print("\\n📋 AI增强检测结果摘要:")
            print("-" * 50)
            print(result.final_report.summary)
            
            # 显示LLM分析洞察
            if result.llm_analysis:
                print("\\n🤖 qwen-plus智能分析洞察:")
                print("-" * 30)
                for key, value in result.llm_analysis.items():
                    if key == "root_causes" and isinstance(value, list):
                        print(f"   {key}: {', '.join(value)}")
                    elif key == "technical_insights":
                        print(f"   技术洞察: {value}")
                    else:
                        print(f"   {key}: {value}")
            
            # 显示增强维护建议
            if result.risk_assessment and result.risk_assessment.recommendations:
                print("\\n💡 AI增强维护建议:")
                for i, rec in enumerate(result.risk_assessment.recommendations, 1):
                    print(f"   {i}. {rec}")
        
        if result.errors:
            print(f"\\n❌ 错误: {result.errors}")
    
    print(f"\\n🎉 AI增强演示完成! 共生成了 {len(results)} 个智能检测报告")
    print("\\n📁 增强报告文件保存在: outputs/reports/")
    print("📖 每个报告包含传统分析 + qwen-plus AI洞察")
    print("🤖 体验阿里百炼qwen-plus在工业检测中的强大能力!")

if __name__ == "__main__":
    main()