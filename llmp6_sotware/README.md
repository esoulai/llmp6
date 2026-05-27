# LLMP6：六层可组合大语言模型架构

一种面向大型语言模型应用的六层可组合架构，支持灵活配置每层的模型和执行方式。

---

## 📐 架构概述

```
用户输入 → Assign → Core → Filter → Tool → Check → Show → 用户输出
              |                                    |
              └→ 解析用户意图，自动配置提示语       └→ 检查失败，返回Core重生成
```

### 各层职责

| 层级 | 职责 | 数据来源 | 说明 |
|-----|------|---------|------|
| **Assign** | 解析用户意图，生成/修改其他模型的提示语 | 无 | 用户输入 |
| **Core** | 生成初始内容 | 无 | **必需**，基座大模型 |
| **Filter** | 事实核查，过滤错误信息 | `database.json` | 支持并集/交集执行 |
| **Tool** | 执行工具调用（Agent） | 外部API/对话Agent | 可选，支持并集/交集 |
| **Check** | 目标达成检查、合规检查 | `rules.json` | 支持并集/交集执行 |
| **Show** | 格式转换，语气调整 | 无 | 支持并集/交集执行 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests pyyaml
```

### 2. 配置模型

创建 `models.yaml` 文件：

```yaml
models:
  # 基座大模型（用于Core层）
  deepseek:
    type: api
    url: https://api.deepseek.com/v1/chat/completions
    key: YOUR_DEEPSEEK_API_KEY
    model: deepseek-chat
  
  qwen:
    type: api
    url: https://api.qwen.xfyun.cn/v1/chat/completions
    key: YOUR_QWEN_API_KEY
    model: qwen-max
  
  # 轻量级模型（用于其他层）
  phi3:
    type: api
    url: http://localhost:11434/api/chat
    model: phi3
```

### 3. 配置知识库（可选）

创建 `database.json` 文件（用于 Filter 层事实核查）：

```json
{
  "facts": [
    "水的沸点是100摄氏度",
    "法国的首都是巴黎",
    "中国的首都是北京"
  ]
}
```

### 4. 配置规则（可选）

创建 `rules.json` 文件（用于 Check 层合规检查）：

```json
{
  "rules": [
    "不得讨论中国领导人及其家属的负面信息",
    "不得传播未经证实的信息"
  ],
  "banned_keywords": ["台独", "港独", "暴力", "色情"]
}
```

---

## 🖥️ 命令行使用

### 基本用法

```bash
# 最简单的使用（仅Core层）
python -m llmp6 --core-model deepseek --prompt "你好"

# 完整使用（包含Filter、Check、Show层）
python -m llmp6 \
    --core-model deepseek \
    --filter-model deepseek phi3 \
    --check-model deepseek \
    --show-model deepseek \
    --database database.json \
    --rules rules.json \
    --prompt "北京今天天气怎么样？"
```

### 命令行参数

| 参数 | 说明 | 是否必需 |
|-----|------|---------|
| `--core-model` | Core层使用的模型名称 | **是** |
| `--assign-model` | Assign层使用的模型名称 | 否 |
| `--filter-model` | Filter层使用的模型（空格分隔为并集） | 否 |
| `--tool-model` | Tool层使用的模型（空格分隔为并集） | 否 |
| `--check-model` | Check层使用的模型（空格分隔为并集） | 否 |
| `--show-model` | Show层使用的模型（空格分隔为并集） | 否 |
| `--models` | 模型配置文件路径 | 否（默认 models.yaml） |
| `--database` | 知识库文件路径 | 否 |
| `--rules` | 规则文件路径 | 否 |
| `--prompt` | 用户输入 | **是** |
| `--json` | JSON格式输出 | 否 |

---

## 🐍 Python API 使用

### 基本示例

```python
from llmp6 import LLMP6Config, LLMP6Pipeline

# 创建配置
config = LLMP6Config(
    core_model="deepseek",
    filter_model=["deepseek", "phi3"],
    check_model=["deepseek"],
    show_model=["deepseek"],
    database_file="database.json",
    rules_file="rules.json"
)

# 创建管道
pipeline = LLMP6Pipeline(config)

# 执行
result = pipeline.run("北京今天天气怎么样？")

# 获取结果
print("最终输出:", result["final_output"])
print("总耗时:", result["total_time"], "秒")
print("重试次数:", result["retry_count"])
```

### 执行结果结构

```python
{
    "input": "用户输入内容",
    "layers": {
        "Assign": {"output": "...", "time": 0.5},
        "Core": {"output": "...", "time": 1.2},
        "Filter": {"output": "...", "time": 0.8},
        "Check": {"output": "...", "time": 0.3},
        "Show": {"output": "...", "time": 0.2}
    },
    "total_time": 3.0,
    "final_output": "最终回答内容",
    "retry_count": 0  # Check失败后的重试次数
}
```

---

## ⚡ 执行模式

### 并集执行（并行）

多个模型**同时并行执行**，结果合并：

```bash
--filter-model deepseek phi3 qwen
```

执行流程：`content → [Filter(deepseek) ∥ Filter(phi3) ∥ Filter(qwen)] → 结果合并`

### 交集执行（串行）

多个模型**依次串行执行**，前一个输出作为后一个输入：

```bash
--filter-model deepseek --filter-model phi3 --filter-model qwen
```

执行流程：`content → Filter(deepseek) → Filter(phi3) → Filter(qwen) → 输出`

### 单个执行

```bash
--filter-model deepseek
```

执行流程：`content → Filter(deepseek) → 输出`

---

## 📁 项目结构

```
llmp6/
├── __init__.py      # 包入口，导出核心类
├── config.py        # 配置类，管理模型和参数
├── pipeline.py      # 核心管道，实现六层执行逻辑
└── cli.py           # 命令行接口
```

---

## 🎯 核心特性

- **灵活配置**：每层可独立选择不同模型
- **并集执行**：多个模型并行执行，提高效率
- **交集执行**：多个模型串行执行，层层过滤
- **自动重试**：Check失败时自动返回Core层重生成
- **知识库增强**：Filter层可使用外部知识库
- **规则引擎**：Check层支持自定义规则和关键词过滤

---

## 📝 示例：完整对话流程

```python
from llmp6 import LLMP6Config, LLMP6Pipeline

# 配置：使用DeepSeek作为基座，Phi3做事实核查
config = LLMP6Config(
    core_model="deepseek",
    filter_model=["phi3"],
    check_model=["phi3"],
    show_model=["phi3"],
    database_file="database.json",
    rules_file="rules.json"
)

pipeline = LLMP6Pipeline(config)

# 对话示例
result = pipeline.run("请解释什么是人工智能？")
print(result["final_output"])
```

输出：
```
人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
旨在研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统。
人工智能领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
```

---

## 📚 引用

```
刘洋秀. LLMP6: 一种面向大型语言模型应用的六层可组合架构[EB/OL]. https://github.com/esoulai/llmp6, 2024.
```
