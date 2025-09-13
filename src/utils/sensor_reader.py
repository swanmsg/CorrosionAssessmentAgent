"""
传感器数据读取工具模块
处理各种传感器数据的读取和解析
"""

import json
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from ..models import SensorData, SensorType

class SensorReader:
    """传感器数据读取器"""
    
    def __init__(self):
        self.supported_formats = ['.json', '.csv', '.txt']
    
    def read_sensor_file(self, file_path: str) -> List[SensorData]:
        """读取传感器数据文件"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"传感器数据文件不存在: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.json':
            return self._read_json_file(file_path)
        elif file_extension == '.csv':
            return self._read_csv_file(file_path)
        elif file_extension == '.txt':
            return self._read_txt_file(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
    
    def _read_json_file(self, file_path: Path) -> List[SensorData]:
        """读取JSON格式的传感器数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sensor_readings = []
        
        if isinstance(data, list):
            for item in data:
                sensor_data = self._parse_sensor_item(item)
                if sensor_data:
                    sensor_readings.append(sensor_data)
        elif isinstance(data, dict):
            sensor_data = self._parse_sensor_item(data)
            if sensor_data:
                sensor_readings.append(sensor_data)
        
        return sensor_readings
    
    def _read_csv_file(self, file_path: Path) -> List[SensorData]:
        """读取CSV格式的传感器数据"""
        df = pd.read_csv(file_path)
        sensor_readings = []
        
        for _, row in df.iterrows():
            sensor_data = self._parse_sensor_row(row.to_dict())
            if sensor_data:
                sensor_readings.append(sensor_data)
        
        return sensor_readings
    
    def _read_txt_file(self, file_path: Path) -> List[SensorData]:
        """读取文本格式的传感器数据"""
        sensor_readings = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # 跳过空行和注释
                    sensor_data = self._parse_sensor_line(line)
                    if sensor_data:
                        sensor_readings.append(sensor_data)
        
        return sensor_readings
    
    def _parse_sensor_item(self, item: Dict[str, Any]) -> SensorData:
        """解析单个传感器数据项"""
        try:
            # 处理时间戳
            timestamp_str = item.get('timestamp', datetime.now().isoformat())
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.now()
            
            # 处理传感器类型
            sensor_type_str = item.get('sensor_type', 'thickness').lower()
            try:
                sensor_type = SensorType(sensor_type_str)
            except ValueError:
                sensor_type = SensorType.THICKNESS  # 默认类型
            
            # 处理位置信息
            location = item.get('location', {"x": 0, "y": 0, "z": 0})
            if not isinstance(location, dict):
                location = {"x": 0, "y": 0, "z": 0}
            
            sensor_data = SensorData(
                sensor_id=item.get('sensor_id', f'sensor_{datetime.now().timestamp()}'),
                sensor_type=sensor_type,
                value=float(item.get('value', 0.0)),
                unit=item.get('unit', ''),
                timestamp=timestamp,
                location=location,
                quality=float(item.get('quality', 1.0))
            )
            
            return sensor_data
            
        except Exception as e:
            print(f"解析传感器数据失败: {e}")
            return None
    
    def _parse_sensor_row(self, row: Dict[str, Any]) -> SensorData:
        """解析CSV行数据"""
        return self._parse_sensor_item(row)
    
    def _parse_sensor_line(self, line: str) -> SensorData:
        """解析文本行数据"""
        # 假设格式: sensor_id,sensor_type,value,unit,timestamp,x,y,z,quality
        parts = line.split(',')
        
        if len(parts) < 5:
            return None
        
        try:
            item = {
                'sensor_id': parts[0].strip(),
                'sensor_type': parts[1].strip(),
                'value': parts[2].strip(),
                'unit': parts[3].strip(),
                'timestamp': parts[4].strip(),
                'location': {
                    'x': float(parts[5]) if len(parts) > 5 else 0.0,
                    'y': float(parts[6]) if len(parts) > 6 else 0.0,
                    'z': float(parts[7]) if len(parts) > 7 else 0.0
                },
                'quality': float(parts[8]) if len(parts) > 8 else 1.0
            }
            
            return self._parse_sensor_item(item)
            
        except Exception as e:
            print(f"解析文本行失败: {e}")
            return None
    
    def validate_sensor_data(self, sensor_data: SensorData) -> bool:
        """验证传感器数据有效性"""
        # 检查数值范围
        if sensor_data.sensor_type == SensorType.THICKNESS:
            if sensor_data.value < 0 or sensor_data.value > 50:  # 厚度范围0-50mm
                return False
        elif sensor_data.sensor_type == SensorType.TEMPERATURE:
            if sensor_data.value < -50 or sensor_data.value > 100:  # 温度范围-50到100°C
                return False
        elif sensor_data.sensor_type == SensorType.HUMIDITY:
            if sensor_data.value < 0 or sensor_data.value > 100:  # 湿度0-100%
                return False
        elif sensor_data.sensor_type == SensorType.PH:
            if sensor_data.value < 0 or sensor_data.value > 14:  # pH 0-14
                return False
        
        # 检查质量评分
        if sensor_data.quality < 0 or sensor_data.quality > 1:
            return False
        
        return True
    
    def filter_by_quality(self, sensor_readings: List[SensorData], min_quality: float = 0.7) -> List[SensorData]:
        """根据质量过滤传感器数据"""
        return [reading for reading in sensor_readings if reading.quality >= min_quality]
    
    def filter_by_time_range(self, sensor_readings: List[SensorData], 
                           start_time: datetime, end_time: datetime) -> List[SensorData]:
        """根据时间范围过滤传感器数据"""
        return [reading for reading in sensor_readings 
                if start_time <= reading.timestamp <= end_time]
    
    def get_readings_by_type(self, sensor_readings: List[SensorData], 
                           sensor_type: SensorType) -> List[SensorData]:
        """按传感器类型过滤数据"""
        return [reading for reading in sensor_readings if reading.sensor_type == sensor_type]