"""
LLMP6 命令行工具

提供简洁的命令行接口来使用 LLMP6 架构
"""

import argparse
import json
from .config import LLMP6Config
from .pipeline import LLMP6Pipeline


def main():
    parser = argparse.ArgumentParser(
        description="LLMP6 - 六层可组合大语言模型架构",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # 模型配置
    parser.add_argument("--core-model", required=True, help="Core层使用的模型")
    parser.add_argument("--assign-model", help="Assign层使用的模型")
    parser.add_argument("--filter-model", nargs='+', help="Filter层使用的模型（空格分隔为并集）")
    parser.add_argument("--tool-model", nargs='+', help="Tool层使用的模型（空格分隔为并集）")
    parser.add_argument("--check-model", nargs='+', help="Check层使用的模型（空格分隔为并集）")
    parser.add_argument("--show-model", nargs='+', help="Show层使用的模型（空格分隔为并集）")
    
    # 配置文件
    parser.add_argument("--models", default="models.yaml", help="模型配置文件")
    parser.add_argument("--database", help="知识库文件（JSON格式）")
    parser.add_argument("--rules", help="规则文件（JSON格式）")
    
    # 输入输出
    parser.add_argument("--prompt", required=True, help="用户输入")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    
    args = parser.parse_args()
    
    # 创建配置
    config = LLMP6Config(
        core_model=args.core_model,
        assign_model=args.assign_model,
        filter_model=args.filter_model,
        tool_model=args.tool_model,
        check_model=args.check_model,
        show_model=args.show_model,
        models_file=args.models,
        database_file=args.database,
        rules_file=args.rules
    )
    
    # 创建管道并执行
    pipeline = LLMP6Pipeline(config)
    result = pipeline.run(args.prompt)
    
    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("LLMP6 执行结果")
        print("=" * 60)
        print(f"\n输入: {args.prompt}")
        print(f"\n{'='*60}")
        print("各层执行详情:")
        for layer, layer_result in result["layers"].items():
            print(f"\n  [{layer}]")
            print(f"    模型: {layer_result.get('models', [])}")
            print(f"    耗时: {layer_result.get('time', 0)}s")
            print(f"    模式: {layer_result.get('execution_mode', 'single')}")
        print(f"\n{'='*60}")
        print(f"总耗时: {result['total_time']}s")
        print(f"重试次数: {result['retry_count']}")
        print(f"\n最终输出:\n{result['final_output']}")


if __name__ == "__main__":
    main()
