#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import argparse
import sys
from pathlib import Path
import re

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

def convert_type_to_csharp(json_type):
    """
    将JSON类型转换为C#类型
    
    Args:
        json_type (str): JSON中的类型名称
    
    Returns:
        str: 对应的C#类型
    """
    type_mapping = {
        'number': 'int',
        'float': 'float',
        'string': 'string',
        'bool': 'bool',
        'arraynumber': 'List<int>',
        'arraystring': 'List<string>',
        'note': 'string',
    }
    
    return type_mapping.get(json_type, 'string')  # 默认返回string类型

def generate_cs_file(template_path, output_dir, class_name, name_space, fields_data):
    """
    生成C#代码文件
    
    Args:
        template_path (Path): 模板文件路径
        output_dir (Path): 输出目录路径
        class_name (str): 类名
        name_space (str): 命名空间
        fields_data (list): 字段数据列表
    
    Returns:
        bool: 是否成功
    """
    try:
        # 读取模板文件
        template_file = Path("Template/Config.template")
        if not template_file.exists():
            print(f"错误: 模板文件 '{template_file}' 不存在")
            return False
            
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 准备字段数组
        field_array = []
        for field_name, field_info in fields_data.items():
            # 忽略类型为"note"的字段
            if field_info['type'] == 'note':
                continue
                
            field_data = {
                'getterName': field_name[0].upper() + field_name[1:],
                'realType': convert_type_to_csharp(field_info['type']),
                'desc': field_info['desc']
            }
            field_array.append(field_data)
        
        # 替换模板中的变量
        # 1. 替换类名和命名空间
        result = template.replace('{{className}}', class_name).replace('{{nameSpace}}', name_space)
        
        # 2. 处理字段循环
        fields_content = ""
        for field in field_array:
            # 处理描述中的换行符，确保注释格式正确
            desc = field['desc']
            if '\n' in desc:
                # 将换行符替换为注释格式
                desc_lines = desc.split('\n')
                formatted_desc = desc_lines[0]
                for line in desc_lines[1:]:
                    if line.strip():  # 忽略空行
                        formatted_desc += f"\n        /// {line}"
            else:
                formatted_desc = desc
                
            field_template = """        /// <summary>
        /// {{{desc}}}
        /// </summary>
        public {{{realType}}} {{getterName}} {{ get; set; }}
"""
            field_content = field_template.replace('{{{desc}}}', formatted_desc)
            field_content = field_content.replace('{{{realType}}}', field['realType'])
            field_content = field_content.replace('{{getterName}}', field['getterName'])
            fields_content += field_content
        
        # 替换字段循环部分
        each_pattern = re.compile(r'{{#each fieldArray}}(.*?){{/each}}', re.DOTALL)
        result = each_pattern.sub(fields_content, result)
        
        # 修复类定义的花括号和第一个注释在同一行的问题
        result = result.replace("{\n    {{#each", "{\n        {{#each")
        result = result.replace("{           ", "{\n        ")
        
        # 写入输出文件
        output_file = output_dir / f"{class_name}.cs"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"已生成C#代码文件: {output_file}")
        return True
        
    except Exception as e:
        print(f"生成C#代码文件时出错: {e}")
        return False

def split_json_file(input_file, output_dir=None, output_script_dir=None):
    """
    将JSON文件按照顶级键拆分成多个子文件，并生成对应的C#代码
    
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
            output_script_path = input_path.parent.parent
        
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
            
            # 检查value是否是列表且至少有两个元素
            if isinstance(value, list) and len(value) >= 2:
                # 第一个元素包含字段类型
                field_types = value[0]
                # 第二个元素包含字段描述
                field_descs = value[1]
                
                # 准备字段数据
                fields_data = {}
                for field_name, field_type in field_types.items():
                    fields_data[field_name] = {
                        'type': field_type,
                        'desc': field_descs.get(field_name, "")
                    }
                
                # 生成对应的C#代码文件
                generate_cs_file(
                    Path("Template/Config.template"),
                    codegen_dir,
                    key,  # 类名
                    table_name,  # 命名空间
                    fields_data
                )
        
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