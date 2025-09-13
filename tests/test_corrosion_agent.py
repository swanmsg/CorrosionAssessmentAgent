"""
腐蚀检测Agent测试用例
"""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path
import sys

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.corrosion_agent import CorrosionDetectionAgent
from src.agents.nodes import DataCollectionNode, CorrosionAnalysisNode, RiskAssessmentNode
from src.models import AgentState, SensorData, SensorType, CorrosionLevel
from src.utils.image_processor import ImageProcessor
from src.config import config


class TestCorrosionDetectionAgent:
    """腐蚀检测Agent测试类"""
    
    def test_agent_initialization(self):
        """测试Agent初始化"""
        agent = CorrosionDetectionAgent()
        assert agent is not None
        assert hasattr(agent, 'graph')
        assert hasattr(agent, 'nodes')
    
    @pytest.mark.asyncio
    async def test_basic_inspection_flow(self):
        """测试基础检测流程"""
        agent = CorrosionDetectionAgent()
        
        result = await agent.run_inspection(
            platform_id="TEST_PLATFORM",
            inspection_area="测试区域"
        )
        
        assert result is not None
        assert result.platform_id == "TEST_PLATFORM"
        assert result.inspection_area == "测试区域"
        assert result.session_id is not None
    
    def test_sync_inspection_flow(self):
        """测试同步检测流程"""
        agent = CorrosionDetectionAgent()
        
        result = agent.run_inspection_sync(
            platform_id="TEST_PLATFORM_SYNC",
            inspection_area="同步测试区域"
        )
        
        assert result is not None
        assert result.platform_id == "TEST_PLATFORM_SYNC"
        assert result.inspection_area == "同步测试区域"


class TestDataCollectionNode:
    """数据收集节点测试类"""
    
    def test_node_initialization(self):
        """测试节点初始化"""
        node = DataCollectionNode()
        assert node is not None
        assert hasattr(node, 'image_processor')
        assert hasattr(node, 'sensor_reader')
    
    def test_data_collection_execution(self):
        """测试数据收集执行"""
        node = DataCollectionNode()
        
        # 创建测试状态
        state = AgentState(
            session_id="test_session",
            current_step="test",
            platform_id="TEST_PLATFORM",
            inspection_area="测试区域",
            start_time=datetime.now(),
            last_update=datetime.now()
        )
        
        # 执行数据收集
        result_state = node.execute(state)
        
        assert result_state is not None
        assert len(result_state.sensor_readings) > 0
        assert len(result_state.processed_images) > 0
    
    def test_sample_image_generation(self):
        """测试示例图像生成"""
        node = DataCollectionNode()
        sample_images = node._generate_sample_images("测试区域")
        
        assert len(sample_images) > 0
        for image_data in sample_images:
            assert image_data.image_id is not None
            assert Path(image_data.file_path).exists()


class TestCorrosionAnalysisNode:
    """腐蚀分析节点测试类"""
    
    def test_node_initialization(self):
        """测试节点初始化"""
        node = CorrosionAnalysisNode()
        assert node is not None
        assert hasattr(node, 'image_processor')
    
    def test_analysis_with_no_images(self):
        """测试无图像时的分析"""
        node = CorrosionAnalysisNode()
        
        state = AgentState(
            session_id="test_session",
            current_step="test",
            platform_id="TEST_PLATFORM",
            inspection_area="测试区域",
            start_time=datetime.now(),
            last_update=datetime.now()
        )
        
        result_state = node.execute(state)
        assert len(result_state.corrosion_detections) == 0


class TestRiskAssessmentNode:
    """风险评估节点测试类"""
    
    def test_node_initialization(self):
        """测试节点初始化"""
        node = RiskAssessmentNode()
        assert node is not None
    
    def test_risk_assessment_no_corrosion(self):
        """测试无腐蚀时的风险评估"""
        node = RiskAssessmentNode()
        
        state = AgentState(
            session_id="test_session",
            current_step="test",
            platform_id="TEST_PLATFORM",
            inspection_area="测试区域",
            start_time=datetime.now(),
            last_update=datetime.now()
        )
        
        result_state = node.execute(state)
        
        assert result_state.risk_assessment is not None
        assert result_state.risk_assessment.corrosion_level == CorrosionLevel.LOW
    
    def test_environmental_factor_calculation(self):
        """测试环境因子计算"""
        node = RiskAssessmentNode()
        
        # 创建测试传感器数据
        sensor_readings = [
            SensorData(
                sensor_id="temp_001",
                sensor_type=SensorType.TEMPERATURE,
                value=25.0,
                unit="°C",
                timestamp=datetime.now(),
                location={"x": 0, "y": 0, "z": 0},
                quality=0.95
            ),
            SensorData(
                sensor_id="humidity_001",
                sensor_type=SensorType.HUMIDITY,
                value=75.0,
                unit="%RH",
                timestamp=datetime.now(),
                location={"x": 0, "y": 0, "z": 0},
                quality=0.92
            )
        ]
        
        env_factor = node._calculate_environmental_factor(sensor_readings)
        assert 0.0 <= env_factor <= 1.0


class TestImageProcessor:
    """图像处理器测试类"""
    
    def test_processor_initialization(self):
        """测试处理器初始化"""
        processor = ImageProcessor()
        assert processor is not None
        assert processor.target_size == (640, 480)
    
    def test_sample_image_creation(self):
        """测试示例图像创建"""
        from src.agents.nodes import DataCollectionNode
        
        node = DataCollectionNode()
        image = node._create_sample_corrosion_image()
        
        assert image is not None
        assert image.shape == (480, 640, 3)
        assert image.dtype.name == 'uint8'


class TestConfiguration:
    """配置测试类"""
    
    def test_config_loading(self):
        """测试配置加载"""
        assert config is not None
        assert hasattr(config, 'low_risk_threshold')
        assert hasattr(config, 'medium_risk_threshold')
        assert hasattr(config, 'high_risk_threshold')
    
    def test_risk_level_determination(self):
        """测试风险等级确定"""
        # 测试低风险
        assert config.get_risk_level(0.2) == "LOW"
        
        # 测试中等风险
        assert config.get_risk_level(0.5) == "MEDIUM"
        
        # 测试高风险
        assert config.get_risk_level(0.7) == "HIGH"
        
        # 测试严重风险
        assert config.get_risk_level(0.9) == "CRITICAL"


@pytest.mark.asyncio
async def test_full_workflow():
    """测试完整工作流"""
    agent = CorrosionDetectionAgent()
    
    result = await agent.run_inspection(
        platform_id="FULL_TEST_PLATFORM",
        inspection_area="完整测试区域"
    )
    
    # 验证完整流程的结果
    assert result.session_id is not None
    assert result.current_step == "report_generation"
    assert result.final_report is not None
    assert result.risk_assessment is not None
    
    # 验证报告内容
    report = result.final_report
    assert report.platform_id == "FULL_TEST_PLATFORM"
    assert report.area_inspected == "完整测试区域"
    assert report.inspector == "Corrosion Detection Agent"
    assert len(report.maintenance_recommendations) > 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])