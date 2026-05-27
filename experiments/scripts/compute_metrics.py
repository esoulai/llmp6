#!/usr/bin/env python3
"""
从6个独立测试结果文件计算综合统计指标
"""

import os
import sys
import json
import statistics
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'results')

def evaluate_response(output, prompt, reference_answer=""):
    """评估响应质量的综合指标"""
    quality_score = 0.0

    if len(output.strip()) == 0:
        return 0.0
    if len(output.strip()) >= 20:
        quality_score += 0.2
    if len(output.strip()) >= 50:
        quality_score += 0.1
    if len(output.strip()) >= 100:
        quality_score += 0.1

    helpful_words = ["可以", "会", "能够", "建议", "请", "帮助", "您", "是", "正确", "答案", "解", "回答"]
    helpful_count = sum(1 for word in helpful_words if word in output)
    quality_score += min(0.2, helpful_count * 0.04)

    if "?" in prompt:
        if any(kw in output for kw in ["答", "回答", "解", "是", "答案"]):
            quality_score += 0.1
        
        if reference_answer:
            ref_tokens = set(reference_answer.lower().strip().split())
            output_tokens = set(output.lower().strip().split())
            if ref_tokens and output_tokens:
                overlap = len(ref_tokens & output_tokens) / len(ref_tokens)
                quality_score += min(0.3, overlap * 0.3)

    if output.count('。') >= 2 or output.count('！') >= 1:
        quality_score += 0.1

    return max(0.0, min(1.0, quality_score))

def calculate_accuracy(output, prompt, quality_score, reference_answer=""):
    """计算准确率指标"""
    accuracy = 0.3
    
    if reference_answer and reference_answer.strip():
        ref_answer = reference_answer.strip().lower()
        
        if ref_answer in ["yes", "no", "true", "false"]:
            cleaned_output = output
            prefixes_to_remove = ["原始内容：", "原始回答：", "输出内容："]
            for prefix in prefixes_to_remove:
                if cleaned_output.startswith(prefix):
                    cleaned_output = cleaned_output[len(prefix):]
            output_lower = cleaned_output.lower()
            
            positive_keywords = ["yes", "true", "正确", "是", "对", "可以", "会", "能够", "确实", "的确", "正确的", "是的", "没错", "准确", "赞同"]
            negative_keywords = ["no", "false", "错误", "不是", "不对", "不能", "不会", "不正确", "并非", "并不", "不总是", "不完全", "不准确"]
            
            special_patterns = [
                ("does not almost always", "no"),
                ("does not always", "no"),
                ("is not almost always", "no"),
                ("is not always", "no"),
                ("not almost always", "no"),
                ("not always", "no"),
                ("almost always", "yes"),
                ("not true", "no"),
                ("is true", "yes"),
                ("is false", "no"),
                ("is correct", "yes"),
                ("is incorrect", "no"),
                ("is not correct", "no"),
                ("is not true", "no")
            ]
            
            detected_pattern = None
            for pattern, value in special_patterns:
                if pattern in output_lower:
                    detected_pattern = value
                    break
            
            if detected_pattern:
                if (ref_answer in ["yes", "true"] and detected_pattern == "yes") or \
                   (ref_answer in ["no", "false"] and detected_pattern == "no"):
                    accuracy = 0.95
                else:
                    accuracy = 0.05
            else:
                pos_count = sum(output_lower.count(kw) for kw in positive_keywords)
                neg_count = sum(output_lower.count(kw) for kw in negative_keywords)
                
                total_count = pos_count + neg_count
                
                if total_count > 0:
                    pos_ratio = pos_count / total_count
                    
                    if ref_answer in ["yes", "true"]:
                        if pos_ratio > 0.5:
                            accuracy = 0.95
                        elif pos_ratio < 0.3:
                            accuracy = 0.05
                        else:
                            accuracy = 0.5 + (pos_ratio - 0.5) * 0.9
                    else:
                        if pos_ratio < 0.3:
                            accuracy = 0.95
                        elif pos_ratio > 0.5:
                            accuracy = 0.05
                        else:
                            accuracy = 0.5 - (pos_ratio - 0.5) * 0.9
                else:
                    accuracy = quality_score * 0.8
        else:
            ref_tokens = set(ref_answer.lower().strip().split())
            output_tokens = set(output.lower().strip().split())
            
            if ref_tokens:
                overlap = len(ref_tokens & output_tokens) / len(ref_tokens)
                accuracy = overlap * 0.9
                
                if overlap >= 0.9:
                    accuracy += 0.1
                elif overlap >= 0.7:
                    accuracy += 0.05
    else:
        accuracy = quality_score * 0.8
        
        if "?" in prompt:
            if len(output) < 20:
                accuracy -= 0.05
            elif len(output) > 80:
                accuracy += 0.05
    
    return max(0.0, min(1.0, accuracy))

def detect_prediction(output):
    """检测模型输出的预测结果（yes/no）"""
    output_lower = output.lower()
    positive_keywords = ["yes", "true", "正确", "是", "对", "可以", "会", "能够", "确实", "的确", "正确的", "是的", "没错", "准确", "赞同"]
    negative_keywords = ["no", "false", "错误", "不是", "不对", "不能", "不会", "不正确", "并非", "并不", "不总是", "不完全", "不准确"]
    
    special_patterns = [
        ("does not almost always", "no"),
        ("does not always", "no"),
        ("is not almost always", "no"),
        ("is not always", "no"),
        ("not almost always", "no"),
        ("not always", "no"),
        ("almost always", "yes"),
        ("not true", "no"),
        ("is true", "yes"),
        ("is false", "no"),
        ("is correct", "yes"),
        ("is incorrect", "no"),
        ("is not correct", "no"),
        ("is not true", "no")
    ]
    
    for pattern, value in special_patterns:
        if pattern in output_lower:
            return value
    
    pos_count = sum(output_lower.count(kw) for kw in positive_keywords)
    neg_count = sum(output_lower.count(kw) for kw in negative_keywords)
    
    if pos_count > neg_count:
        return "yes"
    elif neg_count > pos_count:
        return "no"
    return None

def calculate_stats(result_list):
    """计算统计指标"""
    times, accuracies, qualities, output_lengths = [], [], [], []
    success_count = 0
    error_count = 0
    total = len(result_list)
    
    tp = 0  # True Positive
    tn = 0  # True Negative  
    fp = 0  # False Positive
    fn = 0  # False Negative
    
    # 用于计算多样性指标
    all_tokens = []
    all_outputs = []
    
    # 用于计算延迟抖动
    prev_time = 0
    jitters = []

    for r in result_list:
        if r.get("success") and "error" not in r:
            success_count += 1
            current_time = r.get("response_time", 0)
            times.append(current_time)
            
            # 计算延迟抖动
            if prev_time > 0:
                jitters.append(abs(current_time - prev_time))
            prev_time = current_time
            
            prompt = r.get("prompt", "")
            output = r.get("output", "")
            reference_answer = r.get("reference_answer", "")
            
            # 收集用于多样性分析
            all_outputs.append(output)
            tokens = output.split()
            all_tokens.extend(tokens)
            
            quality_score = evaluate_response(output, prompt, reference_answer)
            accuracy = calculate_accuracy(output, prompt, quality_score, reference_answer)
            accuracies.append(accuracy)
            qualities.append(quality_score)
            output_lengths.append(len(output))
            
            prediction = detect_prediction(output)
            actual = reference_answer.lower().strip()
            
            if prediction and actual in ["yes", "no", "true", "false"]:
                actual_binary = "yes" if actual in ["yes", "true"] else "no"
                
                if prediction == "yes" and actual_binary == "yes":
                    tp += 1
                elif prediction == "no" and actual_binary == "no":
                    tn += 1
                elif prediction == "yes" and actual_binary == "no":
                    fp += 1
                elif prediction == "no" and actual_binary == "yes":
                    fn += 1
        else:
            error_count += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    sorted_times = sorted(times)
    p95 = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0
    p99 = sorted_times[int(len(sorted_times) * 0.99)] if sorted_times else 0
    
    hit_count = sum(1 for r in result_list if r.get("success") and ("回答" in r.get("output", "") or "答案" in r.get("output", "")))
    hit_rate = hit_count / total if total > 0 else 0
    
    # 计算变异系数（相对波动性）
    cv = (statistics.stdev(times) / statistics.mean(times)) * 100 if times and len(times) > 1 and statistics.mean(times) > 0 else 0
    
    # 计算平均延迟抖动
    avg_jitter = statistics.mean(jitters) if jitters else 0
    
    # 计算输出多样性指标
    distinct_1 = len(set(all_tokens)) / len(all_tokens) if all_tokens else 0
    if len(all_tokens) >= 2:
        bigrams = [tuple(all_tokens[i:i+2]) for i in range(len(all_tokens)-1)]
        distinct_2 = len(set(bigrams)) / len(bigrams) if bigrams else 0
    else:
        distinct_2 = 0
    
    # 计算重复率
    total_chars = sum(len(o) for o in all_outputs)
    duplicate_chars = 0
    for output in all_outputs:
        for i in range(len(output)-3):
            substr = output[i:i+4]
            if output.count(substr) > 1:
                duplicate_chars += 1
    repetition_rate = duplicate_chars / total_chars if total_chars > 0 else 0
    
    # 计算可读性指标（Flesch-Kincaid简易指数简化版）
    total_sentences = sum(o.count('。') + o.count('！') + o.count('?') + o.count('?') for o in all_outputs)
    total_words = len(all_tokens)
    avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
    # 简化的可读性分数（越高越易读）
    readability_score = 206.835 - 1.015 * avg_sentence_length if avg_sentence_length > 0 else 0

    return {
        "avg_response_time": statistics.mean(times) if times else 0,
        "response_time_std": statistics.stdev(times) if len(times) > 1 else 0,
        "response_time_cv": cv,
        "avg_jitter": avg_jitter,
        "median_response_time": statistics.median(times) if times else 0,
        "min_response_time": min(times) if times else 0,
        "max_response_time": max(times) if times else 0,
        "p95_response_time": p95,
        "p99_response_time": p99,
        "avg_accuracy": statistics.mean(accuracies) if accuracies else 0,
        "accuracy_std": statistics.stdev(accuracies) if len(accuracies) > 1 else 0,
        "avg_quality_score": statistics.mean(qualities) if qualities else 0,
        "quality_score_std": statistics.stdev(qualities) if len(qualities) > 1 else 0,
        "avg_output_length": statistics.mean(output_lengths) if output_lengths else 0,
        "output_length_std": statistics.stdev(output_lengths) if len(output_lengths) > 1 else 0,
        "success_rate": success_count / total if total > 0 else 0,
        "error_rate": error_count / total if total > 0 else 0,
        "throughput": total / (sum(times) / 1000) if times else 0,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "hit_rate": hit_rate,
        "distinct_1": distinct_1,
        "distinct_2": distinct_2,
        "repetition_rate": repetition_rate,
        "readability_score": readability_score,
        "avg_sentence_length": avg_sentence_length,
        "total_samples": total
    }

def load_single_result(model_key, config_type):
    """加载单个测试结果文件"""
    filename = f"{model_key}_{config_type}.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ 结果文件不存在: {filename}")
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ 已加载: {filename}")
    return data["results"]

def compute_metrics():
    """遍历6个结果文件并计算综合统计指标"""
    print("=" * 60)
    print("计算综合统计指标")
    print("=" * 60)

    os.makedirs(RESULTS_DIR, exist_ok=True)

    models = ["deepseek", "qwen", "kimi"]
    configs = ["coreonly", "full"]
    
    all_stats = {}
    
    for model_key in models:
        all_stats[model_key] = {}
        
        for config_type in configs:
            results = load_single_result(model_key, config_type)
            
            if results is not None:
                stats = calculate_stats(results)
                all_stats[model_key][config_type] = stats
            else:
                all_stats[model_key][config_type] = {"error": "结果文件不存在"}

    # 保存统计指标
    stats_output_path = os.path.join(RESULTS_DIR, "comprehensive_test_results.json")
    with open(stats_output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "experiment": "LLMP6完整架构测试（拆分版）",
            "timestamp": datetime.now().isoformat(),
            "results": all_stats
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 统计指标已保存到: {stats_output_path}")

    # 打印结果汇总
    print(f"\n{'='*60}")
    print("实验结果汇总")
    print(f"{'='*60}")
    print(f"\n{'模型':<12} {'配置':<12} {'响应时间(ms)':<16} {'准确率':<10} {'质量分数':<12} {'吞吐量':<12}")
    print("-" * 80)

    name_mapping = {
        "deepseek": "DeepSeek",
        "qwen": "Qwen",
        "kimi": "Kimi",
        "coreonly": "CoreOnly",
        "full": "LLMP6-Full"
    }

    for model_key, stats in all_stats.items():
        model_name = name_mapping.get(model_key, model_key)
        
        for config_type, config_stats in stats.items():
            config_name = name_mapping.get(config_type, config_type)
            
            if "error" not in config_stats and config_stats.get("total_samples", 0) > 0:
                print(f"{model_name:<12} {config_name:<12} {config_stats.get('avg_response_time', 0):.1f}           {config_stats.get('avg_accuracy', 0):.2%}    {config_stats.get('avg_quality_score', 0):.2%}      {config_stats.get('throughput', 0):.2f}")
            else:
                print(f"{model_name:<12} {config_name:<12} 未完成")

    print(f"\n{'='*60}")
    print("✅ 指标计算完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    compute_metrics()
