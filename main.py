#!/usr/bin/env python3
"""
海上石油平台腐蚀检测Agent主程序
基于LangGraph的智能腐蚀检测系统
"""

import asyncio
import argparse
from pathlib import Path
from typing import List, Optional

from src.agents.corrosion_agent import CorrosionDetectionAgent
from src.config import config


def setup_logging():
    """设置日志"""
    from loguru import logger
    import sys
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.log_level
    )
    
    # 添加文件输出
    logger.add(
        config.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=config.log_level,
        rotation="10 MB",
        retention="30 days"
    )
    
    return logger


async def run_inspection_async(platform_id: str, 
                             area: str, 
                             image_files: Optional[List[str]] = None,
                             sensor_files: Optional[List[str]] = None):
    """异步运行检测流程"""
    logger = setup_logging()
    
    logger.info(f"开始腐蚀检测: 平台={platform_id}, 区域={area}")
    
    # 创建Agent实例
    agent = CorrosionDetectionAgent()
    
    try:
        # 运行检测流程
        result = await agent.run_inspection(
            platform_id=platform_id,
            inspection_area=area,
            image_files=image_files or [],
            sensor_files=sensor_files or []
        )
        
        # 输出结果摘要
        logger.info("检测完成!")
        
        if result.final_report:
            logger.info(f"报告ID: {result.final_report.report_id}")
            logger.info(f"风险等级: {result.risk_assessment.corrosion_level.value if result.risk_assessment else 'N/A'}")
            logger.info(f"检测的腐蚀点数量: {len(result.corrosion_detections)}")
            
            if result.corrosion_detections:
                total_area = sum(d.corrosion_area for d in result.corrosion_detections)
                max_depth = max(d.corrosion_depth for d in result.corrosion_detections)
                logger.info(f"总腐蚀面积: {total_area:.2f} 平方毫米")
                logger.info(f"最大腐蚀深度: {max_depth:.2f} 毫米")
        
        if result.errors:
            logger.error(f"检测过程中发现错误: {result.errors}")
        
        if result.warnings:
            logger.warning(f"检测过程中的警告: {result.warnings}")
        
        return result
        
    except Exception as e:
        logger.error(f"检测流程失败: {e}")
        raise


def run_inspection_sync(platform_id: str, 
                       area: str, 
                       image_files: Optional[List[str]] = None,
                       sensor_files: Optional[List[str]] = None):
    """同步运行检测流程"""
    logger = setup_logging()
    
    logger.info(f"开始腐蚀检测: 平台={platform_id}, 区域={area}")
    
    # 创建Agent实例
    agent = CorrosionDetectionAgent()
    
    try:
        # 运行检测流程
        result = agent.run_inspection_sync(
            platform_id=platform_id,
            inspection_area=area,
            image_files=image_files or [],
            sensor_files=sensor_files or []
        )
        
        # 输出结果摘要
        logger.info("检测完成!")
        
        if result.final_report:
            logger.info(f"报告ID: {result.final_report.report_id}")
            logger.info(f"风险等级: {result.risk_assessment.corrosion_level.value if result.risk_assessment else 'N/A'}")
            logger.info(f"检测的腐蚀点数量: {len(result.corrosion_detections)}")
            
            if result.corrosion_detections:
                total_area = sum(d.corrosion_area for d in result.corrosion_detections)
                max_depth = max(d.corrosion_depth for d in result.corrosion_detections)
                logger.info(f"总腐蚀面积: {total_area:.2f} 平方毫米")
                logger.info(f"最大腐蚀深度: {max_depth:.2f} 毫米")
        
        if result.errors:
            logger.error(f"检测过程中发现错误: {result.errors}")
        
        if result.warnings:
            logger.warning(f"检测过程中的警告: {result.warnings}")
        
        return result
        
    except Exception as e:
        logger.error(f"检测流程失败: {e}")
        raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="海上石油平台腐蚀检测Agent")
    
    parser.add_argument("--platform-id", "-p", required=True, help="石油平台ID")
    parser.add_argument("--area", "-a", required=True, help="检测区域")
    parser.add_argument("--images", "-i", nargs="*", help="图像文件路径列表")
    parser.add_argument("--sensors", "-s", nargs="*", help="传感器数据文件路径列表")
    parser.add_argument("--async-mode", "-A", action="store_true", help="使用异步模式运行")
    
    args = parser.parse_args()
    
    # 验证文件路径
    image_files = []
    if args.images:
        for img_path in args.images:
            if Path(img_path).exists():
                image_files.append(img_path)
            else:
                print(f"警告: 图像文件不存在: {img_path}")
    
    sensor_files = []
    if args.sensors:
        for sensor_path in args.sensors:
            if Path(sensor_path).exists():
                sensor_files.append(sensor_path)
            else:
                print(f"警告: 传感器文件不存在: {sensor_path}")
    
    try:
        if args.async_mode:
            # 异步模式
            result = asyncio.run(run_inspection_async(
                platform_id=args.platform_id,
                area=args.area,
                image_files=image_files,
                sensor_files=sensor_files
            ))
        else:
            # 同步模式
            result = run_inspection_sync(
                platform_id=args.platform_id,
                area=args.area,
                image_files=image_files,
                sensor_files=sensor_files
            )
        
        print(f"\n✅ 检测完成! 会话ID: {result.session_id}")
        
        if result.final_report:
            print(f"📊 报告已保存到: outputs/reports/{result.final_report.report_id}.json")
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断检测流程")
    except Exception as e:
        print(f"\n❌ 检测失败: {e}")
        return 1
    
    return 0


def demo():
    """演示模式 - 使用示例数据运行"""
    print("🚀 运行演示模式...")
    
    try:
        result = run_inspection_sync(
            platform_id="PLATFORM_001",
            area="甲板区域A",
            image_files=[],  # 将自动生成示例图像
            sensor_files=[]  # 将自动生成示例传感器数据
        )
        
        print(f"\n✅ 演示完成! 会话ID: {result.session_id}")
        
        if result.final_report:
            print(f"📊 报告已保存到: outputs/reports/{result.final_report.report_id}.json")
            print(f"🎯 风险等级: {result.risk_assessment.corrosion_level.value if result.risk_assessment else 'N/A'}")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    
    # 检查是否是演示模式
    if len(sys.argv) == 2 and sys.argv[1] == "demo":
        sys.exit(demo())
    else:
        sys.exit(main())