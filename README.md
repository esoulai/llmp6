<div align="center">
 
# 🚀 LLMP6: A six-layer composable architecture for large language model applications

**Yangxiu Liu**
 
*Beijing Esoul AI Information Technology Company Limited*
 
📧 liuyangxiu@esoulai.com

<br>
<a href="README.zh-CN.md">🇨🇳 中文</a> &nbsp;|&nbsp; <a href="README.md">🇺🇸 English</a>
 
---
</div>
 
## 📖 1.Introduction
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

 

## 📁 2.Contents
 
```
llmp6/
├── llmp6_sotware/    # software
│   ├── config.py       
│   ├── pipeline.py    
│   ├── cli.py          
│   └── README.md       
│──experiments/       # Experimental code and results  
│   ├── data/           
│   ├── results/
│   ├── scripts/            
│   └── README.md
└──README.md
```
 
## 📜 License
 
MIT License
