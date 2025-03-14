#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from pathlib import Path

def setup_credentials():
    """设置Google Sheets API凭证"""
    # 定义访问Google Sheets所需的权限范围
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    # 获取凭证文件路径
    creds_file = input("请输入您的Google API凭证JSON文件路径: ")
    
    try:
        # 使用凭证文件授权
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"凭证设置错误: {e}")
        return None

def get_sheet_data(client):
    """获取Google表格数据"""
    # 获取表格信息
    spreadsheet_url = input("请输入Google表格的URL或ID: ")
    sheet_name = input("请输入工作表名称(默认为第一个工作表): ") or None
    
    try:
        # 打开表格
        if 'https://' in spreadsheet_url:
            spreadsheet = client.open_by_url(spreadsheet_url)
        else:
            spreadsheet = client.open_by_key(spreadsheet_url)
        
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

def export_to_json(data, format_type="list"):
    """将数据导出为JSON文件"""
    if not data:
        print("没有数据可导出")
        return
    
    # 创建输出目录
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 确定输出文件名
    output_file = output_dir / "google_sheet_data.json"
    
    # 根据格式类型处理数据
    if format_type == "list":
        # 列表对象格式 - 默认
        json_data = data
    elif format_type == "nested":
        # 嵌套对象格式
        key_field = input("请输入作为主键的字段名: ")
        if key_field not in data[0].keys():
            print(f"错误: 字段 '{key_field}' 不存在")
            return
        
        json_data = {}
        for item in data:
            key = item.pop(key_field)
            json_data[key] = item
    else:
        print(f"不支持的格式类型: {format_type}")
        return
    
    # 写入JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"数据已成功导出到: {output_file}")
    
    # 显示数据预览
    print("\n数据预览:")
    if format_type == "list":
        preview = json_data[:2] if len(json_data) > 2 else json_data
    else:
        preview = dict(list(json_data.items())[:2]) if len(json_data) > 2 else json_data
    
    print(json.dumps(preview, ensure_ascii=False, indent=2))

def main():
    """主函数"""
    print("=== Google表格数据导出工具 ===")
    
    # 设置凭证
    client = setup_credentials()
    if not client:
        return
    
    # 获取表格数据
    data = get_sheet_data(client)
    if not data:
        return
    
    # 选择导出格式
    print("\n请选择JSON导出格式:")
    print("1. 列表对象格式 (默认)")
    print("2. 嵌套对象格式")
    format_choice = input("请输入选项 (1/2): ") or "1"
    
    format_type = "list" if format_choice == "1" else "nested"
    
    # 导出数据
    export_to_json(data, format_type)

if __name__ == "__main__":
    main() 