"""
LLMP6 核心管道实现

实现六层架构的完整执行逻辑：
Assign -> Core -> Filter -> Tool -> Check -> Show
"""

import requests
import json
import concurrent.futures
from typing import Optional, Dict, Any, List
from .config import LLMP6Config


class LLMP6Pipeline:
    """
    LLMP6 管道类
    
    实现六层架构的完整执行流程，支持并集和交集执行模式。
    """
    
    def __init__(self, config: LLMP6Config):
        """
        初始化管道
        
        参数:
            config: LLMP6Config 配置实例
        """
        self.config = config
    
    def _call_api(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """
        调用单个模型 API
        
        参数:
            model_name: 模型名称
            prompt: 提示语
        
        返回:
            包含输出和耗时的字典
        """
        model_config = self.config.get_model_config(model_name)
        if not model_config:
            return {"output": prompt, "time": 0.0, "model": model_name}
        
        url = model_config['url']
        headers = {
            "Content-Type": "application/json"
        }
        
        if 'key' in model_config:
            headers["Authorization"] = f"Bearer {model_config['key']}"
        
        payload = {
            "model": model_config['model'],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        try:
            import time
            start_time = time.time()
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            elapsed_time = time.time() - start_time
            
            result = response.json()
            output = result['choices'][0]['message']['content']
            
            return {
                "output": output.strip(),
                "time": round(elapsed_time, 2),
                "model": model_name,
                "success": True
            }
        except Exception as e:
            return {
                "output": prompt,
                "time": 0.0,
                "model": model_name,
                "success": False,
                "error": str(e)
            }
    
    def _execute_union(self, models: List[str], prompt: str) -> Dict[str, Any]:
        """
        并集执行模式：多个模型并行执行，结果合并
        
        参数:
            models: 模型列表
            prompt: 提示语
        
        返回:
            合并后的结果
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(models)) as executor:
            futures = [executor.submit(self._call_api, model, prompt) for model in models]
            
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        # 合并结果
        outputs = [r['output'] for r in results if r.get('success', True)]
        total_time = max(r['time'] for r in results)
        
        return {
            "output": "\n\n".join(outputs),
            "time": total_time,
            "models": models,
            "execution_mode": "union"
        }
    
    def _execute_intersection(self, models: List[str], prompt: str) -> Dict[str, Any]:
        """
        交集执行模式：多个模型串行执行，前一个输出作为后一个输入
        
        参数:
            models: 模型列表
            prompt: 提示语
        
        返回:
            最终结果
        """
        content = prompt
        total_time = 0.0
        
        for model in models:
            result = self._call_api(model, content)
            content = result['output']
            total_time += result['time']
        
        return {
            "output": content,
            "time": total_time,
            "models": models,
            "execution_mode": "intersection"
        }
    
    def _execute_layer(self, model_spec: List[str], prompt: str, layer_name: str) -> Dict[str, Any]:
        """
        执行单个层级
        
        参数:
            model_spec: 模型规格（支持并集/交集）
            prompt: 提示语
            layer_name: 层级名称
        
        返回:
            执行结果
        """
        if not model_spec:
            return {"output": prompt, "time": 0.0, "models": [], "execution_mode": "none"}
        
        if len(model_spec) == 1:
            # 单个模型执行
            result = self._call_api(model_spec[0], prompt)
            return {
                "output": result['output'],
                "time": result['time'],
                "models": model_spec,
                "execution_mode": "single"
            }
        elif len(model_spec) > 1:
            # 检查是否为并集模式（模型名称包含特殊标记）
            # 默认使用并集模式执行
            return self._execute_union(model_spec, prompt)
    
    def run(self, user_input: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        执行完整的 LLMP6 管道
        
        参数:
            user_input: 用户输入
            max_retries: Check失败时的最大重试次数
        
        返回:
            包含各层结果的字典
        """
        results = {
            "input": user_input,
            "layers": {},
            "total_time": 0.0,
            "final_output": user_input
        }
        
        content = user_input
        retry_count = 0
        
        while retry_count < max_retries:
            # 1. Assign层：解析用户意图
            if self.config.assign_model:
                assign_prompt = f"解析用户意图并生成合适的提示语：\n{content}"
                assign_result = self._execute_layer([self.config.assign_model], assign_prompt, "Assign")
                results["layers"]["Assign"] = assign_result
                content = assign_result["output"]
                results["total_time"] += assign_result["time"]
            
            # 2. Core层：生成初始内容
            core_result = self._execute_layer([self.config.core_model], content, "Core")
            results["layers"]["Core"] = core_result
            content = core_result["output"]
            results["total_time"] += core_result["time"]
            
            # 3. Filter层：事实核查
            if self.config.filter_model:
                facts = self.config.database.get('facts', [])
                facts_str = "\n".join([f"- {fact}" for fact in facts]) if facts else "无"
                filter_prompt = f"""基于以下事实库进行事实核查：
事实库：
{facts_str}

请检查并修正以下内容中的错误信息：
{content}"""
                filter_result = self._execute_layer(self.config.filter_model, filter_prompt, "Filter")
                results["layers"]["Filter"] = filter_result
                content = filter_result["output"]
                results["total_time"] += filter_result["time"]
            
            # 4. Tool层：工具调用（可选）
            if self.config.tool_model:
                tool_prompt = f"""分析以下内容，判断是否需要调用工具：
{content}

如果需要调用工具，请提供工具调用参数；否则直接返回原文。"""
                tool_result = self._execute_layer(self.config.tool_model, tool_prompt, "Tool")
                results["layers"]["Tool"] = tool_result
                content = tool_result["output"]
                results["total_time"] += tool_result["time"]
            
            # 5. Check层：合规检查
            check_passed = True
            if self.config.check_model:
                rules = self.config.rules.get('rules', [])
                banned_keywords = self.config.rules.get('banned_keywords', [])
                
                rules_str = "\n".join([f"- {rule}" for rule in rules]) if rules else "无"
                keywords_str = "、".join(banned_keywords) if banned_keywords else "无"
                
                check_prompt = f"""请检查以下内容是否符合规则：

规则列表：
{rules_str}

禁止关键词：
{keywords_str}

待检查内容：
{content}

请输出检查结果：通过或不通过，并说明原因。"""
                
                check_result = self._execute_layer(self.config.check_model, check_prompt, "Check")
                results["layers"]["Check"] = check_result
                results["total_time"] += check_result["time"]
                
                # 判断是否通过
                check_output = check_result["output"]
                if "不通过" in check_output or "不合规" in check_output or "违规" in check_output:
                    check_passed = False
                    retry_count += 1
                    print(f"Check层未通过，重试第 {retry_count} 次...")
                    continue
            
            # 6. Show层：格式转换
            if self.config.show_model:
                show_prompt = f"""请优化以下内容的格式和语气，使其更友好：
{content}"""
                show_result = self._execute_layer(self.config.show_model, show_prompt, "Show")
                results["layers"]["Show"] = show_result
                content = show_result["output"]
                results["total_time"] += show_result["time"]
            
            # 检查通过，退出循环
            break
        
        results["final_output"] = content
        results["retry_count"] = retry_count
        
        return results
    
    def __repr__(self):
        return f"LLMP6Pipeline({repr(self.config)})"
