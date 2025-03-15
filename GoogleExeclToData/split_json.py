#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from pathlib import Path
from json_splitter import split_json_file

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

def main():
    """
    主函数 - 用于直接拆分JSON文件
    """
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