"""
LLM服务模块
集成阿里百炼平台qwen-plus模型
用于增强腐蚀检测分析和报告生成
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import dashscope
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    print("⚠️ dashscope未安装，将使用本地分析模式")

from ..config import config
from ..models import CorrosionDetection, RiskAssessment, SensorData


class QwenLLMService:
    """阿里百炼qwen-plus模型服务"""
    
    def __init__(self):
        if DASHSCOPE_AVAILABLE:
            dashscope.api_key = config.dashscope_api_key
            self.model_name = config.qwen_model
            self.available = True
        else:
            self.available = False
            print("⚠️ LLM服务不可用，将使用传统分析方法")
    
    def analyze_corrosion_data(self, 
                              sensor_data: List[SensorData], 
                              corrosion_detections: List[CorrosionDetection]) -> Dict[str, Any]:
        """使用LLM分析腐蚀数据"""
        if not self.available:
            return self._fallback_analysis(sensor_data, corrosion_detections)
        
        # 构建分析提示
        prompt = self._build_analysis_prompt(sensor_data, corrosion_detections)
        
        try:
            response = Generation.call(
                model=self.model_name,
                prompt=prompt,
                temperature=0.1,  # 降低温度以获得更稳定的分析结果
                max_tokens=1500
            )
            
            if response.status_code == 200:
                result = response.output.text
                return self._parse_analysis_result(result)
            else:
                print(f"⚠️ LLM调用失败: {response.message}")
                return self._fallback_analysis(sensor_data, corrosion_detections)
                
        except Exception as e:
            print(f"⚠️ LLM调用异常: {e}")
            return self._fallback_analysis(sensor_data, corrosion_detections)
    
    def generate_enhanced_report_summary(self, 
                                       sensor_data: List[SensorData],
                                       corrosion_detections: List[CorrosionDetection],
                                       risk_assessment: RiskAssessment,
                                       platform_id: str,
                                       inspection_area: str) -> str:
        """生成增强的报告摘要"""
        if not self.available:
            return self._fallback_summary(sensor_data, corrosion_detections, risk_assessment, platform_id, inspection_area)
        
        prompt = self._build_summary_prompt(sensor_data, corrosion_detections, risk_assessment, platform_id, inspection_area)
        
        try:
            response = Generation.call(
                model=self.model_name,
                prompt=prompt,
                temperature=0.2,
                max_tokens=1000
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
            else:
                print(f"⚠️ 摘要生成失败: {response.message}")
                return self._fallback_summary(sensor_data, corrosion_detections, risk_assessment, platform_id, inspection_area)
                
        except Exception as e:
            print(f"⚠️ 摘要生成异常: {e}")
            return self._fallback_summary(sensor_data, corrosion_detections, risk_assessment, platform_id, inspection_area)
    
    def generate_maintenance_insights(self, risk_assessment: RiskAssessment) -> List[str]:
        """生成深度维护洞察"""
        if not self.available:
            return risk_assessment.recommendations if risk_assessment else []
        
        prompt = f"""作为海上石油平台维护专家，基于以下风险评估结果，提供具体的维护洞察和建议：

风险等级: {risk_assessment.corrosion_level}
风险评分: {risk_assessment.risk_score:.2f}
紧急程度: {risk_assessment.urgency}
当前建议: {', '.join(risk_assessment.recommendations)}

请提供3-5条具体的、可操作的维护洞察，每条建议应包含：
1. 具体的执行步骤
2. 时间要求
3. 资源需求
4. 预期效果

要求：
- 建议要专业、具体、可执行
- 考虑海上作业的特殊性
- 关注安全和成本效益
- 每条建议控制在50字以内

请直接返回编号的建议列表，不需要其他格式："""

        try:
            response = Generation.call(
                model=self.model_name,
                prompt=prompt,
                temperature=0.3,
                max_tokens=800
            )
            
            if response.status_code == 200:
                result = response.output.text.strip()
                # 解析返回的建议列表
                insights = []
                lines = result.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        # 清理编号和格式
                        clean_line = line
                        for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '•']:
                            if clean_line.startswith(prefix):
                                clean_line = clean_line[len(prefix):].strip()
                                break
                        insights.append(clean_line)
                
                return insights[:5] if insights else risk_assessment.recommendations
            else:
                return risk_assessment.recommendations
                
        except Exception as e:
            print(f"⚠️ 维护洞察生成异常: {e}")
            return risk_assessment.recommendations
    
    def _build_analysis_prompt(self, sensor_data: List[SensorData], corrosion_detections: List[CorrosionDetection]) -> str:
        """构建腐蚀分析提示"""
        sensor_summary = self._format_sensor_data(sensor_data)
        corrosion_summary = self._format_corrosion_data(corrosion_detections)
        
        prompt = f"""作为海上石油平台腐蚀检测专家，请分析以下数据：

传感器数据：
{sensor_summary}

腐蚀检测结果：
{corrosion_summary}

请基于以上数据进行专业分析，重点关注：
1. 腐蚀的严重程度评估
2. 可能的腐蚀成因分析
3. 环境因素的影响
4. 腐蚀发展趋势预测

请以JSON格式返回分析结果，包含以下字段：
- severity_assessment: 严重程度评估(字符串)
- root_causes: 可能原因列表
- environmental_factors: 环境因素影响
- trend_prediction: 发展趋势预测
- technical_insights: 技术洞察

确保返回有效的JSON格式。"""

        return prompt
    
    def _build_summary_prompt(self, sensor_data: List[SensorData], corrosion_detections: List[CorrosionDetection],
                             risk_assessment: RiskAssessment, platform_id: str, inspection_area: str) -> str:
        """构建报告摘要提示"""
        sensor_summary = self._format_sensor_data(sensor_data)
        corrosion_summary = self._format_corrosion_data(corrosion_detections)
        
        prompt = f"""作为海上石油平台检测报告撰写专家，请为以下检测结果生成专业的报告摘要：

平台信息：
- 平台ID: {platform_id}
- 检测区域: {inspection_area}
- 检测时间: {datetime.now().strftime('%Y年%m月%d日')}

传感器数据摘要：
{sensor_summary}

腐蚀检测结果：
{corrosion_summary}

风险评估：
- 风险等级: {risk_assessment.corrosion_level}
- 风险评分: {risk_assessment.risk_score:.2f}
- 紧急程度: {risk_assessment.urgency}

请生成一份200-300字的专业检测报告摘要，内容应包括：
1. 检测概况
2. 主要发现
3. 风险评估结论
4. 关键建议

要求：
- 语言专业、准确
- 突出重点问题
- 便于管理层快速理解
- 符合工业检测报告标准"""

        return prompt
    
    def _format_sensor_data(self, sensor_data: List[SensorData]) -> str:
        """格式化传感器数据"""
        if not sensor_data:
            return "无传感器数据"
        
        summary = []
        for sensor in sensor_data:
            summary.append(f"- {sensor.sensor_type}: {sensor.value}{sensor.unit} (质量: {sensor.quality:.2f})")
        
        return "\n".join(summary)
    
    def _format_corrosion_data(self, corrosion_detections: List[CorrosionDetection]) -> str:
        """格式化腐蚀检测数据"""
        if not corrosion_detections:
            return "未检测到腐蚀"
        
        summary = []
        for detection in corrosion_detections:
            summary.append(f"- {detection.corrosion_type}: 面积{detection.corrosion_area:.1f}mm², "
                         f"深度{detection.corrosion_depth:.1f}mm, 置信度{detection.confidence:.2f}")
        
        return "\n".join(summary)
    
    def _parse_analysis_result(self, result: str) -> Dict[str, Any]:
        """解析LLM分析结果"""
        try:
            # 尝试解析JSON
            parsed = json.loads(result)
            return parsed
        except json.JSONDecodeError:
            # 如果解析失败，提取文本信息
            return {
                "severity_assessment": "基于LLM的综合分析",
                "root_causes": ["需要进一步分析"],
                "environmental_factors": "海洋环境因素影响",
                "trend_prediction": "需要持续监测",
                "technical_insights": result[:200] + "..." if len(result) > 200 else result
            }
    
    def _fallback_analysis(self, sensor_data: List[SensorData], corrosion_detections: List[CorrosionDetection]) -> Dict[str, Any]:
        """回退分析方法"""
        return {
            "severity_assessment": f"检测到{len(corrosion_detections)}个腐蚀点",
            "root_causes": ["海洋环境腐蚀", "材料老化"],
            "environmental_factors": "高湿度、盐雾环境",
            "trend_prediction": "需要定期监测",
            "technical_insights": "建议使用传统分析方法进行详细评估"
        }
    
    def _fallback_summary(self, sensor_data: List[SensorData], corrosion_detections: List[CorrosionDetection],
                         risk_assessment: RiskAssessment, platform_id: str, inspection_area: str) -> str:
        """回退摘要生成方法"""
        summary_parts = [
            f"【检测概况】对{platform_id}平台{inspection_area}进行了腐蚀检测，收集了{len(sensor_data)}项传感器数据。",
            f"【主要发现】{'检测到' + str(len(corrosion_detections)) + '个腐蚀点' if corrosion_detections else '未发现明显腐蚀'}。",
            f"【风险评估】风险等级为{risk_assessment.corrosion_level}，评分{risk_assessment.risk_score:.2f}。",
            f"【关键建议】{risk_assessment.recommendations[0] if risk_assessment.recommendations else '继续定期监测'}。"
        ]
        return "".join(summary_parts)


# 全局LLM服务实例
llm_service = QwenLLMService()