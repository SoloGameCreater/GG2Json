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

def generate_config_manager(output_dir, table_name, sheet_names):
    """
    生成ConfigManager类文件
    
    Args:
        output_dir (Path): 输出目录路径
        table_name (str): 表格名称
        sheet_names (list): 工作表名称列表
    
    Returns:
        bool: 是否成功
    """
    try:
        # 读取模板文件
        template_file = Path("Template/ConfigManagerSplit.template")
        if not template_file.exists():
            print(f"错误: 模板文件 '{template_file}' 不存在")
            return False
            
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 准备数据
        manager_class_name = f"{table_name}ConfigManager"
        
        # 准备字段数组
        field_array = []
        for sheet_name in sheet_names:
            field_array.append({
                'configClassName': sheet_name,
                'lowersheetname': sheet_name.lower()
            })
        
        # 创建结果字符串
        result = template
        
        # 1. 替换命名空间和类名
        result = result.replace("{{this.nameSpace}}", table_name)
        result = result.replace("{{{this.managerClassName}}}", manager_class_name)
        result = result.replace("{{{this.jsonPath}}}", f"Config/{table_name}")
        
        # 2. 移除子类型相关的部分
        result = re.sub(r'{{#each subTypeArray}}.*?{{/each}}', '', result, flags=re.DOTALL)
        
        # 3. 处理配置属性
        config_props = []
        for field in field_array:
            config_props.append(f"public List<{field['configClassName']}> {field['configClassName']}List => getConfig<{field['configClassName']}>();")
        config_props_str = "\n        ".join(config_props)
        
        # 替换配置属性部分
        result = re.sub(r'{{#each fieldArray}}public {{#isSingleTable this\.configClassName}}.*?{{/isSingleTable}}\n        {{/each}}', 
                        config_props_str + "\n        ", result, flags=re.DOTALL)
        
        # 4. 处理私有字段列表
        private_lists = []
        for field in field_array:
            private_lists.append(f"private List<{field['configClassName']}> {field['lowersheetname']}List;")
        private_lists_str = "\n        ".join(private_lists)
        
        # 替换私有字段列表部分
        result = re.sub(r'{{#each fieldArray}}private List<{{{this\.configClassName}}}> {{{this\.lowersheetname}}}List;\n        {{/each}}', 
                        private_lists_str + "\n        ", result, flags=re.DOTALL)
        
        # 5. 处理类型字典
        type_dict_entries = []
        for i, field in enumerate(field_array):
            entry = f"[typeof({field['configClassName']})] = \"{field['lowersheetname']}\""
            if i < len(field_array) - 1:
                entry += ","
            type_dict_entries.append(entry)
        type_dict_str = "\n            ".join(type_dict_entries)
        
        # 替换类型字典部分
        result = re.sub(r'{{#each fieldArray}}\[typeof\({{{this\.configClassName}}}\)\] = "{{{this\.lowersheetname}}}",\n            {{/each}}', 
                        type_dict_str, result, flags=re.DOTALL)
        
        # 6. 处理tryLoad方法中的case语句
        try_load_cases = []
        for field in field_array:
            try_load_cases.append(f"case \"{field['lowersheetname']}\": if ({field['lowersheetname']}List != null) return; break;")
        try_load_cases_str = "\n                ".join(try_load_cases)
        
        # 替换tryLoad方法中的case语句部分
        result = re.sub(r'{{#each fieldArray}}case "{{{this\.lowersheetname}}}": if \({{{this\.lowersheetname}}}List != null\) return; break;\n                {{/each}}', 
                        try_load_cases_str, result, flags=re.DOTALL)
        
        # 7. 处理tryLoad方法中的switch语句
        switch_cases = []
        for field in field_array:
            switch_cases.append(f"case \"{field['lowersheetname']}\": {field['lowersheetname']}List = JsonConvert.DeserializeObject<List<{field['configClassName']}>>(ta.text); break;")
        switch_cases_str = "\n                ".join(switch_cases)
        
        # 替换tryLoad方法中的switch语句部分
        result = re.sub(r'{{#each fieldArray}}case "{{{this\.lowersheetname}}}": {{{this\.lowersheetname}}}List = JsonConvert\.DeserializeObject<List<{{{this\.configClassName}}}>>\(ta\.text\); break;\n                {{/each}}', 
                        switch_cases_str, result, flags=re.DOTALL)
        
        # 8. 处理getConfig方法中的switch语句
        get_config_cases = []
        for field in field_array:
            get_config_cases.append(f"case \"{field['lowersheetname']}\": return {field['lowersheetname']}List as List<T>;")
        get_config_cases_str = "\n                ".join(get_config_cases)
        
        # 替换getConfig方法中的switch语句部分
        result = re.sub(r'{{#each fieldArray}}case "{{{this\.lowersheetname}}}": return {{{this\.lowersheetname}}}List as List<T>;\n                {{/each}}', 
                        get_config_cases_str, result, flags=re.DOTALL)
        
        # 9. 清理多余的空行
        result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
        
        # 写入输出文件
        output_file = output_dir / f"{manager_class_name}.Loader.cs"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"已生成ConfigManager文件: {output_file}")
        return True
        
    except Exception as e:
        print(f"生成ConfigManager文件时出错: {e}")
        return False

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
        
        # 收集所有工作表名称
        sheet_names = []
        
        # 清空export目录中的现有文件
        for file in output_path.glob("*.json"):
            try:
                file.unlink()
                print(f"已删除文件: {file}")
            except Exception as e:
                print(f"删除文件 {file} 时出错: {e}")
        
        # 拆分JSON文件
        for key, value in data.items():
            # 添加工作表名称
            sheet_names.append(key)
            
            # 处理数据，忽略note类型字段和空值
            if isinstance(value, list) and len(value) >= 2:
                # 第一个元素包含字段类型
                field_types = value[0]
                
                # 过滤字段类型，移除note字段
                filtered_field_types = {}
                for field_name, field_type in field_types.items():
                    if field_type != 'note':
                        filtered_field_types[field_name] = field_type
                
                # 只保留数据行，不包含字段类型和字段描述
                filtered_data = []
                
                # 处理所有数据行（从第三个元素开始，即索引为2）
                for i in range(2, len(value)):
                    row = value[i]
                    filtered_row = {}
                    
                    for field_name, field_value in row.items():
                        # 忽略类型为note的字段
                        if field_name in field_types and field_types[field_name] == 'note':
                            continue
                        
                        # 忽略不在过滤后的字段类型中的字段
                        if field_name not in filtered_field_types:
                            continue
                        
                        # 忽略空值字段
                        if field_value is None or field_value == "":
                            continue
                        
                        # 根据第一行定义的字段类型进行类型转换
                        if field_name in field_types:
                            field_type = field_types[field_name]
                            
                            # 字符串类型转换
                            if field_type == 'string' and not isinstance(field_value, str):
                                field_value = str(field_value)
                            
                            # 数字类型转换
                            elif field_type == 'number' and isinstance(field_value, str):
                                try:
                                    if '.' in field_value:
                                        field_value = float(field_value)
                                    else:
                                        field_value = int(field_value)
                                except ValueError:
                                    # 如果转换失败，保留原始值
                                    pass
                            
                            # 布尔类型转换
                            elif field_type == 'bool':
                                if isinstance(field_value, str):
                                    if field_value.lower() in ('true', '1'):
                                        field_value = True
                                    elif field_value.lower() in ('false', '0'):
                                        field_value = False
                                elif isinstance(field_value, (int, float)):
                                    field_value = bool(field_value)
                            
                            # 数组类型转换
                            elif field_type == 'arraynumber' and isinstance(field_value, str):
                                try:
                                    # 尝试将逗号分隔的字符串转换为数字列表
                                    if ',' in field_value:
                                        field_value = [int(x.strip()) if x.strip().isdigit() else float(x.strip()) for x in field_value.split(',') if x.strip()]
                                except ValueError:
                                    # 如果转换失败，保留原始值
                                    pass
                            
                            # 浮点数类型转换
                            elif field_type == 'float':
                                if isinstance(field_value, str):
                                    try:
                                        field_value = float(field_value)
                                    except ValueError:
                                        # 如果转换失败，保留原始值
                                        pass
                                elif isinstance(field_value, int):
                                    field_value = float(field_value)
                        
                        filtered_row[field_name] = field_value
                    
                    filtered_data.append(filtered_row)
                
                # 更新处理后的数据
                value = filtered_data
            
            # 创建输出文件路径（使用小写的工作表名称）
            lowercase_key = key.lower()
            output_file = output_path / f"{lowercase_key}.json"
            
            # 将数据写入输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(value, f, ensure_ascii=False, indent=2)
            
            print(f"已创建文件: {output_file}")
            
            # 为C#代码生成保存原始的字段类型和描述
            if isinstance(value, list) and len(value) >= 2:
                # 获取原始数据中的字段类型和描述
                original_field_types = data[key][0]
                original_field_descs = data[key][1] if len(data[key]) > 1 else {}
                
                # 准备字段数据
                fields_data = {}
                for field_name, field_type in original_field_types.items():
                    fields_data[field_name] = {
                        'type': field_type,
                        'desc': original_field_descs.get(field_name, "")
                    }
                
                # 生成对应的C#代码文件
                generate_cs_file(
                    Path("Template/Config.template"),
                    codegen_dir,
                    key,  # 类名
                    table_name,  # 命名空间
                    fields_data
                )
        
        # 生成ConfigManager类文件
        generate_config_manager(codegen_dir, table_name, sheet_names)
        
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