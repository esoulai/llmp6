#!/usr/bin/env python3
"""
Qwen LLMP6-Full 测试 - 使用完整六层架构
"""

import os
import time
from test_utils import (
    load_test_data,
    call_llmp6_full_batch,
    save_results,
    CORE_MODELS_CONFIG
)

def run_qwen_full():
    print("=" * 60)
    print("Qwen LLMP6-Full 测试")
    print("=" * 60)

    # 加载分组数据
    grouped_data = load_test_data(grouped=True)
    print(f"\n分组数据：{len(grouped_data['groups'])} 组，每组 {len(grouped_data['groups'][0])} 条问答")

    results = []
    model_key = "qwen"

    for group_idx, group in enumerate(grouped_data['groups']):
        group_prompts = [item["question"] for item in group]
        print(f"\n  组 {group_idx + 1}/{len(grouped_data['groups'])}: 处理 {len(group)} 条问答")

        # 每组调用一次完整的6层架构
        batch_results = call_llmp6_full_batch(model_key, group_prompts)

        for item, result in zip(group, batch_results):
            result["prompt"] = item["question"]
            result["reference_answer"] = item.get("reference_answer", "")
            results.append(result)

        time.sleep(0.5)

    # 保存结果
    save_results(model_key, "full", results)

    print(f"\n✅ Qwen LLMP6-Full 测试完成")
    print(f"   处理样本数: {len(results)}")

if __name__ == "__main__":
    run_qwen_full()
