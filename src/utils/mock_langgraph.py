"""
LangGraph的简化模拟实现
为了让系统能够独立运行，不依赖外部LangGraph包
"""

from typing import Dict, Any, Callable, Optional, Union
import asyncio

class END:
    """结束标记"""
    pass

class StateGraph:
    """状态图的简化实现"""
    
    def __init__(self, state_class):
        self.state_class = state_class
        self.nodes = {}
        self.edges = {}
        self.conditional_edges = {}
        self.entry_point = None
    
    def add_node(self, name: str, func: Callable):
        """添加节点"""
        self.nodes[name] = func
    
    def set_entry_point(self, name: str):
        """设置入口点"""
        self.entry_point = name
    
    def add_edge(self, from_node: str, to_node: str):
        """添加边"""
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)
    
    def add_conditional_edges(self, from_node: str, condition_func: Callable, mapping: Dict[str, str]):
        """添加条件边"""
        self.conditional_edges[from_node] = (condition_func, mapping)
    
    def compile(self):
        """编译图"""
        return CompiledGraph(self)

class CompiledGraph:
    """编译后的图"""
    
    def __init__(self, graph: StateGraph):
        self.graph = graph
    
    def invoke(self, initial_state):
        """同步执行图"""
        print(f"Mock LangGraph invoke 被调用，初始状态类型: {type(initial_state)}")
        state = initial_state
        current_node = self.graph.entry_point
        
        max_iterations = 20  # 防止无限循环
        iteration = 0
        
        while current_node != END and current_node is not None and iteration < max_iterations:
            iteration += 1
            
            # 执行当前节点
            if current_node in self.graph.nodes:
                node_func = self.graph.nodes[current_node]
                print(f"执行节点: {current_node}, 输入类型: {type(state)}")
                
                try:
                    result = node_func(state)
                    print(f"节点 {current_node} 返回类型: {type(result)}")
                    
                    # 确保返回的是正确的状态对象类型
                    if isinstance(result, self.graph.state_class):
                        state = result
                        print(f"OK 节点 {current_node} 正常返回 AgentState 对象")
                    elif isinstance(result, dict):
                        # 如果返回字典，尝试转换为状态对象
                        print(f"WARNING 警告: 节点 {current_node} 返回了字典，尝试重建状态对象")
                        try:
                            # 尝试使用字典创建新的状态对象
                            state = self.graph.state_class(**result)
                            print(f"OK 成功重建了 AgentState 对象")
                        except Exception as rebuild_error:
                            print(f"ERROR 无法重建状态对象: {rebuild_error}")
                            # 更新现有状态对象的字段
                            for key, value in result.items():
                                if hasattr(state, key):
                                    setattr(state, key, value)
                            print(f"OK 使用字典更新了现有状态对象")
                    else:
                        print(f"ERROR 错误: 节点 {current_node} 返回了不正确的类型: {type(result)}")
                        # 保持原状态不变
                except Exception as e:
                    print(f"ERROR 节点执行失败 {current_node}: {e}")
                    # 确保 state 有 errors 属性
                    if hasattr(state, 'errors'):
                        state.errors.append(f"节点 {current_node} 执行失败: {str(e)}")
                    else:
                        print(f"WARNING 警告: 状态对象没有 errors 属性")
            
            # 确定下一个节点
            next_node = self._get_next_node(current_node, state)
            current_node = next_node
        
        return state
    
    async def ainvoke(self, initial_state):
        """异步执行图"""
        # 简化实现：直接调用同步版本
        return self.invoke(initial_state)
    
    def _get_next_node(self, current_node: str, state) -> Union[str, None]:
        """获取下一个节点"""
        # 检查条件边
        if current_node in self.graph.conditional_edges:
            condition_func, mapping = self.graph.conditional_edges[current_node]
            condition_result = condition_func(state)
            if condition_result in mapping:
                next_node = mapping[condition_result]
                return next_node if next_node != END else None
        
        # 检查普通边
        if current_node in self.graph.edges:
            edges = self.graph.edges[current_node]
            if edges:
                next_node = edges[0]  # 取第一个边
                return next_node if next_node != END else None
        
        return None