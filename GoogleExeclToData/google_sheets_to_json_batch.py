#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import argparse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from pathlib import Path

def setup_credentials(creds_file):
    """设置Google Sheets API凭证"""
    # 定义访问Google Sheets所需的权限范围
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    try:
        # 使用凭证文件授权
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"凭证设置错误: {e}")
        return None

def get_sheet_data(client, spreadsheet_id, sheet_name=None):
    """获取Google表格数据"""
    try:
        # 打开表格
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        # 选择工作表
        if sheet_name:
            worksheet = spreadsheet.worksheet(sheet_name)
        else:
            worksheet = spreadsheet.sheet1
        
        # 获取所有数据
        data = worksheet.get_all_records()
        return data
    except Exception as e:
        print(f"获取表格数据错误: {e}")
        return None

def export_to_json(data, output_file, format_type="list", key_field=None):
    """将数据导出为JSON文件"""
    if not data:
        print("没有数据可导出")
        return False
    
    # 确保输出目录存在
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    
    # 根据格式类型处理数据
    if format_type == "list":
        # 列表对象格式 - 默认
        json_data = data
    elif format_type == "nested":
        # 嵌套对象格式
        if not key_field or key_field not in data[0].keys():
            print(f"错误: 字段 '{key_field}' 不存在或未指定")
            return False
        
        json_data = {}
        for item in data:
            key = item.pop(key_field)
            json_data[key] = item
    else:
        print(f"不支持的格式类型: {format_type}")
        return False
    
    # 写入JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    return True

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='从Google Sheets导出数据到JSON文件')
    parser.add_argument('--sheet_id', required=True, help='Google表格ID')
    parser.add_argument('--output', required=True, help='输出JSON文件路径')
    parser.add_argument('--credentials', required=True, help='Google API凭证JSON文件路径')
    parser.add_argument('--format', choices=['list', 'nested'], default='list', help='JSON格式类型: list或nested')
    parser.add_argument('--key_field', help='嵌套格式的主键字段名')
    parser.add_argument('--sheet_name', help='工作表名称(默认为第一个工作表)')
    
    args = parser.parse_args()
    
    # 检查参数
    if args.format == 'nested' and not args.key_field:
        print("错误: 嵌套格式需要指定--key_field参数")
        return 1
    
    # 设置凭证
    client = setup_credentials(args.credentials)
    if not client:
        return 1
    
    # 获取表格数据
    data = get_sheet_data(client, args.sheet_id, args.sheet_name)
    if not data:
        return 1
    
    # 导出数据
    success = export_to_json(data, args.output, args.format, args.key_field)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 