"""
腐蚀检测Agent核心工作流
基于LangGraph构建的多节点检测流程
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# 使用本地的模拟LangGraph实现
# 强制使用mock版本以确保行为一致性
from ..utils.mock_langgraph import StateGraph, END

from ..models import AgentState, CorrosionLevel
from ..config import config
from .nodes import (
    DataCollectionNode,
    CorrosionAnalysisNode, 
    RiskAssessmentNode,
    ReportGenerationNode
)

class CorrosionDetectionAgent:
    """腐蚀检测Agent主类"""
    
    def __init__(self):
        self.graph = self._build_graph()
        self.nodes = {
            "data_collection": DataCollectionNode(),
            "corrosion_analysis": CorrosionAnalysisNode(),
            "risk_assessment": RiskAssessmentNode(),
            "report_generation": ReportGenerationNode()
        }
    
    def _build_graph(self) -> StateGraph:
        """构建Agent工作流图"""
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("data_collection", self._data_collection_node)
        workflow.add_node("corrosion_analysis", self._corrosion_analysis_node)
        workflow.add_node("risk_assessment", self._risk_assessment_node)
        workflow.add_node("report_generation", self._report_generation_node)
        
        # 定义工作流路径
        workflow.set_entry_point("data_collection")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "data_collection",
            self._should_continue_to_analysis,
            {
                "continue": "corrosion_analysis",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "corrosion_analysis", 
            self._should_continue_to_risk_assessment,
            {
                "continue": "risk_assessment",
                "retry": "corrosion_analysis",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "risk_assessment",
            self._should_generate_report,
            {
                "generate": "report_generation",
                "end": END
            }
        )
        
        workflow.add_edge("report_generation", END)
        
        return workflow.compile()
    
    def _data_collection_node(self, state: AgentState) -> AgentState:
        """数据收集节点"""
        state.current_step = "data_collection"
        state.last_update = datetime.now()
        
        try:
            # 执行数据收集
            state = self.nodes["data_collection"].execute(state)
            print(f"数据收集完成: 传感器数据 {len(state.sensor_readings)} 条, 图像数据 {len(state.processed_images)} 张")
        except Exception as e:
            state.errors.append(f"数据收集失败: {str(e)}")
            print(f"数据收集错误: {e}")
        
        return state
    
    def _corrosion_analysis_node(self, state: AgentState) -> AgentState:
        """腐蚀分析节点"""
        state.current_step = "corrosion_analysis"
        state.last_update = datetime.now()
        
        try:
            # 执行腐蚀分析
            state = self.nodes["corrosion_analysis"].execute(state)
            print(f"腐蚀分析完成: 检测到 {len(state.corrosion_detections)} 个腐蚀点")
        except Exception as e:
            state.errors.append(f"腐蚀分析失败: {str(e)}")
            print(f"腐蚀分析错误: {e}")
        
        return state
    
    def _risk_assessment_node(self, state: AgentState) -> AgentState:
        """风险评估节点"""
        state.current_step = "risk_assessment"
        state.last_update = datetime.now()
        
        try:
            # 执行风险评估
            state = self.nodes["risk_assessment"].execute(state)
            risk_level = state.risk_assessment.corrosion_level if state.risk_assessment else "UNKNOWN"
            print(f"风险评估完成: 风险等级 {risk_level}")
        except Exception as e:
            state.errors.append(f"风险评估失败: {str(e)}")
            print(f"风险评估错误: {e}")
        
        return state
    
    def _report_generation_node(self, state: AgentState) -> AgentState:
        """报告生成节点"""
        state.current_step = "report_generation"
        state.last_update = datetime.now()
        
        try:
            # 生成最终报告
            state = self.nodes["report_generation"].execute(state)
            print(f"报告生成完成: 报告ID {state.final_report.report_id if state.final_report else 'None'}")
        except Exception as e:
            state.errors.append(f"报告生成失败: {str(e)}")
            print(f"报告生成错误: {e}")
        
        return state
    
    def _should_continue_to_analysis(self, state: AgentState) -> str:
        """判断是否继续到分析阶段"""
        if state.errors:
            return "end"
        
        if not state.sensor_readings and not state.processed_images:
            state.errors.append("没有可用的传感器数据或图像数据")
            return "end"
        
        return "continue"
    
    def _should_continue_to_risk_assessment(self, state: AgentState) -> str:
        """判断是否继续到风险评估阶段"""
        if state.errors:
            return "end"
        
        if not state.corrosion_detections:
            state.warnings.append("未检测到腐蚀，跳过风险评估")
            return "end"
        
        return "continue"
    
    def _should_generate_report(self, state: AgentState) -> str:
        """判断是否生成报告"""
        # 总是生成报告，即使没有检测到腐蚀
        return "generate"
    
    async def run_inspection(self, 
                           platform_id: str,
                           inspection_area: str,
                           sensor_files: Optional[List[str]] = None,
                           image_files: Optional[List[str]] = None) -> AgentState:
        """运行完整的检测流程"""
        
        # 初始化状态
        initial_state = AgentState(
            session_id=str(uuid.uuid4()),
            current_step="init",
            platform_id=platform_id,
            inspection_area=inspection_area,
            image_files=image_files or [],
            start_time=datetime.now(),
            last_update=datetime.now()
        )
        
        print(f"开始检测流程: 平台 {platform_id}, 区域 {inspection_area}")
        
        # 运行工作流
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            print(f"检测流程完成: 会话 {final_state.session_id}")
            
            if final_state.errors:
                print(f"发现错误: {final_state.errors}")
            if final_state.warnings:
                print(f"警告信息: {final_state.warnings}")
                
            return final_state
            
        except Exception as e:
            print(f"工作流执行失败: {e}")
            initial_state.errors.append(f"工作流执行失败: {str(e)}")
            return initial_state
    
    def run_inspection_sync(self, 
                           platform_id: str,
                           inspection_area: str,
                           sensor_files: Optional[List[str]] = None,
                           image_files: Optional[List[str]] = None) -> AgentState:
        """同步运行检测流程"""
        
        # 初始化状态
        initial_state = AgentState(
            session_id=str(uuid.uuid4()),
            current_step="init", 
            platform_id=platform_id,
            inspection_area=inspection_area,
            image_files=image_files or [],
            start_time=datetime.now(),
            last_update=datetime.now()
        )
        
        print(f"开始检测流程: 平台 {platform_id}, 区域 {inspection_area}")
        
        # 运行工作流
        try:
            final_state = self.graph.invoke(initial_state)
            
            # 检查返回的类型
            print(f"工作流返回类型: {type(final_state)}")
            
            if isinstance(final_state, dict):
                print(f"错误: 工作流返回了字典而不是AgentState对象")
                print(f"字典内容: {list(final_state.keys()) if isinstance(final_state, dict) else 'N/A'}")
                # 返回初始状态而不是字典
                initial_state.errors.append("工作流返回了错误的数据类型")
                return initial_state
            
            print(f"检测流程完成: 会话 {final_state.session_id}")
            
            if final_state.errors:
                print(f"发现错误: {final_state.errors}")
            if final_state.warnings:
                print(f"警告信息: {final_state.warnings}")
                
            return final_state
            
        except Exception as e:
            print(f"工作流执行失败: {e}")
            initial_state.errors.append(f"工作流执行失败: {str(e)}")
            return initial_state