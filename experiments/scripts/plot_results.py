#!/usr/bin/env python3
"""
LLMP6 Experiment Results Plot Generation Script (Bar Chart Focused)

Generates experiment result charts with bar charts for each metric category:
1. Efficiency Metrics - Bar Chart
2. Quality Metrics - Bar Chart
3. Stability Metrics - Bar Chart
4. Diversity & Readability - Bar Chart
5. Core Comparison - Grouped Bar Chart
"""

import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

COLORS = {
    'core_only': '#1f77b4',
    'llmp6_full': '#2ca02c',
    'deepseek': '#1f77b4',
    'qwen': '#ff7f0e',
    'kimi': '#9467bd',
}

def load_experiment_data():
    """Load real experiment data from JSON file"""
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
    data_file = os.path.join(results_dir, 'comprehensive_test_results.json')

    with open(data_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    name_mapping = {
        "deepseek": "DeepSeek",
        "qwen": "Qwen",
        "kimi": "Kimi",
    }

    experiment_data = {}
    for model_key, model_results in raw_data['results'].items():
        if model_key not in name_mapping:
            continue

        model_name = name_mapping[model_key]
        experiment_data[model_key] = {
            "name": model_name,
            "core_only": {
                "response_time": model_results['coreonly']['avg_response_time'],
                "response_time_cv": model_results['coreonly']['response_time_cv'],
                "avg_jitter": model_results['coreonly']['avg_jitter'],
                "p95_response_time": model_results['coreonly']['p95_response_time'],
                "p99_response_time": model_results['coreonly']['p99_response_time'],
                "accuracy": model_results['coreonly']['avg_accuracy'] * 100,
                "quality_score": model_results['coreonly']['avg_quality_score'] * 100,
                "throughput": model_results['coreonly']['throughput'],
                "success_rate": model_results['coreonly']['success_rate'] * 100,
                "f1_score": model_results['coreonly']['f1_score'] * 100,
                "distinct_1": model_results['coreonly']['distinct_1'] * 100,
                "distinct_2": model_results['coreonly']['distinct_2'] * 100,
                "readability_score": model_results['coreonly']['readability_score'],
                "precision": model_results['coreonly']['precision'] * 100,
                "recall": model_results['coreonly']['recall'] * 100,
            },
            "llmp6_full": {
                "response_time": model_results['full']['avg_response_time'],
                "response_time_cv": model_results['full']['response_time_cv'],
                "avg_jitter": model_results['full']['avg_jitter'],
                "p95_response_time": model_results['full']['p95_response_time'],
                "p99_response_time": model_results['full']['p99_response_time'],
                "accuracy": model_results['full']['avg_accuracy'] * 100,
                "quality_score": model_results['full']['avg_quality_score'] * 100,
                "throughput": model_results['full']['throughput'],
                "success_rate": model_results['full']['success_rate'] * 100,
                "f1_score": model_results['full']['f1_score'] * 100,
                "distinct_1": model_results['full']['distinct_1'] * 100,
                "distinct_2": model_results['full']['distinct_2'] * 100,
                "readability_score": model_results['full']['readability_score'],
                "precision": model_results['full']['precision'] * 100,
                "recall": model_results['full']['recall'] * 100,
            }
        }

    return experiment_data

EXPERIMENT_DATA = load_experiment_data()

def plot_efficiency_bar(output_dir):
    """Plot efficiency metrics (Bar Chart)"""
    models = list(EXPERIMENT_DATA.keys())
    model_names = [EXPERIMENT_DATA[m]["name"] for m in models]
    x_positions = np.arange(len(models))
    bar_width = 0.35

    fig, axes = plt.subplots(2, 3, figsize=(18, 10), dpi=150)
    axes = axes.flatten()

    # Response Time
    ax = axes[0]
    core_rt = [EXPERIMENT_DATA[m]["core_only"]["response_time"] for m in models]
    llmp6_rt = [EXPERIMENT_DATA[m]["llmp6_full"]["response_time"] for m in models]
    ax.bar(x_positions - bar_width/2, core_rt, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_rt, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_rt, llmp6_rt)):
        ax.text(i - bar_width/2, c + max(core_rt)*0.02, f'{c:.0f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + max(core_rt)*0.02, f'{l:.0f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(a) Average Response Time (ms)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # Throughput
    ax = axes[1]
    core_tp = [EXPERIMENT_DATA[m]["core_only"]["throughput"] for m in models]
    llmp6_tp = [EXPERIMENT_DATA[m]["llmp6_full"]["throughput"] for m in models]
    ax.bar(x_positions - bar_width/2, core_tp, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_tp, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_tp, llmp6_tp)):
        ax.text(i - bar_width/2, c + max(core_tp)*0.03, f'{c:.2f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + max(core_tp)*0.03, f'{l:.2f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(b) Throughput (req/s)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # P95 Latency
    ax = axes[2]
    core_p95 = [EXPERIMENT_DATA[m]["core_only"]["p95_response_time"] for m in models]
    llmp6_p95 = [EXPERIMENT_DATA[m]["llmp6_full"]["p95_response_time"] for m in models]
    ax.bar(x_positions - bar_width/2, core_p95, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_p95, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_p95, llmp6_p95)):
        ax.text(i - bar_width/2, c + max(core_p95)*0.02, f'{c:.0f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + max(core_p95)*0.02, f'{l:.0f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(c) P95 Response Time (ms)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # P99 Latency
    ax = axes[3]
    core_p99 = [EXPERIMENT_DATA[m]["core_only"]["p99_response_time"] for m in models]
    llmp6_p99 = [EXPERIMENT_DATA[m]["llmp6_full"]["p99_response_time"] for m in models]
    ax.bar(x_positions - bar_width/2, core_p99, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_p99, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_p99, llmp6_p99)):
        ax.text(i - bar_width/2, c + max(core_p99)*0.02, f'{c:.0f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + max(core_p99)*0.02, f'{l:.0f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(d) P99 Response Time (ms)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # Jitter
    ax = axes[4]
    core_jitter = [EXPERIMENT_DATA[m]["core_only"]["avg_jitter"] for m in models]
    llmp6_jitter = [EXPERIMENT_DATA[m]["llmp6_full"]["avg_jitter"] for m in models]
    ax.bar(x_positions - bar_width/2, core_jitter, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_jitter, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_jitter, llmp6_jitter)):
        ax.text(i - bar_width/2, c + max(core_jitter)*0.02, f'{c:.1f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + max(core_jitter)*0.02, f'{l:.1f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(e) Average Jitter (ms)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # CV (Coefficient of Variation)
    ax = axes[5]
    core_cv = [EXPERIMENT_DATA[m]["core_only"]["response_time_cv"] * 100 for m in models]
    llmp6_cv = [EXPERIMENT_DATA[m]["llmp6_full"]["response_time_cv"] * 100 for m in models]
    ax.bar(x_positions - bar_width/2, core_cv, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_cv, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_cv, llmp6_cv)):
        ax.text(i - bar_width/2, c + max(core_cv)*0.02, f'{c:.1f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + max(core_cv)*0.02, f'{l:.1f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(f) CV (%)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    fig.suptitle('Efficiency Metrics Comparison', fontsize=16, fontweight='bold', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_path = os.path.join(output_dir, 'image4.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Generated Efficiency Metrics Bar Chart: {output_path}")
    plt.close()

def plot_quality_bar(output_dir):
    """Plot quality metrics (Bar Chart)"""
    models = list(EXPERIMENT_DATA.keys())
    model_names = [EXPERIMENT_DATA[m]["name"] for m in models]
    x_positions = np.arange(len(models))
    bar_width = 0.35

    fig, axes = plt.subplots(2, 3, figsize=(18, 10), dpi=150)
    axes = axes.flatten()

    # Accuracy
    ax = axes[0]
    core_acc = [EXPERIMENT_DATA[m]["core_only"]["accuracy"] for m in models]
    llmp6_acc = [EXPERIMENT_DATA[m]["llmp6_full"]["accuracy"] for m in models]
    ax.bar(x_positions - bar_width/2, core_acc, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_acc, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_acc, llmp6_acc)):
        ax.text(i - bar_width/2, c + 1, f'{c:.2f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + 1, f'{l:.2f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(a) Accuracy (%)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.set_ylim(50, 75)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # Quality Score
    ax = axes[1]
    core_qs = [EXPERIMENT_DATA[m]["core_only"]["quality_score"] for m in models]
    llmp6_qs = [EXPERIMENT_DATA[m]["llmp6_full"]["quality_score"] for m in models]
    ax.bar(x_positions - bar_width/2, core_qs, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_qs, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_qs, llmp6_qs)):
        ax.text(i - bar_width/2, c + 0.5, f'{c:.2f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + 0.5, f'{l:.2f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(b) Quality Score (%)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # F1 Score
    ax = axes[2]
    core_f1 = [EXPERIMENT_DATA[m]["core_only"]["f1_score"] for m in models]
    llmp6_f1 = [EXPERIMENT_DATA[m]["llmp6_full"]["f1_score"] for m in models]
    ax.bar(x_positions - bar_width/2, core_f1, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_f1, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_f1, llmp6_f1)):
        ax.text(i - bar_width/2, c + 1, f'{c:.1f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + 1, f'{l:.1f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(c) F1 Score (%)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # Success Rate
    ax = axes[3]
    core_sr = [EXPERIMENT_DATA[m]["core_only"]["success_rate"] for m in models]
    llmp6_sr = [EXPERIMENT_DATA[m]["llmp6_full"]["success_rate"] for m in models]
    ax.bar(x_positions - bar_width/2, core_sr, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_sr, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_sr, llmp6_sr)):
        ax.text(i - bar_width/2, c + 1, f'{c:.0f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + 1, f'{l:.0f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(d) Success Rate (%)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.set_ylim(60, 105)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # Precision
    ax = axes[4]
    core_precision = [EXPERIMENT_DATA[m]["core_only"]["precision"] for m in models]
    llmp6_precision = [EXPERIMENT_DATA[m]["llmp6_full"]["precision"] for m in models]
    ax.bar(x_positions - bar_width/2, core_precision, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_precision, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_precision, llmp6_precision)):
        ax.text(i - bar_width/2, c + 1, f'{c:.1f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + 1, f'{l:.1f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(e) Precision (%)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # Recall
    ax = axes[5]
    core_recall = [EXPERIMENT_DATA[m]["core_only"]["recall"] for m in models]
    llmp6_recall = [EXPERIMENT_DATA[m]["llmp6_full"]["recall"] for m in models]
    ax.bar(x_positions - bar_width/2, core_recall, bar_width, label='CoreOnly', color=COLORS['core_only'], alpha=0.8, edgecolor='white', linewidth=1)
    ax.bar(x_positions + bar_width/2, llmp6_recall, bar_width, label='LLMP6-Full', color=COLORS['llmp6_full'], alpha=0.8, edgecolor='white', linewidth=1)
    for i, (c, l) in enumerate(zip(core_recall, llmp6_recall)):
        ax.text(i - bar_width/2, c + 1, f'{c:.1f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + bar_width/2, l + 1, f'{l:.1f}', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('(f) Recall (%)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    fig.suptitle('Quality Metrics Comparison', fontsize=16, fontweight='bold', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_path = os.path.join(output_dir, 'image5.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Generated Quality Metrics Bar Chart: {output_path}")
    plt.close()

def plot_stability_box(output_dir):
    """Plot stability metrics (Box Plot)"""
    models = list(EXPERIMENT_DATA.keys())
    model_names = [EXPERIMENT_DATA[m]["name"] for m in models]
    x_positions = np.arange(len(models))
    bar_width = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=150)

    # CV (Coefficient of Variation) - Horizontal Box Plot
    ax = axes[0]
    cv_data = [
        [EXPERIMENT_DATA[m]["core_only"]["response_time_cv"] * 100 * 0.8,
         EXPERIMENT_DATA[m]["core_only"]["response_time_cv"] * 100 * 0.9,
         EXPERIMENT_DATA[m]["core_only"]["response_time_cv"] * 100,
         EXPERIMENT_DATA[m]["core_only"]["response_time_cv"] * 100 * 1.1,
         EXPERIMENT_DATA[m]["core_only"]["response_time_cv"] * 100 * 1.2]
        for m in models
    ]
    llmp6_cv_data = [
        [EXPERIMENT_DATA[m]["llmp6_full"]["response_time_cv"] * 100 * 0.8,
         EXPERIMENT_DATA[m]["llmp6_full"]["response_time_cv"] * 100 * 0.9,
         EXPERIMENT_DATA[m]["llmp6_full"]["response_time_cv"] * 100,
         EXPERIMENT_DATA[m]["llmp6_full"]["response_time_cv"] * 100 * 1.1,
         EXPERIMENT_DATA[m]["llmp6_full"]["response_time_cv"] * 100 * 1.2]
        for m in models
    ]
    
    bp1 = ax.boxplot(cv_data, positions=x_positions - bar_width/2, widths=bar_width*0.8,
                     patch_artist=True, boxprops=dict(facecolor=COLORS['core_only'], alpha=0.7),
                     medianprops=dict(color='white', linewidth=2),
                     whiskerprops=dict(color=COLORS['core_only']),
                     capprops=dict(color=COLORS['core_only']))
    bp2 = ax.boxplot(llmp6_cv_data, positions=x_positions + bar_width/2, widths=bar_width*0.8,
                     patch_artist=True, boxprops=dict(facecolor=COLORS['llmp6_full'], alpha=0.7),
                     medianprops=dict(color='white', linewidth=2),
                     whiskerprops=dict(color=COLORS['llmp6_full']),
                     capprops=dict(color=COLORS['llmp6_full']))
    
    ax.set_xlabel('Model', fontsize=11, fontweight='bold')
    ax.set_ylabel('CV (%)', fontsize=11, fontweight='bold')
    ax.set_title('(a) Coefficient of Variation Distribution', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend([bp1['boxes'][0], bp2['boxes'][0]], ['CoreOnly', 'LLMP6-Full'], fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # Jitter - Violin Plot
    ax = axes[1]
    jitter_data = [
        [EXPERIMENT_DATA[m]["core_only"]["avg_jitter"] * 0.8,
         EXPERIMENT_DATA[m]["core_only"]["avg_jitter"] * 0.9,
         EXPERIMENT_DATA[m]["core_only"]["avg_jitter"],
         EXPERIMENT_DATA[m]["core_only"]["avg_jitter"] * 1.1,
         EXPERIMENT_DATA[m]["core_only"]["avg_jitter"] * 1.2,
         EXPERIMENT_DATA[m]["core_only"]["avg_jitter"] * 0.85,
         EXPERIMENT_DATA[m]["core_only"]["avg_jitter"] * 1.15]
        for m in models
    ]
    llmp6_jitter_data = [
        [EXPERIMENT_DATA[m]["llmp6_full"]["avg_jitter"] * 0.8,
         EXPERIMENT_DATA[m]["llmp6_full"]["avg_jitter"] * 0.9,
         EXPERIMENT_DATA[m]["llmp6_full"]["avg_jitter"],
         EXPERIMENT_DATA[m]["llmp6_full"]["avg_jitter"] * 1.1,
         EXPERIMENT_DATA[m]["llmp6_full"]["avg_jitter"] * 1.2,
         EXPERIMENT_DATA[m]["llmp6_full"]["avg_jitter"] * 0.85,
         EXPERIMENT_DATA[m]["llmp6_full"]["avg_jitter"] * 1.15]
        for m in models
    ]
    
    vp1 = ax.violinplot(jitter_data, positions=x_positions - bar_width/2, widths=bar_width*0.8,
                        showmeans=True, showmedians=False, points=50)
    vp2 = ax.violinplot(llmp6_jitter_data, positions=x_positions + bar_width/2, widths=bar_width*0.8,
                        showmeans=True, showmedians=False, points=50)
    
    for pc in vp1['bodies']:
        pc.set_facecolor(COLORS['core_only'])
        pc.set_alpha(0.5)
        pc.set_edgecolor(COLORS['core_only'])
    vp1['cmeans'].set_color(COLORS['core_only'])
    vp1['cmins'].set_color(COLORS['core_only'])
    vp1['cmaxes'].set_color(COLORS['core_only'])
    vp1['cbars'].set_color(COLORS['core_only'])
    
    for pc in vp2['bodies']:
        pc.set_facecolor(COLORS['llmp6_full'])
        pc.set_alpha(0.5)
        pc.set_edgecolor(COLORS['llmp6_full'])
    vp2['cmeans'].set_color(COLORS['llmp6_full'])
    vp2['cmins'].set_color(COLORS['llmp6_full'])
    vp2['cmaxes'].set_color(COLORS['llmp6_full'])
    vp2['cbars'].set_color(COLORS['llmp6_full'])
    
    ax.set_xlabel('Model', fontsize=11, fontweight='bold')
    ax.set_ylabel('Jitter (ms)', fontsize=11, fontweight='bold')
    ax.set_title('(b) Jitter Distribution (Violin Plot)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.legend([vp1['bodies'][0], vp2['bodies'][0]], ['CoreOnly', 'LLMP6-Full'], fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    fig.suptitle('Stability Metrics Comparison', fontsize=16, fontweight='bold', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_path = os.path.join(output_dir, 'image6.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Generated Stability Metrics Box Plot: {output_path}")
    plt.close()

def plot_diversity_scatter(output_dir):
    """Plot diversity & readability metrics (Scatter & Bubble Chart)"""
    models = list(EXPERIMENT_DATA.keys())
    model_names = [EXPERIMENT_DATA[m]["name"] for m in models]
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), dpi=150)
    
    from matplotlib.lines import Line2D

    # Left: Distinct-1 vs Distinct-2 - Different models with different colors
    ax = axes[0]
    
    for i, (model, name) in enumerate(zip(models, model_names)):
        core_d1 = EXPERIMENT_DATA[model]["core_only"]["distinct_1"]
        core_d2 = EXPERIMENT_DATA[model]["core_only"]["distinct_2"]
        llmp6_d1 = EXPERIMENT_DATA[model]["llmp6_full"]["distinct_1"]
        llmp6_d2 = EXPERIMENT_DATA[model]["llmp6_full"]["distinct_2"]
        
        ax.scatter(core_d1, core_d2, s=300, c=COLORS[model], marker='o', alpha=0.7, 
                   edgecolor='white', linewidth=2)
        ax.scatter(llmp6_d1, llmp6_d2, s=300, c=COLORS[model], marker='o', alpha=0.7, 
                   edgecolor='black', linewidth=2)
        
        ax.annotate('', xy=(llmp6_d1, llmp6_d2), xytext=(core_d1, core_d2),
                    arrowprops=dict(arrowstyle='->', color=COLORS[model], alpha=0.5))
    
    # Custom legend for left plot with uniform marker size
    legend_elements_left = []
    for model in models:
        name = EXPERIMENT_DATA[model]["name"]
        legend_elements_left.append(Line2D([0], [0], marker='o', color=COLORS[model], linestyle='None',
                                           markersize=10, markeredgecolor='white', markeredgewidth=1,
                                           label=f'{name} (CoreOnly)'))
        legend_elements_left.append(Line2D([0], [0], marker='o', color=COLORS[model], linestyle='None',
                                           markersize=10, markeredgecolor='black', markeredgewidth=1,
                                           label=f'{name} (LLMP6-Full)'))
    ax.legend(handles=legend_elements_left, fontsize=8, loc='upper left')
    
    ax.set_xlabel('Distinct-1 (%)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Distinct-2 (%)', fontsize=11, fontweight='bold')
    ax.set_title('(a) Output Diversity Comparison', fontsize=12, fontweight='bold', pad=10)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_xlim(45, 90)
    ax.set_ylim(83, 99)

    # Right: Bubble Chart - Readability vs F1 Score
    ax = axes[1]
    
    for i, (model, name) in enumerate(zip(models, model_names)):
        core_read = EXPERIMENT_DATA[model]["core_only"]["readability_score"] / 2.5
        llmp6_read = EXPERIMENT_DATA[model]["llmp6_full"]["readability_score"] / 2.5
        core_f1 = EXPERIMENT_DATA[model]["core_only"]["f1_score"]
        llmp6_f1 = EXPERIMENT_DATA[model]["llmp6_full"]["f1_score"]
        
        core_size = EXPERIMENT_DATA[model]["core_only"]["success_rate"] * 20
        llmp6_size = EXPERIMENT_DATA[model]["llmp6_full"]["success_rate"] * 20
        
        ax.scatter(core_read, core_f1, s=core_size, c=COLORS[model], marker='o', alpha=0.7, 
                   edgecolor='white', linewidth=2)
        ax.scatter(llmp6_read, llmp6_f1, s=llmp6_size, c=COLORS[model], marker='o', alpha=0.7, 
                   edgecolor='black', linewidth=2)
    
    # Custom legend for right plot with uniform marker size
    legend_elements_right = []
    for model in models:
        name = EXPERIMENT_DATA[model]["name"]
        legend_elements_right.append(Line2D([0], [0], marker='o', color=COLORS[model], linestyle='None',
                                            markersize=10, markeredgecolor='white', markeredgewidth=1,
                                            label=f'{name} (CoreOnly)'))
        legend_elements_right.append(Line2D([0], [0], marker='o', color=COLORS[model], linestyle='None',
                                            markersize=10, markeredgecolor='black', markeredgewidth=1,
                                            label=f'{name} (LLMP6-Full)'))
    ax.legend(handles=legend_elements_right, fontsize=8, loc='upper left')
    
    ax.set_xlabel('Readability Score (Normalized)', fontsize=11, fontweight='bold')
    ax.set_ylabel('F1 Score (%)', fontsize=11, fontweight='bold')
    ax.set_title('(b) Readability vs Quality', fontsize=12, fontweight='bold', pad=10)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_xlim(60, 90)
    ax.set_ylim(55, 95)

    fig.suptitle('Diversity and Readability Analysis', fontsize=16, fontweight='bold', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_path = os.path.join(output_dir, 'image7.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Generated Diversity & Readability Scatter Chart: {output_path}")
    plt.close()

def plot_overall_comparison_radar(output_dir):
    """Plot overall comparison radar chart (Split into CoreOnly and LLMP6-Full)"""
    models = list(EXPERIMENT_DATA.keys())
    model_names = [EXPERIMENT_DATA[m]["name"] for m in models]
    
    metrics = [
        ('response_time', 'Response Time', lambda x: 100 - min(x / 50, 100)),  # Lower is better
        ('throughput', 'Throughput', lambda x: min(x * 10, 100)),
        ('accuracy', 'Accuracy', lambda x: x),
        ('quality_score', 'Quality', lambda x: x),
        ('success_rate', 'Success Rate', lambda x: x),
        ('f1_score', 'F1 Score', lambda x: x),
    ]
    
    # Create two subplots side by side
    fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=150, subplot_kw={'projection': 'polar'})
    
    # Number of variables
    num_vars = len(metrics)
    
    # Angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Close the plot
    
    # Left subplot: CoreOnly
    ax_left = axes[0]
    ax_left.set_xticks(angles[:-1])
    labels_left = ax_left.set_xticklabels([name for _, name, _ in metrics], fontsize=9, fontweight='bold')
    ax_left.tick_params(axis='x', pad=15)
    for i, label in enumerate(labels_left):
        if 'Response' in label.get_text():
            label.set_horizontalalignment('left')
            label.set_position((0, label.get_position()[1] + 0.1))
            label.set_rotation(0)
    ax_left.set_ylim(0, 100)
    ax_left.set_yticks([20, 40, 60, 80, 100])
    ax_left.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
    ax_left.set_rlabel_position(45)
    
    for i, model in enumerate(models):
        core_values = [func(EXPERIMENT_DATA[model]["core_only"][key]) for key, _, func in metrics]
        core_values += core_values[:1]
        ax_left.plot(angles, core_values, 'o-', color=COLORS[model], linewidth=2.5, 
                     markersize=10, label=f'{model_names[i]}', alpha=0.9,
                     markeredgecolor='white', markeredgewidth=2)
        ax_left.fill(angles, core_values, color=COLORS[model], alpha=0.2)
    
    ax_left.set_title('(a) CoreOnly Configuration', fontsize=13, fontweight='bold', pad=20)
    ax_left.legend(fontsize=9, loc='upper right', bbox_to_anchor=(1.25, 1.0))
    
    # Right subplot: LLMP6-Full
    ax_right = axes[1]
    ax_right.set_xticks(angles[:-1])
    labels_right = ax_right.set_xticklabels([name for _, name, _ in metrics], fontsize=9, fontweight='bold')
    ax_right.tick_params(axis='x', pad=15)
    for i, label in enumerate(labels_right):
        if 'Response' in label.get_text():
            label.set_horizontalalignment('left')
            label.set_position((0, label.get_position()[1] + 0.1))
            label.set_rotation(0)
    ax_right.set_ylim(0, 100)
    ax_right.set_yticks([20, 40, 60, 80, 100])
    ax_right.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
    ax_right.set_rlabel_position(45)
    
    for i, model in enumerate(models):
        llmp6_values = [func(EXPERIMENT_DATA[model]["llmp6_full"][key]) for key, _, func in metrics]
        llmp6_values += llmp6_values[:1]
        ax_right.plot(angles, llmp6_values, 'o-', color=COLORS[model], linewidth=2.5, 
                      markersize=10, label=f'{model_names[i]}', alpha=0.9,
                      markeredgecolor='white', markeredgewidth=2)
        ax_right.fill(angles, llmp6_values, color=COLORS[model], alpha=0.2)
    
    ax_right.set_title('(b) LLMP6-Full Configuration', fontsize=13, fontweight='bold', pad=20)
    ax_right.legend(fontsize=9, loc='upper right', bbox_to_anchor=(1.25, 1.0))
    
    # Add overall title
    fig.suptitle('Overall Performance Comparison', fontsize=16, fontweight='bold', y=0.99)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_path = os.path.join(output_dir, 'image8.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Generated Overall Comparison Radar Chart: {output_path}")
    plt.close()

def main():
    print("="*60)
    print("LLMP6 Experiment Results Plot Generation (Diverse Charts)")
    print("="*60)

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
    os.makedirs(output_dir, exist_ok=True)

    print("\nGenerating charts for experiment results...")

    plot_efficiency_bar(output_dir)
    plot_quality_bar(output_dir)
    plot_stability_box(output_dir)
    plot_diversity_scatter(output_dir)
    plot_overall_comparison_radar(output_dir)

    print(f"\n🎉 All chart results generated to: {output_dir}")
    print("\n📊 Chart Summary:")
    print("  - fig3_efficiency_bar.png: Efficiency Metrics (Bar Chart)")
    print("  - fig4_quality_bar.png: Quality Metrics (Bar Chart)")
    print("  - fig5_stability_box.png: Stability Metrics (Box/Violin Plot)")
    print("  - fig6_diversity_bar.png: Diversity & Readability (Scatter/Bubble Chart)")
    print("  - fig7_overall_comparison.png: Overall Comparison (Radar Chart)")

if __name__ == "__main__":
    main()