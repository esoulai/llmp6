#!/usr/bin/env python3
"""
LLMP6测试工具模块 - 共享函数和配置
"""

import os
import sys
import json
import time
import urllib.request
import yaml
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_DIR = os.path.join(PROJECT_ROOT, "experiments", "data")
RESULTS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "results")

def load_model_config():
    config_path = os.path.join(SCRIPT_DIR, "models.yaml")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
            return config_data.get("models", {})
    
    return {
        "deepseek": {
            "name": "DeepSeek",
            "url": "https://api.deepseek.com/v1/chat/completions",
            "model": "deepseek-chat",
            "key": os.environ.get("DEEPSEEK_API_KEY", "")
        },
        "qwen": {
            "name": "Qwen",
            "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "model": "qwen3.6-plus",
            "key": os.environ.get("QWEN_API_KEY", "")
        },
        "kimi": {
            "name": "Kimi",
            "url": "https://api.moonshot.cn/v1/chat/completions",
            "model": "moonshot-v1-8k",
            "key": os.environ.get("KIMI_API_KEY", "")
        }
    }

CORE_MODELS_CONFIG = load_model_config()

OLLAMA_LAYERS = {
    "assign": {
        "name": "Assign层-意图理解",
        "model": "phi3:mini",
        "prompt_template": "请分析以下用户输入的意图，并生成适合大语言模型的提示语：\n\n用户输入：{content}\n\n意图分析：\n生成的提示语："
    },
    "tool": {
        "name": "Tool层-工具调用",
        "model": "sam860/lucy:1.7b",
        "prompt_template": "请分析以下内容是否需要调用工具（如计算器、搜索、代码执行等），并决定使用哪个工具：\n\n内容：{content}\n\n工具选择："
    },
    "filter": {
        "name": "Filter层-事实核查",
        "model": "bespoke-minicheck:latest",
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
        grouped_path = os.path.join(DATA_DIR, "csqa2_experiment_data_grouped.json")
        if os.path.exists(grouped_path):
            with open(grouped_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
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
    """调用云API"""
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
    """批量调用云API"""
    model_config = CORE_MODELS_CONFIG[model_key]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {model_config['key']}"
    }
    
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
        return [{"success": False, "response_time": (time.time() - start_time) * 1000 / len(prompts), "error": str(e)}] * len(prompts)


def call_ollama(model_name, prompt, timeout=60):
    """调用Ollama模型"""
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


def call_llmp6_full_batch(model_key, prompts):
    """批量调用LLMP6-Full架构 - 正确流程：Assign -> Core -> Tool -> Filter -> Check -> Show"""
    
    db_path = os.path.join(PROJECT_ROOT, "database.yaml")
    rules_path = os.path.join(PROJECT_ROOT, "rules.json")
    
    with open(db_path, 'r', encoding='utf-8') as f:
        db_data = yaml.safe_load(f)
    facts = db_data.get("facts", [])
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        rules_data = json.load(f)
    rules = rules_data.get("rules", [])
    banned_keywords = rules_data.get("banned_keywords", [])
    
    combined_content = "\n\n".join([f"问题{i+1}：{prompt}" for i, prompt in enumerate(prompts)])
    combined_content += "\n\n请按顺序依次回答以上问题，每个问题的答案用【问题X答案】格式包裹。"
    
    total_time = 0
    layer_times = {}
    
    print("    [Assign] 意图理解...")
    assign_prompt = OLLAMA_LAYERS["assign"]["prompt_template"].format(content=combined_content)
    assign_result = call_ollama(OLLAMA_LAYERS["assign"]["model"], assign_prompt)
    if assign_result["success"]:
        total_time += assign_result["response_time"]
        layer_times["assign"] = assign_result["response_time"]
        core_input = assign_result["output"]
    else:
        layer_times["assign"] = 0
        core_input = combined_content
    
    print("    [Core] 调用基座模型...")
    core_result = call_cloud_api(model_key, core_input)
    if not core_result["success"]:
        return [{"success": False, "response_time": core_result["response_time"], "error": core_result.get("error", "Core层失败")} for _ in prompts]
    total_time += core_result["response_time"]
    layer_times["core"] = core_result["response_time"]
    content = core_result["output"]

    print("    [Tool] 工具调用...")
    tool_prompt = OLLAMA_LAYERS["tool"]["prompt_template"].format(content=content)
    tool_result = call_ollama(OLLAMA_LAYERS["tool"]["model"], tool_prompt)
    if tool_result["success"]:
        total_time += tool_result["response_time"]
        layer_times["tool"] = tool_result["response_time"]
        content = tool_result["output"]
    else:
        layer_times["tool"] = 0

    print("    [Filter] 事实核查...")
    facts_str = "\n".join([f"- {fact}" for fact in facts])
    filter_prompt = f"""请核查以下内容的事实准确性。
    
已知事实库：
{facts_str}

待核查内容：
{content}

如果内容中的事实与已知事实库矛盾，请修正为正确内容。如果内容不涉及已知事实，则保留原内容。"""

    filter_result = call_ollama(OLLAMA_LAYERS["filter"]["model"], filter_prompt)
    if filter_result["success"]:
        total_time += filter_result["response_time"]
        layer_times["filter"] = filter_result["response_time"]
        content = filter_result["output"]
    else:
        layer_times["filter"] = 0

    print("    [Check] 合规检查...")
    rules_str = "\n".join([f"- {rule}" for rule in rules])
    keywords_str = "、".join(banned_keywords)
    check_prompt = f"""请检查以下内容是否符合安全合规要求。

合规规则：
{rules_str}

禁止关键词：{keywords_str}

待检查内容：
{content}

如果内容违反规则，请指出违反了什么规则，并说明原因。如果合规，请回复"合规"。"""

    check_result = call_ollama(OLLAMA_LAYERS["check"]["model"], check_prompt)
    if check_result["success"]:
        total_time += check_result["response_time"]
        layer_times["check"] = check_result["response_time"]
        
        if "不合规" in check_result["output"] or "违规" in check_result["output"] or "违反" in check_result["output"]:
            print("    [Check] 不合规，重新生成...")
            retry_prompt = f"""请重新生成回答，注意以下问题：
            
{check_result["output"]}

原始问题：
{combined_content}

请生成符合合规要求的回答，每个问题的答案用【问题X答案】格式包裹。"""
            
            retry_result = call_cloud_api(model_key, retry_prompt)
            if retry_result["success"]:
                total_time += retry_result["response_time"]
                layer_times["core"] += retry_result["response_time"]
                content = retry_result["output"]
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


def save_results(model_key, config_type, results):
    """保存测试结果到独立文件"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output_path = os.path.join(RESULTS_DIR, f"{model_key}_{config_type}.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "model": model_key,
            "config": config_type,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果已保存到: {output_path}")
    return output_path
