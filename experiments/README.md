# LLMP6 实验套件

本目录包含 LLMP6 六层可组合架构的完整实验数据和测试代码。

---

## 🎯 实验目的

验证 LLMP6 架构的性能提升效果：

- **对比两种配置**：CoreOnly（仅基座模型） vs LLMP6-Full（完整六层架构）
- **测试三个模型**：DeepSeek、Qwen、Kimi
- **评估三类指标**：
  - ⚡ 效率：响应时间、吞吐量、P95/P99延迟
  - 📈 质量：准确率、F1分数、质量分数
  - 🛡️ 稳定性：抖动、变异系数、成功率

---

## 📁 目录结构

```
experiments/
├── data/                    # 测试数据集
│   ├── csqa2_experiment_data.json       # 原始CSQA2问答数据
│   └── csqa2_experiment_data_grouped.json  # 分组后数据（10组×100条）
├── results/                 # 实验结果输出
│   ├── comprehensive_test_results.json   # 综合统计指标
│   ├── raw_test_results.json             # 原始测试结果
│   ├── deepseek_coreonly.json            # DeepSeek CoreOnly结果
│   ├── deepseek_full.json                # DeepSeek LLMP6-Full结果
│   ├── qwen_coreonly.json                # Qwen CoreOnly结果
│   ├── qwen_full.json                    # Qwen LLMP6-Full结果
│   ├── kimi_coreonly.json                # Kimi CoreOnly结果
│   ├── kimi_full.json                    # Kimi LLMP6-Full结果
│   └── *.png                             # 可视化图表
└── scripts/                 # 测试脚本
    ├── run_experiment.py                # 一键运行完整实验（整合版）
    ├── create_grouped_data.py           # 创建分组数据
    ├── run_test_deepseek_coreonly.py    # DeepSeek CoreOnly测试
    ├── run_test_deepseek_full.py        # DeepSeek LLMP6-Full测试
    ├── run_test_qwen_coreonly.py        # Qwen CoreOnly测试
    ├── run_test_qwen_full.py            # Qwen LLMP6-Full测试
    ├── run_test_kimi_coreonly.py        # Kimi CoreOnly测试
    ├── run_test_kimi_full.py            # Kimi LLMP6-Full测试
    ├── compute_metrics.py               # 计算统计指标
    ├── plot_results.py                  # 生成可视化图表
    ├── plot_architecture_diagrams.py    # 生成架构图
    └── test_utils.py                    # 工具函数模块
```

---

## 🚀 运行方式

### 方法一：一键运行（推荐）

```bash
# 进入脚本目录
cd experiments/scripts

# 运行完整实验（调用外部API，会产生费用）
python3 run_experiment.py

# 生成可视化图表
python3 plot_results.py
```

### 方法二：分步运行（适合调试）

```bash
# 1. 创建分组数据（仅需运行一次）
python3 create_grouped_data.py

# 2. 运行各个模型测试（可单独运行）
python3 run_test_deepseek_coreonly.py
python3 run_test_deepseek_full.py
python3 run_test_qwen_coreonly.py
python3 run_test_qwen_full.py
python3 run_test_kimi_coreonly.py
python3 run_test_kimi_full.py

# 3. 计算统计指标
python3 compute_metrics.py

# 4. 生成图表
python3 plot_results.py
```

### 方法三：仅重新计算指标（无需API）

```bash
python3 compute_metrics.py
python3 plot_results.py
```

---

## 📊 输出结果

### 数据文件

| 文件 | 内容 |
|------|------|
| `results/comprehensive_test_results.json` | 综合统计指标（所有模型+配置） |
| `results/raw_test_results.json` | 原始测试结果（包含所有样本输出） |
| `results/*_coreonly.json` | 各模型CoreOnly配置测试结果 |
| `results/*_full.json` | 各模型LLMP6-Full配置测试结果 |

### 可视化图表

| 图表文件 | 内容 |
|----------|------|
| `results/image1.png` | LLMP6六层架构图 |
| `results/image2.png` | 执行模式示意图（并集/交集） |
| `results/image3.png` | 实验流程图 |
| `results/image4.png` | 效率指标对比柱状图 |
| `results/image5.png` | 质量指标对比柱状图 |
| `results/image6.png` | 稳定性指标箱线图 |
| `results/image7.png` | 多样性与可读性分析图 |
| `results/image8.png` | 综合性能雷达图 |

---

## 📈 预期结果

LLMP6-Full 相比 CoreOnly 的预期提升：

| 指标 | 预期变化 |
|------|----------|
| 准确率 | ↑ 8-15% |
| F1分数 | ↑ 5-12% |
| 质量分数 | ↑ 10-18% |
| 响应时间 | ↑ 20-40%（因增加多层处理） |
| 吞吐量 | ↓ 10-20% |
| 稳定性 | ↑ 显著提升 |

---

## 📦 依赖安装

```bash
pip install requests pyyaml matplotlib seaborn numpy pandas
```

---

## ⚠️ 注意事项

1. **API费用**：`run_experiment.py` 和各 `run_test_*.py` 脚本会调用 DeepSeek、Qwen、Kimi 的云API，会产生费用
2. **数据备份**：`raw_test_results.json` 包含所有样本的原始输出，用于后续分析，请妥善保存
3. **Ollama模型**：运行 LLMP6-Full 测试前需确保已安装所需的Ollama模型：
   ```bash
   ollama pull llama3.2:3b
   ollama pull sam860/lucy:1.7b
   ollama pull bespoke-minicheck
   ollama pull llama-guard3:1b
   ollama pull OmniNode/Orion:V1.3
   ```
4. **运行时间**：完整实验约需1-2小时（取决于API响应速度和网络状况）
5. **配置检查**：确保 `scripts/test_utils.py` 中的API密钥配置正确

---

## 🔬 实验流程

```
┌─────────────────────────────────────────────────────────────┐
│                    LLMP6 实验流程                           │
├─────────────────────────────────────────────────────────────┤
│  1. create_grouped_data.py                                 │
│     └── 将1000条问答分成10组，每组100条                     │
│                                                            │
│  2. run_test_*.py (x6) 或 run_experiment.py               │
│     └── 分别测试3个模型 × 2种配置 = 6组实验                  │
│                                                            │
│  3. compute_metrics.py                                     │
│     └── 计算准确率、F1、响应时间、吞吐量等指标                │
│                                                            │
│  4. plot_results.py                                        │
│     └── 生成柱状图、雷达图、箱线图等可视化图表                │
└─────────────────────────────────────────────────────────────┘
```