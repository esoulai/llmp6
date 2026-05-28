<span id="english"></span>
<div align="center">

# 📊 LLMP6 Experiment Data

<a href="#english">🇺🇸 English</a> &nbsp;|&nbsp; <a href="#chinese">🇨🇳 中文</a>

</div>

## 📁 1. Directory

```
experiments/
├── data/                    # Test datasets
│   ├── csqa2_experiment_data.json       # Original CSQA2 QA data
│   └── csqa2_experiment_data_grouped.json  # Grouped data (10 groups × 100 items)
├── results/                 # Experiment result outputs
│   ├── comprehensive_test_results.json   # Comprehensive statistical metrics
│   ├── deepseek_coreonly.json            # DeepSeek CoreOnly results
│   ├── deepseek_full.json                # DeepSeek LLMP6-Full results
│   ├── qwen_coreonly.json                # Qwen CoreOnly results
│   ├── qwen_full.json                    # Qwen LLMP6-Full results
│   ├── kimi_coreonly.json                # Kimi CoreOnly results
│   ├── kimi_full.json                    # Kimi LLMP6-Full results
│   └── *.png                             # Visualization charts
└── scripts/                 # Test scripts
    ├── create_grouped_data.py           # Create grouped data
    ├── run_test_deepseek_coreonly.py    # DeepSeek CoreOnly test
    ├── run_test_deepseek_full.py        # DeepSeek LLMP6-Full test
    ├── run_test_qwen_coreonly.py        # Qwen CoreOnly test
    ├── run_test_qwen_full.py            # Qwen LLMP6-Full test
    ├── run_test_kimi_coreonly.py        # Kimi CoreOnly test
    ├── run_test_kimi_full.py            # Kimi LLMP6-Full test
    ├── compute_metrics.py               # Compute statistical metrics
    ├── plot_results.py                  # Generate visualization charts
    ├── plot_architecture_diagrams.py    # Generate architecture diagrams
    ├── models.yaml                      # Model configuration file
    ├── database.yaml                    # Fact verification database
    ├── rules.yaml                       # Compliance rules
    └── test_utils.py                    # Utility functions module
```

## 🚀 2. Running the Code

```bash
# 0. Draw architecture diagrams
python3 plot_architecture_diagrams.py

# 1. Create grouped data (only need to run once)
python3 create_grouped_data.py

# 2. Run individual model tests (can run separately)
python3 run_test_deepseek_coreonly.py
python3 run_test_deepseek_full.py
python3 run_test_qwen_coreonly.py
python3 run_test_qwen_full.py
python3 run_test_kimi_coreonly.py
python3 run_test_kimi_full.py

# 3. Compute statistical metrics
python3 compute_metrics.py

# 4. Generate result charts
python3 plot_results.py
```

## 📊 3. Output Results

| File | Content |
|------|---------|
| `results/comprehensive_test_results.json` | Comprehensive statistical metrics (all models + configurations) |
| `results/*_coreonly.json` | Each model's CoreOnly configuration test results |
| `results/*_full.json` | Each model's LLMP6-Full configuration test results |
| `results/*.png` | Result data visualization charts |

## ⚠️ 4. Notes

1. **API Costs**: Each `run_test_*.py` script will call the cloud APIs for DeepSeek, Qwen, and Kimi configured in `models.yaml`, which will incur costs
2. **Ollama Models**: Before running LLMP6-Full tests, ensure you have installed the required Ollama models:
   ```bash
   ollama pull phi3:mini
   ollama pull sam860/lucy:1.7b
   ollama pull bespoke-minicheck
   ollama pull llama-guard3:1b
   ollama pull OmniNode/Orion:V1.3
   ```
3. **Environment Configuration**: This repository only contains core result data and essential code. Running the code directly may require additional setup:
   - python: Python 3.8+ with dependencies: `pip install pyyaml json`
   - ollama: Ollama server running locally on port 11434
   - api: API keys configured in `models.yaml`
   - knowledge base: `database.yaml` and `rules.yaml`

---

<span id="chinese"></span>
<div align="center">

# 📊 LLMP6 实验数据

<a href="#english">🇺🇸 English</a> &nbsp;|&nbsp; <a href="#chinese">🇨🇳 中文</a>

</div>

## 📁 1. 目录结构

```
experiments/
├── data/                    # 测试数据集
│   ├── csqa2_experiment_data.json       # 原始CSQA2问答数据
│   └── csqa2_experiment_data_grouped.json  # 分组后数据（10组×100条）
├── results/                 # 实验结果输出
│   ├── comprehensive_test_results.json   # 综合统计指标
│   ├── deepseek_coreonly.json            # DeepSeek CoreOnly结果
│   ├── deepseek_full.json                # DeepSeek LLMP6-Full结果
│   ├── qwen_coreonly.json                # Qwen CoreOnly结果
│   ├── qwen_full.json                    # Qwen LLMP6-Full结果
│   ├── kimi_coreonly.json                # Kimi CoreOnly结果
│   ├── kimi_full.json                    # Kimi LLMP6-Full结果
│   └── *.png                             # 可视化图表
└── scripts/                 # 测试脚本
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
    ├── models.yaml                      # 模型配置文件
    ├── database.yaml                    # 事实核查知识库
    ├── rules.yaml                       # 合规规则
    └── test_utils.py                    # 工具函数模块
```

## 🚀 2. 代码运行

```bash
# 0. 绘制架构图片
python3 plot_architecture_diagrams.py

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

# 4. 生成结果图片
python3 plot_results.py
```

## 📊 3. 输出结果

| 文件 | 内容 |
|------|------|
| `results/comprehensive_test_results.json` | 综合统计指标（所有模型+配置） |
| `results/*_coreonly.json` | 各模型CoreOnly配置测试结果 |
| `results/*_full.json` | 各模型LLMP6-Full配置测试结果 |
| `results/*.png` | 结果数据可视化图表 |

## ⚠️ 4. 注意事项

1. **API费用**：各 `run_test_*.py` 脚本会调用 `models.yaml` 中配置的 DeepSeek、Qwen、Kimi 的云API，会产生费用
2. **Ollama模型**：运行 LLMP6-Full 测试前需确保已安装所需的Ollama模型：
   ```bash
   ollama pull phi3:mini
   ollama pull sam860/lucy:1.7b
   ollama pull bespoke-minicheck
   ollama pull llama-guard3:1b
   ollama pull OmniNode/Orion:V1.3
   ```
3. **环境配置**：本仓库只包含核心结果数据以及核心代码，直接运行本仓库代码会有困难，需要先配置好环境：
   - python：Python 3.8+ 及依赖库：`pip install pyyaml json`
   - ollama：运行 Ollama 服务
   - api：配置 `models.yaml` 中的 API 密钥
   - 知识库：配置`database.yaml` 和 `rules.yaml`
