# 快速开始指南

## 安装

### 1. 克隆项目

```bash
git clone <repository_url>
cd CorrosionAssessment_Agent
```

### 2. 创建虚拟环境

```bash
# 使用conda
conda create -n corrosion-agent python=3.8
conda activate corrosion-agent

# 或使用venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑配置文件
nano .env
```

必需的配置项：
```bash
# 如果使用AI模型分析（可选）
OPENAI_API_KEY=your_openai_api_key_here

# 数据和输出路径
DATA_ROOT_PATH=data/
OUTPUT_PATH=outputs/

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/corrosion_agent.log
```

## 运行示例

### 方法1: 使用主程序（演示模式）

```bash
python main.py demo
```

这将运行一个完整的演示，包括：
- 自动生成示例传感器数据
- 创建模拟腐蚀图像
- 执行完整的检测流程
- 生成检测报告

### 方法2: 使用自定义参数

```bash
# 基础检测
python main.py --platform-id PLATFORM_001 --area "甲板区域A"

# 使用图像文件
python main.py --platform-id PLATFORM_002 --area "管道区域B" --images image1.jpg image2.jpg

# 使用传感器数据
python main.py --platform-id PLATFORM_003 --area "储罐区域C" --sensors sensor_data.json

# 异步模式
python main.py --platform-id PLATFORM_004 --area "测试区域" --async-mode
```

### 方法3: 运行示例程序

```bash
python examples/demo.py
```

这会运行多个示例场景：
- 基础检测示例
- 使用示例数据的检测
- 同步模式检测

## 输出结果

运行完成后，您可以在以下位置找到结果：

### 1. 检测报告
```
outputs/reports/report_<session_id>.json
```

包含完整的检测报告，包括：
- 传感器数据
- 图像分析结果
- 腐蚀检测详情
- 风险评估
- 维护建议

### 2. 处理后的图像
```
outputs/processed_images/
outputs/sample_images/     # 示例图像
```

### 3. 日志文件
```
logs/corrosion_agent.log
```

## 编程接口使用

### 基础用法

```python
from src.agents.corrosion_agent import CorrosionDetectionAgent

# 创建Agent
agent = CorrosionDetectionAgent()

# 同步执行检测
result = agent.run_inspection_sync(
    platform_id="MY_PLATFORM",
    inspection_area="甲板区域"
)

# 检查结果
print(f"会话ID: {result.session_id}")
if result.risk_assessment:
    print(f"风险等级: {result.risk_assessment.corrosion_level.value}")
    print(f"风险评分: {result.risk_assessment.risk_score:.2f}")

print(f"发现腐蚀点: {len(result.corrosion_detections)}")
```

### 异步用法

```python
import asyncio
from src.agents.corrosion_agent import CorrosionDetectionAgent

async def async_inspection():
    agent = CorrosionDetectionAgent()
    
    result = await agent.run_inspection(
        platform_id="MY_PLATFORM",
        inspection_area="甲板区域"
    )
    
    return result

# 运行异步检测
result = asyncio.run(async_inspection())
```

### 使用自定义数据

```python
# 准备传感器数据文件 (JSON格式)
sensor_data = [
    {
        "sensor_id": "thickness_001",
        "sensor_type": "thickness",
        "value": 10.5,
        "unit": "mm",
        "timestamp": "2024-01-15T10:30:00",
        "location": {"x": 0, "y": 0, "z": 0},
        "quality": 0.95
    }
]

import json
with open("my_sensors.json", "w") as f:
    json.dump(sensor_data, f)

# 运行检测
result = agent.run_inspection_sync(
    platform_id="CUSTOM_PLATFORM",
    inspection_area="自定义区域",
    sensor_files=["my_sensors.json"],
    image_files=["corrosion_photo.jpg"]
)
```

## 测试

### 运行测试套件

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_corrosion_agent.py::TestCorrosionDetectionAgent::test_basic_inspection_flow -v
```

### 单独测试组件

```python
# 测试数据收集
from src.agents.nodes import DataCollectionNode
from src.models import AgentState
from datetime import datetime

node = DataCollectionNode()
state = AgentState(
    session_id="test",
    current_step="test",
    platform_id="TEST",
    inspection_area="测试区域",
    start_time=datetime.now(),
    last_update=datetime.now()
)

result = node.execute(state)
print(f"收集到传感器数据: {len(result.sensor_readings)}")
print(f"处理图像数量: {len(result.processed_images)}")
```

## 常见问题解决

### 1. 导入错误

**问题**: `ModuleNotFoundError: No module named 'src'`

**解决**: 确保在项目根目录下运行，或添加Python路径：
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
```

### 2. 依赖缺失

**问题**: `ImportError: cannot import name 'BaseSettings'`

**解决**: 更新pydantic设置：
```bash
pip install pydantic-settings>=2.0.0
```

### 3. 权限问题

**问题**: `PermissionError: [Errno 13] Permission denied`

**解决**: 确保输出目录有写权限：
```bash
chmod 755 outputs/
mkdir -p outputs/reports outputs/processed_images logs
```

### 4. 内存不足

**问题**: 处理大量图像时内存不足

**解决**: 
- 减少并发处理的图像数量
- 降低图像分辨率
- 增加虚拟内存

### 5. 配置问题

**问题**: 配置文件未加载

**解决**: 
- 确保`.env`文件在项目根目录
- 检查环境变量格式
- 使用绝对路径

## 下一步

1. **了解系统架构**: 阅读[API文档](docs/API.md)了解详细的系统设计
2. **自定义配置**: 根据您的需求修改配置参数
3. **集成到现有系统**: 参考编程接口文档集成到您的应用中
4. **扩展功能**: 添加新的传感器类型或分析算法
5. **生产部署**: 配置日志、监控和错误处理

## 获取帮助

- 查看[API文档](docs/API.md)获取详细的技术信息
- 查看[示例代码](examples/)了解更多使用场景  
- 检查[测试用例](tests/)了解预期行为
- 提交Issue报告问题或建议改进