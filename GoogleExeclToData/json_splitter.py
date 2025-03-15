#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import argparse
import sys
from pathlib import Path

# 设置控制台输出编码为UTF-8
if sys.platform == 'win32':
    # 使用更安全的方式设置编码
    try:
        import codecs
        # 检查sys.stdout是否已经是TextIOWrapper
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception as e:
        print(f"设置控制台编码时出错: {e}")

def split_json_file(input_file):
    """
    将JSON文件按照顶级键拆分成多个子文件
    
    Args:
        input_file (str): 输入JSON文件的路径
    
    Returns:
        bool: 操作是否成功
    """
    try:
        # 获取输入文件的绝对路径
        input_path = Path(input_file).resolve()
        
        # 检查文件是否存在
        if not input_path.exists():
            print(f"错误: 文件 '{input_file}' 不存在")
            return False
        
        # 读取JSON文件
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查数据是否为字典
        if not isinstance(data, dict):
            print(f"错误: 文件 '{input_file}' 不是有效的JSON对象")
            return False
        
        # 创建输出目录
        # 输出目录是输入文件的父目录的父目录下的export文件夹
        output_dir = input_path.parent.parent / 'export'
        output_dir.mkdir(exist_ok=True)
        
        # 拆分JSON文件
        for key, value in data.items():
            # 创建输出文件路径
            output_file = output_dir / f"{key}.json"
            
            # 将数据写入输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(value, f, ensure_ascii=False, indent=2)
            
            print(f"已创建文件: {output_file}")
        
        return True
    
    except Exception as e:
        print(f"拆分JSON文件时出错: {e}")
        return False

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='将JSON文件按顶级键拆分成多个子文件')
    parser.add_argument('--input', required=True, help='输入JSON文件路径')
    
    # 如果没有参数，但有位置参数，则将第一个位置参数作为输入文件
    if len(sys.argv) == 2 and not sys.argv[1].startswith('--'):
        args = parser.parse_args(['--input', sys.argv[1]])
    else:
        args = parser.parse_args()
    
    # 拆分JSON文件
    print(f"正在拆分JSON文件: {args.input}")
    success = split_json_file(args.input)
    
    if success:
        print("拆分JSON文件成功")
        return 0
    else:
        print("拆分JSON文件失败")
        return 1

if __name__ == "__main__":
    exit(main()) 