#!/usr/bin/env python3
"""
创建分组数据脚本：从csqa2_experiment_data.json抽取1000条问答并分组

分组策略：
- 总共1000条问答
- 分成10组，每组100条
- 保存为csqa2_experiment_data_grouped.json
"""

import os
import json

def create_grouped_data(input_path, output_path, group_size=100):
    """
    从输入文件读取数据并分组
    
    Args:
        input_path: 原始数据文件路径
        output_path: 分组数据输出路径
        group_size: 每组的数据条数，默认100
    """
    # 读取原始数据
    print(f"📖 正在读取数据文件: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_items = len(data)
    print(f"✅ 读取到 {total_items} 条数据")
    
    # 确保只取1000条
    if total_items > 1000:
        data = data[:1000]
        total_items = 1000
        print(f"📊 抽取前1000条数据")
    
    # 计算分组数
    num_groups = (total_items + group_size - 1) // group_size
    
    # 分组数据
    groups = []
    for i in range(0, total_items, group_size):
        group = data[i:i+group_size]
        groups.append(group)
    
    # 创建输出结构
    grouped_data = {
        "metadata": {
            "total_groups": len(groups),
            "total_items": total_items,
            "group_size": group_size,
            "created_at": os.path.getmtime(input_path),
            "source": os.path.basename(input_path)
        },
        "groups": groups
    }
    
    # 保存分组数据
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(grouped_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 分组数据已保存到: {output_path}")
    print(f"📈 分组结果：{len(groups)} 组，每组 {group_size} 条")
    print(f"📝 总数据条数：{total_items}")
    
    return grouped_data

def main():
    # 设置路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    data_dir = os.path.join(project_root, "experiments", "data")
    
    input_path = os.path.join(data_dir, "csqa2_experiment_data.json")
    output_path = os.path.join(data_dir, "csqa2_experiment_data_grouped.json")
    
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"❌ 错误：输入文件不存在: {input_path}")
        return
    
    # 创建分组数据
    create_grouped_data(input_path, output_path, group_size=100)

if __name__ == "__main__":
    main()
