#!/usr/bin/env python3
"""
腐蚀检测Agent示例程序
展示如何使用CorrosionDetectionAgent进行腐蚀检测
"""

import asyncio
from pathlib import Path
import sys

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent))

from src.agents.corrosion_agent import CorrosionDetectionAgent
from src.config import config


async def example_basic_inspection():
    """基础检测示例"""
    print("=" * 50)
    print("基础腐蚀检测示例")
    print("=" * 50)
    
    # 创建Agent实例
    agent = CorrosionDetectionAgent()
    
    # 运行检测
    result = await agent.run_inspection(
        platform_id="PLATFORM_001",
        inspection_area="甲板区域A"
    )
    
    # 输出结果
    print(f"会话ID: {result.session_id}")
    print(f"检测区域: {result.inspection_area}")
    print(f"传感器读数数量: {len(result.sensor_readings)}")
    print(f"处理的图像数量: {len(result.processed_images)}")
    print(f"检测到的腐蚀点: {len(result.corrosion_detections)}")
    
    if result.risk_assessment:
        print(f"风险等级: {result.risk_assessment.corrosion_level.value}")
        print(f"风险评分: {result.risk_assessment.risk_score:.2f}")
    
    if result.final_report:
        print(f"报告ID: {result.final_report.report_id}")
        print(f"维护建议数量: {len(result.final_report.maintenance_recommendations)}")
    
    print("\\n报告摘要:")
    print("-" * 30)
    if result.final_report:
        print(result.final_report.summary)
    
    return result


async def example_with_sample_data():
    """使用示例数据进行检测"""
    print("=" * 50)
    print("使用示例数据的腐蚀检测")
    print("=" * 50)
    
    # 创建Agent实例
    agent = CorrosionDetectionAgent()
    
    # 准备示例数据文件路径
    sample_sensor_file = "data/sample/sensor_data.json"
    
    # 运行检测
    result = await agent.run_inspection(
        platform_id="PLATFORM_002",
        inspection_area="管道区域B",
        sensor_files=[sample_sensor_file] if Path(sample_sensor_file).exists() else []
    )
    
    # 详细输出分析结果
    print(f"检测完成: {result.session_id}")
    
    if result.corrosion_detections:
        print("\\n🔍 腐蚀检测结果:")
        for i, detection in enumerate(result.corrosion_detections, 1):
            print(f"  {i}. 腐蚀ID: {detection.detection_id}")
            print(f"     类型: {detection.corrosion_type}")
            print(f"     面积: {detection.corrosion_area:.2f} 平方毫米")
            print(f"     深度: {detection.corrosion_depth:.2f} 毫米")
            print(f"     置信度: {detection.confidence:.2f}")
    
    if result.risk_assessment:
        print("\\n⚠️  风险评估:")
        print(f"   等级: {result.risk_assessment.corrosion_level.value}")
        print(f"   评分: {result.risk_assessment.risk_score:.2f}")
        print(f"   紧急程度: {result.risk_assessment.urgency}")
        
        print("\\n💡 建议措施:")
        for rec in result.risk_assessment.recommendations:
            print(f"   - {rec}")
    
    return result


def example_sync_inspection():
    """同步检测示例"""
    print("=" * 50)
    print("同步模式腐蚀检测示例")
    print("=" * 50)
    
    # 创建Agent实例
    agent = CorrosionDetectionAgent()
    
    # 运行同步检测
    result = agent.run_inspection_sync(
        platform_id="PLATFORM_003",
        inspection_area="储罐区域C"
    )
    
    print(f"同步检测完成: {result.session_id}")
    
    if result.errors:
        print(f"错误: {result.errors}")
    
    if result.warnings:
        print(f"警告: {result.warnings}")
    
    return result


async def run_all_examples():
    """运行所有示例"""
    print("🚀 开始运行腐蚀检测Agent示例程序\\n")
    
    try:
        # 示例1: 基础检测
        result1 = await example_basic_inspection()
        print("\\n" + "="*50 + "\\n")
        
        # 示例2: 使用示例数据
        result2 = await example_with_sample_data()
        print("\\n" + "="*50 + "\\n")
        
        # 示例3: 同步模式
        result3 = example_sync_inspection()
        
        print("\\n🎉 所有示例运行完成!")
        print(f"生成的报告:")
        for i, result in enumerate([result1, result2, result3], 1):
            if result.final_report:
                print(f"  {i}. {result.final_report.report_id}.json")
        
    except Exception as e:
        print(f"❌ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    # 确保必要的目录存在
    config.ensure_directories()
    
    # 运行示例
    asyncio.run(run_all_examples())


if __name__ == "__main__":
    main()