# LLMP6: 六层可组合大语言模型架构

一种面向大型语言模型应用的六层可组合架构，支持灵活配置每层的模型和执行方式。

## 架构概述

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

## 核心特性

- **灵活配置**：每层可独立选择不同模型
- **并集执行**：多个模型并行执行，结果合并
- **交集执行**：多个模型串行执行，层层过滤
- **自动重试**：Check失败时自动返回Core层重生成
- **知识库增强**：Filter层可使用外部知识库

## 快速开始

### 安装依赖

```bash
pip install requests pyyaml
```

### 配置模型

复制并修改示例配置文件：

```bash
cp models.yaml.example models.yaml
```

编辑 `models.yaml`，填入你的 API Key：

```yaml
models:
  deepseek:
    type: api
    url: https://api.deepseek.com/v1/chat/completions
    key: YOUR_API_KEY
    model: deepseek-chat
```

### 基本使用

#### 方式一：命令行

```bash
# 最简单的使用（仅Core层）
python3 run.py --core-model deepseek --prompt "你好"

# 完整使用（包含Filter、Check、Show层）
python3 run.py \
    --core-model deepseek \
    --filter-model deepseek phi3 \
    --check-model deepseek \
    --show-model deepseek \
    --database database.json \
    --rules rules.json \
    --prompt "北京今天天气怎么样？"
```

#### 方式二：Python API

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
print(result["final_output"])
```

## 执行模式

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

## 配置文件格式

### models.yaml

```yaml
models:
  deepseek:
    type: api
    url: https://api.deepseek.com/v1/chat/completions
    key: YOUR_API_KEY
    model: deepseek-chat
  phi3:
    type: api
    url: http://localhost:11434/api/chat
    model: phi3
```

### database.json

```json
{
  "facts": [
    "水的沸点是100摄氏度",
    "法国的首都是巴黎",
    "中国的首都是北京"
  ]
}
```

### rules.json

```json
{
  "rules": [
    "不得讨论中国领导人及其家属的负面信息",
    "不得传播未经证实的信息"
  ],
  "banned_keywords": [
    "台独",
    "港独",
    "暴力",
    "色情"
  ]
}
```

## 命令行参数

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

## 项目结构

```
llmp6/
├── llmp6/
│   ├── __init__.py      # 包入口
│   ├── config.py        # 配置类
│   ├── pipeline.py      # 核心管道实现
│   └── cli.py           # 命令行工具
├── run.py               # 主入口脚本
├── models.yaml.example  # 示例模型配置
├── database.json        # 知识库文件
├── rules.json           # 规则文件
└── README.md            # 项目说明
```

## 实验结果

LLMP6-Full配置下：

| 指标 | DeepSeek | Kimi |
|-----|---------|------|
| 响应时间降低 | 44.7% | 17.2% |
| 吞吐量提升 | 86.2% | 21.4% |
| P99延迟降低 | 77.4% | 51.0% |
| 变异系数降低 | 64.3% | 38.3% |
| F1分数提升 | +2.2个百分点 | +1.3个百分点 |

## 引用

```
刘洋秀. LLMP6: 一种面向大型语言模型应用的六层可组合架构[EB/OL]. https://github.com/esoulai/llmp6, 2024.
```

## 许可证

MIT License
