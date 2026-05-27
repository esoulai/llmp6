"""
LLMP6 配置类

提供简洁的方式配置每层的模型和参数
"""

import yaml
import json
from typing import Optional, List, Dict, Any


class LLMP6Config:
    """
    LLMP6 配置类
    
    支持两种配置方式：
    1. 通过配置文件（models.yaml, database.json, rules.json）
    2. 通过构造函数参数直接指定
    """
    
    def __init__(
        self,
        core_model: str,
        assign_model: Optional[str] = None,
        filter_model: Optional[List[str]] = None,
        tool_model: Optional[List[str]] = None,
        check_model: Optional[List[str]] = None,
        show_model: Optional[List[str]] = None,
        models_file: str = "models.yaml",
        database_file: Optional[str] = None,
        rules_file: Optional[str] = None,
        **kwargs
    ):
        """
        初始化配置
        
        参数:
            core_model: Core层使用的模型名称（必需）
            assign_model: Assign层使用的模型名称
            filter_model: Filter层使用的模型列表（支持并集/交集）
            tool_model: Tool层使用的模型列表（支持并集/交集）
            check_model: Check层使用的模型列表（支持并集/交集）
            show_model: Show层使用的模型列表（支持并集/交集）
            models_file: 模型配置文件路径
            database_file: 知识库文件路径（用于Filter层）
            rules_file: 规则文件路径（用于Check层）
        """
        self.core_model = core_model
        self.assign_model = assign_model
        self.filter_model = filter_model or []
        self.tool_model = tool_model or []
        self.check_model = check_model or []
        self.show_model = show_model or []
        
        self.models_file = models_file
        self.database_file = database_file
        self.rules_file = rules_file
        
        # 加载模型配置
        self.models = self._load_models(models_file)
        
        # 加载知识库（如果提供）
        self.database = self._load_database(database_file) if database_file else {}
        
        # 加载规则（如果提供）
        self.rules = self._load_rules(rules_file) if rules_file else {}
    
    def _load_models(self, filepath: str) -> Dict[str, Dict]:
        """加载模型配置文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('models', {})
        except Exception as e:
            print(f"警告：无法加载模型配置文件 {filepath}: {e}")
            return {}
    
    def _load_database(self, filepath: str) -> Dict[str, List]:
        """加载知识库文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告：无法加载知识库文件 {filepath}: {e}")
            return {'facts': []}
    
    def _load_rules(self, filepath: str) -> Dict[str, Any]:
        """加载规则文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告：无法加载规则文件 {filepath}: {e}")
            return {'rules': [], 'banned_keywords': []}
    
    def get_model_config(self, model_name: str) -> Optional[Dict]:
        """获取指定模型的配置"""
        return self.models.get(model_name)
    
    def __repr__(self):
        layers = []
        if self.assign_model:
            layers.append(f"Assign: {self.assign_model}")
        layers.append(f"Core: {self.core_model}")
        if self.filter_model:
            layers.append(f"Filter: {self.filter_model}")
        if self.tool_model:
            layers.append(f"Tool: {self.tool_model}")
        if self.check_model:
            layers.append(f"Check: {self.check_model}")
        if self.show_model:
            layers.append(f"Show: {self.show_model}")
        return f"LLMP6Config({', '.join(layers)})"
