#!/usr/bin/env python3
"""
LLMP6完整架构测试：使用当前已安装的Ollama模型

层级模型配置：
- Assign层: llama3.2:3b (意图理解+任务分配)
- Tool层: sam860/lucy:1.7b (搜索工具)
- Filter层: bespoke-minicheck (事实核查)
- Check层: llama-guard3:1b (合规检查)
- Show层: OmniNode/Orion:V1.3 (格式转换)
"""

import os
import sys
import json
import time
import statistics
import urllib.request
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_DIR = os.path.join(PROJECT_ROOT, "experiments", "data")
RESULTS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "results")

CORE_MODELS_CONFIG = {
    "deepseek": {
        "name": "DeepSeek",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",
        "key": "sk-3c8574a2644f4da694bfc9a5204447df"
    },
    "qwen": {
        "name": "Qwen",
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "model": "qwen-plus",
        "key": "sk-c29356c31edb4bdbaff14173a5d8ab05"
    },
    "kimi": {
        "name": "Kimi",
        "url": "https://api.moonshot.cn/v1/chat/completions",
        "model": "moonshot-v1-8k",
        "key": "sk-pOecxHPn4uA2k5zcyjnWMV2rPfd7eZNLTValGhkDH6QZR73f"
    }
}

OLLAMA_LAYERS = {
    "assign": {
        "name": "Assign层-意图理解",
        "model": "llama3.2:3b",
        "prompt_template": "请分析以下用户输入的意图，并生成适合大语言模型的提示语：\n\n用户输入：{content}\n\n意图分析：\n生成的提示语："
    },
    "tool": {
        "name": "Tool层-工具调用",
        "model": "sam860/lucy:1.7b",
        "prompt_template": "请分析以下内容是否需要调用工具（如计算器、搜索、代码执行等），并决定使用哪个工具：\n\n内容：{content}\n\n工具选择："
    },
    "filter": {
        "name": "Filter层-事实核查",
        "model": "bespoke-minicheck",
        "prompt_template": "请核查以下内容的事实准确性，如发现错误请修正：\n\n待核查内容：{content}\n\n核查结果："
    },
    "check": {
        "name": "Check层-合规检查",
        "model": "llama-guard3:1b",
        "prompt_template": "请检查以下内容是否符合安全合规要求：\n\n内容：{content}\n\n检查结果："
    },
    "show": {
        "name": "Show层-格式转换",
        "model": "OmniNode/Orion:V1.3",
        "prompt_template": "请将以下内容转换为流畅自然的中文回复格式：\n\n原始内容：{content}\n\n转换后的内容："
    }
}

OLLAMA_URL = "http://localhost:11434/api/chat"

def load_test_data(grouped=False):
    """加载测试数据，支持分组模式"""
    if grouped:
        # 加载分组数据
        grouped_path = os.path.join(DATA_DIR, "csqa2_experiment_data_grouped.json")
        if os.path.exists(grouped_path):
            with open(grouped_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    # 默认加载原始数据
    csqa2_path = os.path.join(DATA_DIR, "csqa2_experiment_data.json")
    if os.path.exists(csqa2_path):
        with open(csqa2_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    questions = [
        "中国的首都是哪里？",
        "水的化学式是什么？",
        "地球围绕太阳公转一周需要多长时间？",
        "人类首次登月是在哪一年？",
        "什么是光合作用？",
        "牛顿三大定律是什么？",
        "互联网是谁发明的？",
        "DNA的全称是什么？",
        "世界上最高的山峰是哪座？",
        "什么是人工智能？"
    ]
    return [{"id": i+1, "question": q, "reference_answer": ""} for i, q in enumerate(questions)]

def call_cloud_api(model_key, prompt, timeout=180):
    """调用云API，增加超时时间以支持批量请求"""
    model_config = CORE_MODELS_CONFIG[model_key]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {model_config['key']}"
    }
    payload = {
        "model": model_config["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    start_time = time.time()
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(model_config["url"], data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_time = (time.time() - start_time) * 1000
            result = json.loads(response.read().decode('utf-8'))
            output = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"success": True, "response_time": response_time, "output": output}
    except Exception as e:
        return {"success": False, "response_time": (time.time() - start_time) * 1000, "error": str(e)}

def call_cloud_api_batch(model_key, prompts, timeout=120):
    """批量调用云API，将多条问答打包成一个请求"""
    model_config = CORE_MODELS_CONFIG[model_key]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {model_config['key']}"
    }
    
    # 将多条问答打包成一个请求
    batch_content = "\n\n".join([f"问题{i+1}：{prompt}" for i, prompt in enumerate(prompts)])
    batch_content += "\n\n请按顺序依次回答以上问题，每个问题的答案用【问题X答案】格式包裹。"
    
    payload = {
        "model": model_config["model"],
        "messages": [{"role": "user", "content": batch_content}],
        "temperature": 0.7
    }

    start_time = time.time()
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(model_config["url"], data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_time = (time.time() - start_time) * 1000
            result = json.loads(response.read().decode('utf-8'))
            output = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 解析批量返回的结果
            responses = []
            for i in range(len(prompts)):
                start_marker = f"【问题{i+1}答案】"
                end_marker = f"【问题{i+2}答案】" if i + 1 < len(prompts) else None
                
                if start_marker in output:
                    start_idx = output.find(start_marker) + len(start_marker)
                    if end_marker:
                        end_idx = output.find(end_marker)
                        if end_idx == -1:
                            end_idx = len(output)
                    else:
                        end_idx = len(output)
                    answer = output[start_idx:end_idx].strip()
                    responses.append({"success": True, "response_time": response_time / len(prompts), "output": answer})
                else:
                    responses.append({"success": False, "response_time": response_time / len(prompts), "error": f"未找到问题{i+1}的答案"})
            
            return responses
    except Exception as e:
        # 如果批量调用失败，返回多个失败结果
        return [{"success": False, "response_time": (time.time() - start_time) * 1000 / len(prompts), "error": str(e)}] * len(prompts)

def call_ollama(model_name, prompt, timeout=60):
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.5
    }

    start_time = time.time()
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(OLLAMA_URL, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_time = (time.time() - start_time) * 1000
            result = json.loads(response.read().decode('utf-8'))
            output = result.get("message", {}).get("content", "")
            return {"success": True, "response_time": response_time, "output": output}
    except Exception as e:
        return {"success": False, "response_time": (time.time() - start_time) * 1000, "error": str(e)}

def evaluate_response(output, prompt, reference_answer=""):
    """评估响应质量的综合指标"""
    quality_score = 0.0

    # 基础分：输出有效性检查
    if len(output.strip()) == 0:
        return 0.0
    if len(output.strip()) >= 20:
        quality_score += 0.2
    if len(output.strip()) >= 50:
        quality_score += 0.1
    if len(output.strip()) >= 100:
        quality_score += 0.1

    # 语言质量评估
    helpful_words = ["可以", "会", "能够", "建议", "请", "帮助", "您", "是", "正确", "答案", "解", "回答"]
    helpful_count = sum(1 for word in helpful_words if word in output)
    quality_score += min(0.2, helpful_count * 0.04)

    # 问题响应完整性
    if "?" in prompt:
        if any(kw in output for kw in ["答", "回答", "解", "是", "答案"]):
            quality_score += 0.1
        
        # 如果有参考答案，进行匹配评估
        if reference_answer:
            ref_tokens = set(reference_answer.lower().strip().split())
            output_tokens = set(output.lower().strip().split())
            if ref_tokens and output_tokens:
                overlap = len(ref_tokens & output_tokens) / len(ref_tokens)
                quality_score += min(0.3, overlap * 0.3)

    # 格式规范检查
    if output.count('。') >= 2 or output.count('！') >= 1:
        quality_score += 0.1

    return max(0.0, min(1.0, quality_score))

def calculate_accuracy(output, prompt, quality_score, reference_answer=""):
    """计算准确率指标 - 基于参考答案匹配"""
    # 基础准确率
    accuracy = 0.3
    
    # 如果有参考答案，进行精确匹配
    if reference_answer and reference_answer.strip():
        ref_tokens = set(reference_answer.lower().strip().split())
        output_tokens = set(output.lower().strip().split())
        
        if ref_tokens:
            # 计算答案匹配度（Jaccard相似度）
            overlap = len(ref_tokens & output_tokens) / len(ref_tokens)
            accuracy = overlap * 0.9  # 匹配度占90%权重
            
            # 完全匹配给予额外奖励
            if overlap >= 0.9:
                accuracy += 0.1
            elif overlap >= 0.7:
                accuracy += 0.05
    else:
        # 无参考答案时，基于输出质量推断
        accuracy = quality_score * 0.8
        
        # 问题类型的额外评估
        if "?" in prompt:
            if len(output) < 20:
                accuracy -= 0.05
            elif len(output) > 80:
                accuracy += 0.05
    
    return max(0.0, min(1.0, accuracy))

def call_core_only(model_key, prompt):
    result = call_cloud_api(model_key, prompt)
    if result["success"]:
        # 不在这里计算指标，只保存原始输出
        result["output"] = result["output"]
    return result

def call_llmp6_full(model_key, prompt):
    total_time = 0
    layer_times = {}

    print("    [Core] 调用基座模型...")
    core_result = call_cloud_api(model_key, prompt)
    if not core_result["success"]:
        return {"success": False, "response_time": core_result["response_time"], "error": core_result.get("error", "Core层失败")}
    total_time += core_result["response_time"]
    layer_times["core"] = core_result["response_time"]
    content = core_result["output"]

    print("    [Assign] 意图理解...")
    assign_prompt = OLLAMA_LAYERS["assign"]["prompt_template"].format(content=prompt)
    assign_result = call_ollama(OLLAMA_LAYERS["assign"]["model"], assign_prompt)
    if assign_result["success"]:
        total_time += assign_result["response_time"]
        layer_times["assign"] = assign_result["response_time"]
        content = assign_result["output"]
    else:
        layer_times["assign"] = 0

    print("    [Filter] 事实核查...")
    filter_prompt = OLLAMA_LAYERS["filter"]["prompt_template"].format(content=content)
    filter_result = call_ollama(OLLAMA_LAYERS["filter"]["model"], filter_prompt)
    if filter_result["success"]:
        total_time += filter_result["response_time"]
        layer_times["filter"] = filter_result["response_time"]
        content = filter_result["output"]
    else:
        layer_times["filter"] = 0

    print("    [Tool] 工具调用...")
    tool_prompt = OLLAMA_LAYERS["tool"]["prompt_template"].format(content=content)
    tool_result = call_ollama(OLLAMA_LAYERS["tool"]["model"], tool_prompt)
    if tool_result["success"]:
        total_time += tool_result["response_time"]
        layer_times["tool"] = tool_result["response_time"]
    else:
        layer_times["tool"] = 0

    print("    [Check] 合规检查...")
    check_prompt = OLLAMA_LAYERS["check"]["prompt_template"].format(content=content)
    check_result = call_ollama(OLLAMA_LAYERS["check"]["model"], check_prompt)
    if check_result["success"]:
        total_time += check_result["response_time"]
        layer_times["check"] = check_result["response_time"]
        if "unsafe" in check_result["output"].lower() or "不合规" in check_result["output"]:
            print("    [Check] 不合规，重新生成...")
            core_result = call_cloud_api(model_key, prompt)
            if core_result["success"]:
                total_time += core_result["response_time"]
                layer_times["core"] += core_result["response_time"]
                content = core_result["output"]
    else:
        layer_times["check"] = 0

    print("    [Show] 格式转换...")
    show_prompt = OLLAMA_LAYERS["show"]["prompt_template"].format(content=content)
    show_result = call_ollama(OLLAMA_LAYERS["show"]["model"], show_prompt)
    if show_result["success"]:
        total_time += show_result["response_time"]
        layer_times["show"] = show_result["response_time"]
        content = show_result["output"]
    else:
        layer_times["show"] = 0

    return {
        "success": True,
        "response_time": total_time,
        "output": content,
        "layer_times": layer_times
    }

def call_llmp6_full_batch(model_key, prompts, batch_size=10):
    """批量调用LLMP6-Full架构：将多条问答合并成一段话，整个6层架构只处理一次"""
    # 将多条问答合并成一段话
    combined_content = "\n\n".join([f"问题{i+1}：{prompt}" for i, prompt in enumerate(prompts)])
    combined_content += "\n\n请按顺序依次回答以上问题，每个问题的答案用【问题X答案】格式包裹。"
    
    total_time = 0
    layer_times = {}
    
    print("    [Core] 调用基座模型...")
    core_result = call_cloud_api(model_key, combined_content)
    if not core_result["success"]:
        return [{"success": False, "response_time": core_result["response_time"], "error": core_result.get("error", "Core层失败")} for _ in prompts]
    total_time += core_result["response_time"]
    layer_times["core"] = core_result["response_time"]
    content = core_result["output"]

    print("    [Assign] 意图理解...")
    assign_prompt = OLLAMA_LAYERS["assign"]["prompt_template"].format(content=combined_content)
    assign_result = call_ollama(OLLAMA_LAYERS["assign"]["model"], assign_prompt)
    if assign_result["success"]:
        total_time += assign_result["response_time"]
        layer_times["assign"] = assign_result["response_time"]
        content = assign_result["output"]
    else:
        layer_times["assign"] = 0

    print("    [Filter] 事实核查...")
    filter_prompt = OLLAMA_LAYERS["filter"]["prompt_template"].format(content=content)
    filter_result = call_ollama(OLLAMA_LAYERS["filter"]["model"], filter_prompt)
    if filter_result["success"]:
        total_time += filter_result["response_time"]
        layer_times["filter"] = filter_result["response_time"]
        content = filter_result["output"]
    else:
        layer_times["filter"] = 0

    print("    [Tool] 工具调用...")
    tool_prompt = OLLAMA_LAYERS["tool"]["prompt_template"].format(content=content)
    tool_result = call_ollama(OLLAMA_LAYERS["tool"]["model"], tool_prompt)
    if tool_result["success"]:
        total_time += tool_result["response_time"]
        layer_times["tool"] = tool_result["response_time"]
    else:
        layer_times["tool"] = 0

    print("    [Check] 合规检查...")
    check_prompt = OLLAMA_LAYERS["check"]["prompt_template"].format(content=content)
    check_result = call_ollama(OLLAMA_LAYERS["check"]["model"], check_prompt)
    if check_result["success"]:
        total_time += check_result["response_time"]
        layer_times["check"] = check_result["response_time"]
        if "unsafe" in check_result["output"].lower() or "不合规" in check_result["output"]:
            print("    [Check] 不合规，重新生成...")
            core_result = call_cloud_api(model_key, combined_content)
            if core_result["success"]:
                total_time += core_result["response_time"]
                layer_times["core"] += core_result["response_time"]
                content = core_result["output"]
    else:
        layer_times["check"] = 0

    print("    [Show] 格式转换...")
    show_prompt = OLLAMA_LAYERS["show"]["prompt_template"].format(content=content)
    show_result = call_ollama(OLLAMA_LAYERS["show"]["model"], show_prompt)
    if show_result["success"]:
        total_time += show_result["response_time"]
        layer_times["show"] = show_result["response_time"]
        content = show_result["output"]
    else:
        layer_times["show"] = 0

    # 解析批量返回的结果
    responses = []
    for i in range(len(prompts)):
        start_marker = f"【问题{i+1}答案】"
        end_marker = f"【问题{i+2}答案】" if i + 1 < len(prompts) else None
        
        if start_marker in content:
            start_idx = content.find(start_marker) + len(start_marker)
            if end_marker:
                end_idx = content.find(end_marker)
                if end_idx == -1:
                    end_idx = len(content)
            else:
                end_idx = len(content)
            answer = content[start_idx:end_idx].strip()
            responses.append({
                "success": True,
                "response_time": total_time / len(prompts),
                "output": answer,
                "layer_times": {k: v / len(prompts) for k, v in layer_times.items()}
            })
        else:
            responses.append({
                "success": False,
                "response_time": total_time / len(prompts),
                "error": f"未找到问题{i+1}的答案",
                "layer_times": {k: v / len(prompts) for k, v in layer_times.items()}
            })
    
    return responses

def calculate_stats(result_list):
    """计算统计指标"""
    times, accuracies, qualities = [], [], []
    total = len(result_list)

    for r in result_list:
        if r["success"]:
            times.append(r["response_time"])
            # 从原始结果计算指标
            prompt = r.get("prompt", "")
            output = r.get("output", "")
            quality_score = evaluate_response(output, prompt)
            accuracy = calculate_accuracy(output, prompt, quality_score)
            accuracies.append(accuracy)
            qualities.append(quality_score)

    return {
        "avg_response_time": statistics.mean(times) if times else 0,
        "avg_accuracy": statistics.mean(accuracies) if accuracies else 0,
        "avg_quality_score": statistics.mean(qualities) if qualities else 0,
        "throughput": total / (sum(times) / 1000) if times else 0,
        "total_samples": total
    }

def run_model_test(model_key, test_data, sample_size=100, batch_size=10):
    """
    运行模型测试，支持批量处理
    :param model_key: 模型名称
    :param test_data: 测试数据
    :param sample_size: 使用的数据量（默认100条）
    :param batch_size: 每批打包的数据量（默认10条）
    """
    model_info = CORE_MODELS_CONFIG[model_key]
    print(f"\n{'='*60}")
    print(f"测试模型: {model_info['name']}")
    print(f"{'='*60}")

    # 使用指定的数据量，最多不超过测试数据总量
    actual_size = min(sample_size, len(test_data))
    print(f"\n测试数据量: {actual_size} 条，每 {batch_size} 条打包成一批")
    
    raw_results = {"CoreOnly": [], "LLMP6-Full": []}

    print(f"\n测试 CoreOnly（仅基座模型）...")
    processed_count = 0
    for batch_start in range(0, actual_size, batch_size):
        batch_end = min(batch_start + batch_size, actual_size)
        batch_data = test_data[batch_start:batch_end]
        batch_prompts = [item["question"] for item in batch_data]
        
        print(f"  批次 {processed_count//batch_size + 1}/{(actual_size + batch_size - 1)//batch_size}: 处理第 {batch_start+1}-{batch_end} 条数据")
        
        # 批量调用API
        batch_results = call_cloud_api_batch(model_key, batch_prompts)
        
        for i, (item, result) in enumerate(zip(batch_data, batch_results)):
            result["prompt"] = item["question"]
            result["reference_answer"] = item.get("reference_answer", "")
            raw_results["CoreOnly"].append(result)
            processed_count += 1
        
        time.sleep(0.5)

    print(f"\n测试 LLMP6-Full（完整六层架构）...")
    processed_count = 0
    for batch_start in range(0, actual_size, batch_size):
        batch_end = min(batch_start + batch_size, actual_size)
        batch_data = test_data[batch_start:batch_end]
        batch_prompts = [item["question"] for item in batch_data]
        
        print(f"  批次 {processed_count//batch_size + 1}/{(actual_size + batch_size - 1)//batch_size}: 处理第 {batch_start+1}-{batch_end} 条数据")
        
        batch_results = call_llmp6_full_batch(model_key, batch_prompts, batch_size)
        
        for i, (item, result) in enumerate(zip(batch_data, batch_results)):
            result["prompt"] = item["question"]
            result["reference_answer"] = item.get("reference_answer", "")
            raw_results["LLMP6-Full"].append(result)
            processed_count += 1
        
        time.sleep(0.5)

    return raw_results


def run_grouped_tests(model_key, groups):
    """使用分组数据运行测试：每组10条问答，调用一次API"""
    model_info = CORE_MODELS_CONFIG[model_key]
    print("")
    print("=" * 60)
    print(f"测试模型: {model_info['name']}")
    print("=" * 60)
    print(f"")
    print(f"分组数据：{len(groups)} 组，每组 {len(groups[0])} 条问答")

    raw_results = {"CoreOnly": [], "LLMP6-Full": []}

    # 测试 CoreOnly
    print(f"")
    print("测试 CoreOnly（仅基座模型）...")
    for group_idx, group in enumerate(groups):
        group_prompts = [item["question"] for item in group]
        print(f"  组 {group_idx + 1}/{len(groups)}: 处理 {len(group)} 条问答")

        # 每组调用一次API
        batch_results = call_cloud_api_batch(model_key, group_prompts)

        for item, result in zip(group, batch_results):
            result["prompt"] = item["question"]
            result["reference_answer"] = item.get("reference_answer", "")
            raw_results["CoreOnly"].append(result)

        time.sleep(0.5)

    # 测试 LLMP6-Full
    print(f"")
    print("测试 LLMP6-Full（完整六层架构）...")
    for group_idx, group in enumerate(groups):
        group_prompts = [item["question"] for item in group]
        print(f"  组 {group_idx + 1}/{len(groups)}: 处理 {len(group)} 条问答")

        # 每组调用一次完整的6层架构
        batch_results = call_llmp6_full_batch(model_key, group_prompts)

        for item, result in zip(group, batch_results):
            result["prompt"] = item["question"]
            result["reference_answer"] = item.get("reference_answer", "")
            raw_results["LLMP6-Full"].append(result)

        time.sleep(0.5)

    return raw_results


def run_all_tests():
    print("="*60)
    print("LLMP6完整架构测试（当前已安装Ollama模型）")
    print("="*60)

    os.makedirs(RESULTS_DIR, exist_ok=True)

    # 默认从分组数据文件加载
    print("\n📊 从分组数据文件加载")
    grouped_data = load_test_data(grouped=True)
    print(f"  分组数: {grouped_data['metadata']['total_groups']}")
    print(f"  每组条数: {grouped_data['metadata']['group_size']}")
    print(f"  总数据量: {grouped_data['metadata']['total_items']} 条")

    # 将分组数据展平为普通列表
    test_data = []
    for group in grouped_data['groups']:
        test_data.extend(group)

    print(f"\n测试数据量: {len(test_data)} 条")

    all_raw_results = {}
    for model_key in CORE_MODELS_CONFIG:
        try:
            # 直接使用分组数据，每组10条调用一次API
            model_raw_results = run_grouped_tests(model_key, grouped_data['groups'])
            all_raw_results[model_key] = model_raw_results
        except Exception as e:
            print(f"\n❌ 模型 {model_key} 测试失败: {str(e)}")
            all_raw_results[model_key] = {"CoreOnly": [{"error": str(e)}], "LLMP6-Full": [{"error": str(e)}]}

    # 保存原始结果（包含所有样本的详细输出）
    raw_output_path = os.path.join(RESULTS_DIR, "raw_test_results.json")
    with open(raw_output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "experiment": "LLMP6完整架构测试",
            "timestamp": datetime.now().isoformat(),
            "test_data_samples": len(test_data),
            "layer_models": {k: v["model"] for k, v in OLLAMA_LAYERS.items()},
            "raw_results": all_raw_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 原始结果已保存到: {raw_output_path}")

    # 计算并保存统计指标
    all_stats = {}
    for model_key, raw_results in all_raw_results.items():
        all_stats[model_key] = {
            "CoreOnly": calculate_stats(raw_results["CoreOnly"]),
            "LLMP6-Full": calculate_stats(raw_results["LLMP6-Full"])
        }

    stats_output_path = os.path.join(RESULTS_DIR, "comprehensive_test_results.json")
    with open(stats_output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "experiment": "LLMP6完整架构测试",
            "timestamp": datetime.now().isoformat(),
            "test_data_samples": len(test_data),
            "layer_models": {k: v["model"] for k, v in OLLAMA_LAYERS.items()},
            "results": all_stats
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 统计指标已保存到: {stats_output_path}")

    print(f"\n{'='*60}")
    print("实验结果汇总")
    print(f"{'='*60}")
    print(f"\n{'模型':<12} {'配置':<12} {'响应时间(ms)':<16} {'准确率':<10} {'质量分数':<12} {'吞吐量':<12}")
    print("-"*80)

    for model_key, model_info in CORE_MODELS_CONFIG.items():
        stats = all_stats.get(model_key, {})
        core = stats.get("CoreOnly", {})
        full = stats.get("LLMP6-Full", {})

        if "error" not in core:
            print(f"{model_info['name']:<12} {'CoreOnly':<12} {core.get('avg_response_time', 0):.1f}           {core.get('avg_accuracy', 0):.2%}    {core.get('avg_quality_score', 0):.2%}      {core.get('throughput', 0):.2f}")
        else:
            print(f"{model_info['name']:<12} {'CoreOnly':<12} 错误")

        if "error" not in full:
            print(f"{'':<12} {'LLMP6-Full':<12} {full.get('avg_response_time', 0):.1f}           {full.get('avg_accuracy', 0):.2%}    {full.get('avg_quality_score', 0):.2%}      {full.get('throughput', 0):.2f}")
            if "error" not in core:
                time_diff = ((full["avg_response_time"] - core["avg_response_time"]) / core["avg_response_time"] * 100) if core["avg_response_time"] > 0 else 0
                print(f"{'':<12} {'变化':<12} {time_diff:+.1f}%")
        else:
            print(f"{'':<12} {'LLMP6-Full':<12} 错误")
        print("-"*90)

    print(f"\n结果已保存到: {stats_output_path}")
    return all_raw_results

if __name__ == "__main__":
    run_all_tests()
