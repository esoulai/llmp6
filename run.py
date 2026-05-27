#!/usr/bin/env python3
"""
LLMP6 主入口脚本

使用方式：
    python3 run.py --core-model deepseek --prompt "你好"
    
完整示例：
    python3 run.py \
        --core-model deepseek \
        --filter-model deepseek phi3 \
        --check-model deepseek \
        --show-model deepseek \
        --database database.json \
        --rules rules.json \
        --prompt "北京今天天气怎么样？"
"""

from llmp6.cli import main

if __name__ == "__main__":
    main()
