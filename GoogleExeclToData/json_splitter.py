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

def ensure_codegen_dir(output_path, name):
    """
    确保输出目录下存在名为$name/GodeGen的文件夹
    
    Args:
        output_path (Path): 输出目录路径
        name (str): 表格名称
    
    Returns:
        Path: GodeGen文件夹路径
    """
    # 创建$name文件夹
    name_dir = output_path / name
    name_dir.mkdir(exist_ok=True, parents=True)
    
    # 创建$name/GodeGen文件夹
    codegen_dir = name_dir / "GodeGen"
    codegen_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"已确保目录存在: {codegen_dir}")
    return codegen_dir

def split_json_file(input_file, output_dir=None, output_script_dir=None):
    """
    将JSON文件按照顶级键拆分成多个子文件
    
    Args:
        input_file (str): 输入JSON文件的路径
        output_dir (str, optional): 输出目录的路径，如果为None，则使用默认路径
        output_script_dir (str, optional): 输出脚本目录的路径，如果为None，则使用默认路径
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
        if output_dir:
            output_path = input_path.parent.parent.parent.parent / output_dir
            output_script_path = input_path.parent.parent.parent.parent / output_script_dir
        else:
            # 否则，使用默认路径（输入文件的父目录的父目录下的export文件夹）
            output_path = input_path.parent.parent / 'export'
        
        # 确保输出目录存在
        output_path.mkdir(exist_ok=True, parents=True)
        
        # 获取表格名称（输入文件名，不包含扩展名）
        table_name = input_path.stem
        
        # 确保$name/GodeGen文件夹存在
        codegen_dir = ensure_codegen_dir(output_script_path, table_name)
        
        # 拆分JSON文件
        for key, value in data.items():
            # 创建输出文件路径
            output_file = output_path / f"{key}.json"
            
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
    parser.add_argument('--output-dir', help='输出目录路径，默认为输入文件的父目录的父目录下的export文件夹')
    parser.add_argument('--output-script-dir', help='输出脚本目录路径，默认为输入文件的父目录的父目录下的GodeGen文件夹')
    # 如果没有参数，但有位置参数，则将第一个位置参数作为输入文件
    if len(sys.argv) == 2 and not sys.argv[1].startswith('--'):
        args = parser.parse_args(['--input', sys.argv[1]])
    else:
        args = parser.parse_args()
    
    # 拆分JSON文件
    print(f"正在拆分JSON文件: {args.input}")
    success = split_json_file(args.input, args.output_dir, args.output_script_dir)
    
    if success:
        print("拆分JSON文件成功")
        return 0
    else:
        print("拆分JSON文件失败")
        return 1

if __name__ == "__main__":
    exit(main()) 