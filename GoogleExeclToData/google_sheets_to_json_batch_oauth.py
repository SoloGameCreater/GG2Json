#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import argparse
import pickle
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd
# 导入JSON拆分模块
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

# 定义访问Google Sheets所需的权限范围
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def setup_credentials(creds_file):
    """设置Google Sheets API凭证（使用OAuth 2.0）"""
    creds = None
    token_file = 'token.pickle'
    
    # 如果存在token文件，则加载已保存的凭证
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            try:
                creds = pickle.load(token)
            except:
                print("加载保存的凭证失败，将重新授权")
    
    # 如果没有有效凭证，则请求用户授权
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                print("刷新凭证失败，将重新授权")
                creds = None
        
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"授权过程出错: {e}")
                return None
            
            # 保存凭证以供下次使用
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
    
    try:
        # 创建Google Sheets API服务
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        print(f"创建API服务失败: {e}")
        return None

def get_sheet_data(service, spreadsheet_id, sheet_name=None):
    """获取Google表格数据"""
    try:
        # 获取表格信息
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        # 如果未指定工作表名称，则读取所有工作表
        if not sheet_name:
            all_sheets = []
            for sheet in spreadsheet['sheets']:
                all_sheets.append(sheet['properties']['title'])
            return get_all_sheets_data(service, spreadsheet_id, all_sheets)
        
        # 获取工作表范围
        range_name = f"{sheet_name}"
        
        # 获取数据
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueRenderOption='UNFORMATTED_VALUE'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('未找到数据')
            return None
        
        # 将数据转换为字典列表
        headers = values[0]
        data = []
        for row in values[1:]:
            # 确保行长度与标题行一致
            row_data = row + [''] * (len(headers) - len(row))
            data.append(dict(zip(headers, row_data)))
        
        return data
    except Exception as e:
        print(f"获取表格数据错误: {e}")
        return None

def get_all_sheets_data(service, spreadsheet_id, sheet_names):
    """获取所有工作表的数据，并按工作表名称分组"""
    all_data = {}
    
    for sheet_name in sheet_names:
        try:
            # 获取工作表范围
            range_name = f"{sheet_name}"
            
            # 获取数据
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueRenderOption='UNFORMATTED_VALUE'
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print(f'工作表 {sheet_name} 未找到数据')
                continue
            
            # 将数据转换为字典列表
            headers = values[0]
            sheet_data = []
            for row in values[1:]:
                # 确保行长度与标题行一致
                row_data = row + [''] * (len(headers) - len(row))
                # 创建包含数据的字典
                row_dict = dict(zip(headers, row_data))
                sheet_data.append(row_dict)
            
            # 将当前工作表的数据添加到总数据中，以工作表名称为键
            all_data[sheet_name] = sheet_data
            
        except Exception as e:
            print(f"获取工作表 {sheet_name} 数据错误: {e}")
    
    return all_data

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
        # 如果数据是按工作表分组的字典，则将其展平为列表
        if isinstance(data, dict):
            flat_data = []
            for sheet_name, sheet_data in data.items():
                for item in sheet_data:
                    item['sheet_name'] = sheet_name
                    flat_data.append(item)
            json_data = flat_data
        else:
            json_data = data
    elif format_type == "nested":
        # 嵌套对象格式
        if isinstance(data, dict):
            # 如果数据已经是按工作表分组的字典，需要先展平
            flat_data = []
            for sheet_name, sheet_data in data.items():
                for item in sheet_data:
                    item['sheet_name'] = sheet_name
                    flat_data.append(item)
            data = flat_data
            
        if not key_field or key_field not in data[0].keys():
            print(f"错误: 字段 '{key_field}' 不存在或未指定")
            return False
        
        json_data = {}
        for item in data:
            key = item.pop(key_field)
            json_data[key] = item
    elif format_type == "sheet_grouped":
        # 按工作表分组的格式
        if isinstance(data, dict):
            # 数据已经是按工作表分组的，直接使用
            json_data = data
        else:
            # 如果数据是列表，则按sheet_name字段分组
            json_data = {}
            for item in data:
                if 'sheet_name' not in item:
                    print("错误: 数据中缺少'sheet_name'字段")
                    return False
                
                sheet_name = item.pop('sheet_name')
                if sheet_name not in json_data:
                    json_data[sheet_name] = []
                
                json_data[sheet_name].append(item)
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
    parser.add_argument('--credentials', required=True, help='Google API OAuth 2.0凭证JSON文件路径')
    parser.add_argument('--format', choices=['list', 'nested', 'sheet_grouped'], default='list', help='JSON格式类型: list, nested或sheet_grouped')
    parser.add_argument('--key_field', help='嵌套格式的主键字段名')
    parser.add_argument('--sheet_name', help='工作表名称(默认为第一个工作表)')
    parser.add_argument('--split', action='store_true', help='是否将导出的JSON文件拆分成多个子文件')
    parser.add_argument('--no-split', action='store_true', help='不拆分JSON文件（默认会拆分）')
    parser.add_argument('--output-dir', help='拆分后的JSON文件输出目录路径，默认为输入文件的父目录的父目录下的export文件夹')
    
    args = parser.parse_args()
    
    # 检查参数
    if args.format == 'nested' and not args.key_field:
        print("错误: 嵌套格式需要指定--key_field参数")
        return 1
    
    # 设置凭证
    service = setup_credentials(args.credentials)
    if not service:
        return 1
    
    # 获取表格数据
    data = get_sheet_data(service, args.sheet_id, args.sheet_name)
    if not data:
        return 1
    
    # 导出数据
    success = export_to_json(data, args.output, args.format, args.key_field)
    if not success:
        return 1
    
    # 默认拆分JSON文件，除非明确指定--no-split
    should_split = not args.no_split
    
    # 如果明确指定了--split，则覆盖默认行为
    if args.split:
        should_split = True
    
    # 如果需要拆分JSON文件
    if should_split:
        print(f"正在拆分JSON文件: {args.output}")
        split_success = split_json_file(args.output, args.output_dir)
        if not split_success:
            print("拆分JSON文件失败")
            return 1
        print("拆分JSON文件成功")
    
    return 0

if __name__ == "__main__":
    exit(main()) 