<span id="english"></span>
<div align="center">
 
# 🚀 LLMP6: A Six-Layer Composable Architecture for Large Language Model Applications
 
**Yangxiu Liu**

🏢 *Beijing Esoul AI Information Technology Company Limited (esoul AI)*

📧 liuyangxiu@esoulai.com
 
<a href="#english">🇺🇸 English</a> &nbsp;|&nbsp; <a href="#chinese">🇨🇳 中文</a>
 
</div>

## 📖 1. Introduction

LLMP6 is a six-layer composable architecture for large language model applications, consisting of six layers: Assign, Core, Tool, Filter, Check, and Show. User input is processed through the Assign layer for distribution, then sequentially passes through the remaining five layers to produce the final output.

The Core layer calls the API of existing foundation large language models, while the remaining five layers can be implemented using lightweight specialized small models or engineering logic. When these five small models become excellent after sufficient training and validation, they can be merged into the foundation large model of the Core layer, enabling orderly iteration and continuous optimization of the foundation model.

The advantage of this layered design lies in independent development and flexible combination. Small and medium-sized teams only need to train five specialized small models without bearing the training costs of the foundation large model. At the same time, they can freely combine different specialized small models to refine the output results of the foundation model.

This project has published a preprint on Zenodo and is currently under review for SCI journal submission. DOI: 10.5281/ZENODO.20408749. Link: 📄 [LLMP6: A six-layer composable architecture for large language model applications](https://zenodo.org/records/20408749)

| Layer | Function |
|-------|----------|
| **Assign** | Parse user intent, generate/modify prompts |
| **Core** | Generate initial content using foundation large model |
| **Tool** | Execute tool/agent calls |
| **Filter** | Fact-check, filter incorrect information |
| **Check** | Goal achievement check, compliance check |
| **Show** | Format conversion, tone adjustment |

## 📁 2. Project Structure

```
llmp6/
├── llmp6_sotware/ # Software
│ ├── config.py
│ ├── pipeline.py
│ ├── cli.py
│ └── README.md
├── experiments/   # Experimental code and results
│ ├── data/
│ ├── results/
│ ├── scripts/
│ └── README.md
└── README.md
```

## 📜 License

MIT License

---

<span id="chinese"></span>
<div align="center">
 
# 🚀 LLMP6: 一种面向大型语言模型应用的六层可组合架构
 
**刘洋秀**
 
🏢 *北京虚灵创生信息科技有限公司（esoul AI）*
 
📧 liuyangxiu@esoulai.com

<a href="#english">🇺🇸 English</a> &nbsp;|&nbsp; <a href="#chinese">🇨🇳 中文</a>
 
</div>
 
## 📖 1. 简介

LLMP6 是一种面向大型语言模型应用的六层可组合架构，分别为：assign、core、tool、filter、check、show，用户输入内容通过 assign 进行分配，依次通过其余 5 层模型后得到最后的输出结果。

其中 Core 层调用现有基座大模型的 API，其余五层均可由轻量级专业小模型或工程逻辑实现。当五层小模型经过充分训练和验证变得优秀后，可以合并入 Core 层的基座大模型，实现基座大模型的有序迭代和持续优化。

这种分层设计的优势在于独立开发和自由搭配。中小团队只需训练五个专业小模型，无需承担基座大模型的训练成本，同时可以自由搭配不同的专业小模型，完善基座大模型的输出结果。

本项目已经在 Zenodo 发表预印本，并且正在进行 SCI 期刊投稿。DOI：10.5281/ZENODO.20408749，网址：📄 [LLMP6: A six-layer composable architecture for large language model applications](https://zenodo.org/records/20408749)

| 架构 | 功能 |
|------|------|
| **Assign** | 解析用户意图，生成/修改提示语 |
| **Core** | 基座大模型生成初始内容 |
| **Tool** | 执行工具 agent 调用 |
| **Filter** | 事实核查，过滤错误信息 |
| **Check** | 目标达成检查、合规检查 |
| **Show** | 格式转换，语气调整 |

## 📁 2. 目录结构

```
llmp6/
├── llmp6_sotware/ # 软件
│ ├── config.py
│ ├── pipeline.py
│ ├── cli.py
│ └── README.md
├── experiments/ # 实验结果和代码
│ ├── data/
│ ├── results/
│ ├── scripts/
│ └── README.md
└── README.md
```

## 📜 许可证

MIT License
