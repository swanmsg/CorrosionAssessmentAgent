"""
图像处理工具模块
提供图像预处理、增强和特征提取功能
"""

import cv2
import numpy as np
from typing import Tuple, List
from scipy import ndimage

class ImageProcessor:
    """图像处理器"""
    
    def __init__(self):
        self.target_size = (640, 480)
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """图像预处理"""
        # 调整图像尺寸
        processed = cv2.resize(image, self.target_size)
        
        # 去噪
        processed = cv2.medianBlur(processed, 3)
        
        # 增强对比度
        processed = self._enhance_contrast(processed)
        
        # 锐化
        processed = self._sharpen_image(processed)
        
        return processed
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """增强对比度"""
        # 使用CLAHE（自适应直方图均衡化）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        if len(image.shape) == 3:
            # 彩色图像：转换到LAB空间，只处理L通道
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            # 灰度图像
            return clahe.apply(image)
    
    def _sharpen_image(self, image: np.ndarray) -> np.ndarray:
        """图像锐化"""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1], 
                          [-1, -1, -1]])
        
        if len(image.shape) == 3:
            # 对每个通道单独处理
            sharpened = np.zeros_like(image)
            for i in range(3):
                sharpened[:, :, i] = cv2.filter2D(image[:, :, i], -1, kernel)
            return sharpened
        else:
            return cv2.filter2D(image, -1, kernel)
    
    def detect_corrosion_features(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """检测腐蚀特征（简化版本）"""
        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 定义铁锈颜色范围（橙红色）
        lower_rust = np.array([5, 50, 50])
        upper_rust = np.array([25, 255, 255])
        
        # 创建掩码
        mask = cv2.inRange(hsv, lower_rust, upper_rust)
        
        # 形态学操作去除噪声
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 提取边界框
        bounding_boxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # 过滤掉太小的区域
                x, y, w, h = cv2.boundingRect(contour)
                bounding_boxes.append((x, y, w, h))
        
        return bounding_boxes
    
    def calculate_corrosion_area(self, image: np.ndarray, bounding_boxes: List[Tuple[int, int, int, int]]) -> float:
        """计算腐蚀面积"""
        total_area = 0
        for x, y, w, h in bounding_boxes:
            # 简化计算：使用边界框面积
            total_area += w * h
        
        # 转换为实际面积（假设像素到毫米的转换比例）
        pixel_to_mm_ratio = 0.1  # 1像素 = 0.1mm
        actual_area = total_area * (pixel_to_mm_ratio ** 2)
        
        return actual_area
    
    def estimate_corrosion_depth(self, image: np.ndarray, bounding_boxes: List[Tuple[int, int, int, int]]) -> float:
        """估算腐蚀深度（基于图像特征）"""
        if not bounding_boxes:
            return 0.0
        
        # 转换为灰度图像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        depth_estimates = []
        
        for x, y, w, h in bounding_boxes:
            # 提取腐蚀区域
            roi = gray[y:y+h, x:x+w]
            
            # 计算强度变化（深度特征）
            mean_intensity = np.mean(roi)
            std_intensity = np.std(roi)
            
            # 使用启发式方法估算深度
            # 较暗且变化较大的区域通常表示更深的腐蚀
            depth_factor = (255 - mean_intensity) / 255.0
            variation_factor = std_intensity / 128.0
            
            estimated_depth = depth_factor * variation_factor * 2.0  # 最大2mm
            depth_estimates.append(estimated_depth)
        
        return max(depth_estimates) if depth_estimates else 0.0
    
    def visualize_detections(self, image: np.ndarray, bounding_boxes: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """可视化检测结果"""
        result = image.copy()
        
        for i, (x, y, w, h) in enumerate(bounding_boxes):
            # 绘制边界框
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 添加标签
            label = f"Corrosion {i+1}"
            cv2.putText(result, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return result